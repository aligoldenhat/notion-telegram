from telethon import TelegramClient
import json, os, time
from notion import get_pages, get_expire_users, user_optimizer
import logging

file_path = os.path.join(os.path.dirname(__file__), f'info.json')
with open(file_path, 'r') as f:
    data = json.load(f)

api_id = data["telegram_api"]["api_id"]
api_hash = data["telegram_api"]["api_hash"]

client = TelegramClient('anon', api_id, api_hash)

def generate_massage(sub_users, price):
    sub_users_info = "\n".join('  =>   '.join(sub_user) for sub_user in sub_users)
    massage = f"""
سلام وقت بخیر 
کانفیگ های شما به ایدی تمام شده:

{sub_users_info}

هزینه این کانفیگ ها ماهیانه {price} ناقابل

کانال وضعیت کانفیگ ها : @krowcystatus
"""
    return massage

def sending_massage(users, client):
    for user in users:
        logging.warning(f'sending telegram message for {user}')

        message = generate_massage(users[user][0], users[user][1])

        try:
            with client:
                client.loop.run_until_complete(main(user, message))
        except ValueError as Error:
            print (Error)
            pass

        time.sleep(2)

async def main(telegram, message):
    await client.send_message(telegram, message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    optimized_users = user_optimizer(get_expire_users(get_pages()))
    logging.info(f"users for sending telegram message: \n {optimized_users}")
    
    sending_massage(optimized_users, client)