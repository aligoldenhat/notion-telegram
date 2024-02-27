import requests
import json, os
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

file_path = os.path.join(os.path.dirname(__file__), f'info.json')
with open(file_path, 'r') as f:
    data = json.load(f)

NOTION_TOKEN = data["notion_api"]["notion_token"]
DATABASE_ID = data["notion_api"]["database_id"]

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json"
}

def get_pages(date):
    logging.info("getting pages from notion database")

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    payload = {"filter": {
                "property": "expire_date", 
                "date": {
                    "equals": date
                  }
                }
              }
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    results = data["results"]

    return results


def extract_important_column(pages):
    expired_users = []

    for page in pages:
        try:
            ID = page['properties']['ID']['title'][0]['plain_text']
            telegram = page['properties']['telegram']['rich_text'][0]['plain_text']
            price = page['properties']['price']['number']
            page_id = page['id']
            bank = page['properties']['bank']['select']['name'][0]
            expired_users.append((ID, telegram, price, page_id, bank))
        except TypeError:
            pass
    return expired_users


def user_optimizer(users):
    optimized_users = {}
    uniqe_users = set(user[1] for user in users)

    for uniqe_user in uniqe_users:
        price = 0
        sub_user = []

        for user in users:
            if uniqe_user == user[1]:
                card = user[4]
                price += user[2]
                sub_user.append((user[0], str(user[2])))

        optimized_users[uniqe_user] = (sub_user, price, card)
    
    return optimized_users  

def update_expiredate_and_check_shouldpay(users):
    updated_date = datetime.today()+ relativedelta(months=1)
    updated_date = updated_date.strftime('%Y-%m-%d')
    for user in users:
        url = f"https://api.notion.com/v1/pages/{user[3]}"
        updated_patch_req = {"properties": {'expire_date': {'date': {'start': updated_date}}, 'should_pay': {'checkbox': True}}}
        count_patch_request = 0
        while True:
            count_patch_request += 1
            res = requests.patch(url, json=updated_patch_req, headers=headers)
            if res.status_code == 200 or count_patch_request == 10:
                break
        logging.info(f"update '{user[0]}' expired_date and should_pay")
