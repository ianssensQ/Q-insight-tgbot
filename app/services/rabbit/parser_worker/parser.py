import pandas as pd
from app.services.rabbit.parser_worker.parser_init import client
from app.infrastructure.database.database import engine


async def fetch_messages(channel_username, limit=5):
    async with client:
        channel = await client.get_entity(channel_username)
        messages = []
        async for message in client.iter_messages(channel, limit=limit):
            message_data = {
                'post_date': message.date,
                'post_text': message.text,
                'post_url': f'{channel_username}/{message.id}'
            }
            messages.append(message_data)
        return messages

channel = 'https://t.me/econs'
messages = client.loop.run_until_complete(fetch_messages(channel))

task_id = 1
channel_id = 1

if __name__ == "__main__":
    df = pd.DataFrame(messages)
    df['task_id'] = task_id
    df['channel_id'] = channel_id

    df.to_sql('posts', con=engine, if_exists='append', index=False)





