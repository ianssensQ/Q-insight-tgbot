from telethon import TelegramClient
import nest_asyncio
import asyncio
from decouple import config

nest_asyncio.apply()

api_id = config('API_ID')
api_hash = config('API_HASH')
phone_number = config('PHONE_NUMBER')

client = TelegramClient(phone_number, api_id, api_hash)


async def start():
    await client.start()
    print(await client.get_me())

if __name__ == '__main__':
    asyncio.run(start())
