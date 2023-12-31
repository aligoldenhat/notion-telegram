import requests
import json, os
from datetime import datetime
import logging
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

def get_pages(num_pages=None):
    logging.info("getting pages from notion database")

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    results = data["results"]

    return results


def get_expire_users(pages):
    today = datetime.today().strftime('%Y-%m-%d')
    expired_users = []

    for page in pages:
        try:
            if page['properties']['expire_date']['date']['start'] == today:
                ID = page['properties']['ID']['rich_text'][0]['plain_text']
                telegram = page['properties']['telegram']['rich_text'][0]['plain_text']
                price = page['properties']['price']['number']
                page_id = page['id']
                expired_users.append((ID, telegram, price, 1, page_id))
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
                price += user[2]
                sub_user.append((user[0], str(user[2])))

        optimized_users[uniqe_user] = (sub_user, price)
    
    return optimized_users

def update_expiredate_and_check_shouldpay(users):
    updated_date = datetime.today()+ relativedelta(months=1, days=3)
    updated_date = updated_date.strftime('%Y-%m-%d')
    for user in users:
        url = f"https://api.notion.com/v1/pages/{user[4]}"
        updated_patch_req = {"properties": {'expire_date': {'date': {'start': updated_date}}, 'should_pay': {'checkbox': True}}}
        count_patch_request = 0
        while True:
            count_patch_request += 1
            res = requests.patch(url, json=updated_patch_req, headers=headers)
            if res.status_code == 200 or count_patch_request == 10:
                break
        logging.info(f"update '{user[0]}' expired_date and should_pay")