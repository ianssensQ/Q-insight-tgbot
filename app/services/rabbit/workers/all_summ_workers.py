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
import threading

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

open_queue = 'parsing_queue'
classification_queue = "classification_queue"
summ_posts_queue = "summ_posts_queue"
summ_channels_queue = "summ_channels_queue"
close_queue = "predictions_callback"

channel.queue_declare(queue=open_queue)
channel.queue_declare(queue=classification_queue)
channel.queue_declare(queue=summ_posts_queue)
channel.queue_declare(queue=summ_channels_queue)
channel.queue_declare(queue=close_queue)


def parser_post(ch, method, properties, body):
    data = pickle.loads(body)
    print(data,  properties.headers['task_id'])
    channel_id = data['channel_id']
    channel_to_parse = data['url']
    task_id = properties.headers['task_id']
    interval = properties.headers['interval']
    try:
        messages = client.loop.run_until_complete(fetch_messages(channel_to_parse, days=interval))
        df = pd.DataFrame(messages)
        df.dropna(subset='post_text')

        def is_blank(x):
            return isinstance(x, str) and x.strip() == ''

        data_cleaned = df[~df['post_text'].apply(is_blank)]
        data_cleaned.loc[:, 'task_id'] = task_id
        data_cleaned.loc[:, 'channel_id'] = channel_id
        data_cleaned.to_sql('posts', con=engine, if_exists='append', index=False)
    except Exception as e:
        print(f"Error: {e}")


def make_callback_parser(ch, method, properties, body):
    queue_name = properties.headers['queues'][0]
    channel.basic_publish(exchange="",
                          routing_key=queue_name,
                          properties=pika.BasicProperties(headers=properties.headers),
                          body=body)
    ch.basic_ack(
        delivery_tag=method.delivery_tag
    )
    print("Parsing Done")


def callback_parser(ch, method, properties, body):
    parser_post(ch, method, properties, body)
    make_callback_parser(ch, method, properties, body)


def start_consuming_parser():
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.basic_consume(
        queue=open_queue,
        on_message_callback=callback_parser,
        auto_ack=False,
    )
    print("First queue consuming")
    channel.start_consuming()


def classification_post(ch, method, properties, body):
    pass


def make_callback_classification(ch, method, properties, body):
    queue_name = properties.headers['queues'][3]
    channel.basic_publish(exchange="",
                          routing_key=queue_name,
                          properties=pika.BasicProperties(headers=properties.headers),
                          body=body)
    ch.basic_ack(
        delivery_tag=method.delivery_tag
    )
    print("Classification Done")


def callback_classification(ch, method, properties, body):
    classification_post(ch, method, properties, body)
    make_callback_classification(ch, method, properties, body)


def start_consuming_classification():
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.basic_consume(
        queue=classification_queue,
        on_message_callback=callback_classification,
        auto_ack=False,
    )
    print("Second queue consuming \n")
    channel.start_consuming()


if __name__ == '__main__':
    parser_thread = threading.Thread(target=start_consuming_parser)
    classification_thread = threading.Thread(target=start_consuming_classification)

    parser_thread.start()
    classification_thread.start()

    parser_thread.join()
    classification_thread.join()
