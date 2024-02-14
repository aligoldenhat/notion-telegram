from telethon import TelegramClient
import json, os, time
from notion import get_pages, get_expire_users, user_optimizer, update_expiredate_and_check_shouldpay
import logging

file_path = os.path.join(os.path.dirname(__file__), f'info.json')
with open(file_path, 'r') as f:
    data = json.load(f)

api_id = data["telegram_api"]["api_id"]
api_hash = data["telegram_api"]["api_hash"]
cards = {"m": data["card"]["m"], "b": data["card"]["b"]}

client = TelegramClient('anon', api_id, api_hash)

def generate_massage(sub_users, price, bank):
    sub_users_info = "\n".join('  =>   '.join(sub_user) for sub_user in sub_users)
    card = cards[bank]

    massage = f"""
سلام وقت بخیر 
کانفیگ های شما به ایدی تمام شده:

{sub_users_info}

هزینه این کانفیگ ها ماهیانه {price} ناقابل
روی شماره کارت بزنید کپی میشود:
`{card}`

کانال وضعیت کانفیگ ها : @krowcystatus
"""
    return massage

def sending_massage(users, client):
    for user in users:
        logging.warning(f'sending telegram message for {user}')

        message = generate_massage(users[user][0], users[user][1], users[user][2])

        try:
            with client:
                client.loop.run_until_complete(main(user, message))
        except ValueError as Error:
            print (Error)
            pass

        time.sleep(2)

async def main(telegram, message):
    await client.send_message(telegram, message,
                              parse_mode="md")

if __name__ == "__main__":
    logging.basicConfig(filename = os.path.join(os.path.dirname(__file__), f'nt.log'),
                        filemode = 'a',
                        format = '%(asctime)s %(name)s %(levelname)s: %(message)s',
                        level = logging.INFO)
    
    expired_users = get_expire_users(get_pages())
    optimized_users = user_optimizer(expired_users)
    if optimized_users:
        logging.info(f"users for sending telegram message: \n {optimized_users}")
        sending_massage(optimized_users, client)
        update_expiredate_and_check_shouldpay(expired_users)