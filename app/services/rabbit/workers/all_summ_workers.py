from app.services.rabbit.utils.parser import fetch_messages
from app.services.rabbit.utils.parser_init import client
from app.infrastructure.database.database import engine
from app.services.rabbit.utils.parametrs import connection_params

import joblib
import pickle
import datetime
import uuid
import pika
import asyncio
import pandas as pd

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
open_queue = 'parsing_queue'
channel.queue_declare(queue=open_queue)


def parse_post(ch, method, properties, body):
    data = pickle.loads(body)
    channel_to_parse = data['channel']
    channel_id = data['url']
    task_id = properties.headers['task_id']
    interval = properties.headers['interval']
    check = properties.headers['check']
    try:
        messages = client.loop.run_until_complete(fetch_messages(channel_to_parse, days=interval))
        df = pd.DataFrame(messages)
        df['task_id'] = task_id
        df['channel_id'] = channel_id
        df.to_sql('posts', con=engine, if_exists='append', index=False)
    except Exception as e:
        print(f"Error: {e}")


def callback(ch, method, properties, body):
    parse_post(ch, method, properties, body)


def start_consuming_ml():
    channel.basic_consume(
        queue=open_queue,
        on_message_callback=callback,
        auto_ack=False,  # Автоматическое подтверждение обработки сообщений
    )
    print("Waiting for messages. To exit, press Ctrl+C")
    channel.start_consuming()

if __name__ == "__main__":
    start_consuming_ml()
