import pandas as pd
from app.services.rabbit.utils.parser import fetch_messages
from app.services.rabbit.utils.parser_init import client
from app.infrastructure.database.database import engine

# channel = 'https://t.me/econs'
channel = 'https://t.me/datafeeling'
messages = client.loop.run_until_complete(fetch_messages(channel, days=30))
task_id = 1
channel_id = 1


if __name__ == "__main__":
    df = pd.DataFrame(messages)
    df['task_id'] = task_id
    df['channel_id'] = channel_id
    print(df)
    # df.to_sql('posts', con=engine, if_exists='append', index=False)
