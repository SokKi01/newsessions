import re
import os
import asyncio
from pyrogram import Client, filters
from config import api_id, api_hash, USE_PROXY, proxies_file, passw

sessions_dir = 'sessions'
new_sessions_dir = 'new_sessions'

if not os.path.exists(new_sessions_dir):
    os.makedirs(new_sessions_dir)

def load_proxies(filename):
    with open(filename, "r") as file:
        proxies = [line.strip() for line in file.readlines() if line.strip()]
    return proxies

if USE_PROXY:
    proxies = load_proxies(proxies_file)

session_files = [f for f in os.listdir(sessions_dir) if f.endswith('.session')]
session_names = [os.path.splitext(f)[0] for f in session_files]

if USE_PROXY and len(session_names) != len(proxies):
    print(f"Количество сессий ({len(session_names)}) и прокси ({len(proxies)}) не совпадает.")
    exit()

async def process_session(session_name, proxy=None):
    if USE_PROXY:
        hostname, port, username, password = proxy.split(":")
        proxy_settings = {
            "scheme": "socks5",
            "hostname": hostname,
            "port": int(port),
            "username": username,
            "password": password
        }
    else:
        proxy_settings = None

    app = Client(os.path.join(sessions_dir, session_name), api_id=api_id, api_hash=api_hash, proxy=proxy_settings)

    action_completed = asyncio.Event()

    @app.on_message(filters.user(777000))
    async def handle_message(client, message):
        message_text = message.text
        match = re.search(r'\b\d{5}\b', message_text)
        
        if match:
            code = match.group(0)
            print(f"Получен код от пользователя 777000 в сессии {session_name}: {code}")

            with open('code.txt', 'w') as f:
                f.write(code)
        else:
            print(f"Код не найден в сообщении сессии {session_name}.")

        action_completed.set()

    async def get_phone_number(client):
        me = await client.get_me()  # Получаем информацию о текущей сессии
        phone_number = me.phone_number  # Получаем номер телефона
        if phone_number:
            
            # Создание новой сессии
            new_session_name = f"{phone_number}_pyrogram"
            new_session_path = os.path.join(new_sessions_dir, new_session_name)
            
            new_app = Client(
                new_session_path,
                api_id=api_id,
                api_hash=api_hash,
                phone_number=phone_number,
                password=passw,
                proxy=proxy_settings if USE_PROXY else None
            )
            
            await new_app.start()
            print(f"Новая сессия '{new_session_name}' успешно создана в {new_sessions_dir}")
            await new_app.stop()
        else:
            print(f"Номер телефона не найден в сессии {session_name}")

    await app.start()
    print(f"Запущена сессия: {session_name}, ожидание сообщений...")

    await get_phone_number(app)

    await action_completed.wait()

    await app.stop()

async def main():
    if USE_PROXY:
        for session_name, proxy in zip(session_names, proxies):
            print(f"Обработка сессии: {session_name} с прокси {proxy}")
            await process_session(session_name, proxy)
    else:
        for session_name in session_names:
            print(f"Обработка сессии: {session_name} без прокси")
            await process_session(session_name)

asyncio.run(main())
