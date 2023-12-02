from telethon import TelegramClient
import json, os, time
from notion import get_pages, get_expire_users, user_optimizer

file_path = os.path.join(os.path.dirname(__file__), f'info.json')
with open(file_path, 'r') as f:
    data = json.load(f)

api_id = data["telegram_api"]["api_id"]
api_hash = data["telegram_api"]["api_hash"]

client = TelegramClient('anon', api_id, api_hash)

def generate_massage(sub_users, price):
    massage = f"""
سلام وقت بخیر 
کانفیگ های شما به ایدی تمام شده:
{"\n".join(sub_user for sub_user in sub_users)}

هزینه این کانفیگ ها ماهیانه {price} ناقابل
"""
    return massage

def sending_massage(users, client):
    for user in users:
        message = generate_massage(users[user][0], users[user][1])

        with client:
            client.loop.run_until_complete(main(user, message))
        
        time.sleep(2)

async def main(telegram, message):
    await client.send_message(telegram, message)

sending_massage(user_optimizer(get_expire_users(get_pages())), client)