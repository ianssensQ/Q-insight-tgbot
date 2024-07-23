from app.services.rabbit.utils.parser import fetch_messages
from app.services.rabbit.utils.parser_init import client
from app.infrastructure.database.database import engine
from app.services.rabbit.utils.parametrs import connection_params
from app.services.rabbit.utils.classification import classify_text
from app.services.rabbit.utils.gpt_posts_summ import gpt
from app.services.rabbit.utils.gpt_channels_redaction import gpt_redaction
from app.services.crud.posts import Post
from app.services.crud.channels import Channel

import pickle
import pika
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
    print(data, f"task_id: {properties.headers['task_id']} parsing")
    channel_id = data['channel_id']
    channel_to_parse = data['url']
    task_id = properties.headers['task_id']
    interval = properties.headers['interval']
    try:
        messages = client.loop.run_until_complete(fetch_messages(channel_to_parse, days=interval))
        df = pd.DataFrame(messages)

        def is_blank(x):
            return isinstance(x, str) and x.strip() == ''
        if messages:
            data_cleaned = df[~df['post_text'].apply(is_blank) & df['post_text'].notna()]
            data_cleaned.loc[:, 'task_id'] = task_id
            data_cleaned.loc[:, 'channel_id'] = channel_id
            data_cleaned.to_sql('posts', con=engine, if_exists='append', index=False)
        else:
            print("No messages in this interval")
    except Exception as e:
        print(f"Error 1: {e}")


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

# ---------------------


def classification_post(ch, method, properties, body):
    data = pickle.loads(body)
    print(data, f"task_id: {properties.headers['task_id']} classification")
    channel_id = data['channel_id']
    task_id = properties.headers['task_id']
    try:
        posts_ids = Post.get_ids(task_id, channel_id)
        for ids in posts_ids:
            post = Post(post_id=ids[0])
            if not post.check_res_class():
                post.save_post_result_class(int(classify_text(post.get_text_from_post()[0])))
    except Exception as e:
        print(f"Error 2: {e}")


def make_callback_classification(ch, method, properties, body):
    queue_name = properties.headers['queues'][1]
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


# ---------------------


def summ_post(ch, method, properties, body):
    data = pickle.loads(body)
    print(data, f"task_id: {properties.headers['task_id']} summ post")
    channel_id = data['channel_id']
    task_id = properties.headers['task_id']
    try:
        posts_ids = Post.filter_posts(task_id, channel_id)
        for ids in posts_ids:
            post = Post(post_id=ids[0])
            if not post.check_res_summ():
                post.save_post_result_summ(gpt(post.get_text_from_post()[0]))
    except Exception as e:
        print(f"Error 3: {e}")


def make_callback_summ_post(ch, method, properties, body):
    queue_name = properties.headers['queues'][2]
    channel.basic_publish(exchange="",
                          routing_key=queue_name,
                          properties=pika.BasicProperties(headers=properties.headers),
                          body=body)
    ch.basic_ack(
        delivery_tag=method.delivery_tag
    )
    print("Posts Summary Done")


def callback_summ_post(ch, method, properties, body):
    summ_post(ch, method, properties, body)
    make_callback_summ_post(ch, method, properties, body)


def start_consuming_summ_post():
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.basic_consume(
        queue=summ_posts_queue,
        on_message_callback=callback_summ_post,
        auto_ack=False,
    )
    print("Third queue consuming \n")
    channel.start_consuming()

# ---------------------


def summ_channel(ch, method, properties, body):
    data = pickle.loads(body)
    print(data, f"task_id: {properties.headers['task_id']} summ channel")
    channel_id = data['channel_id']
    task_id = properties.headers['task_id']
    try:
        posts_ids = Post.filter_posts(task_id, channel_id)
        texts = []
        for ids in posts_ids:
            post = Post(post_id=ids[0])
            if post.check_res_summ():
                texts.append(post.load_post_result_summ()[0])
        channel = Channel(channel_id=channel_id)
        if not channel.check_res():
            channel.save_channel_result(gpt_redaction(texts))
    except Exception as e:
        print(f"Error 4: {e}")


def make_callback_summ_channel(ch, method, properties, body):
    queue_name = properties.headers['queues'][3]
    channel.basic_publish(exchange="",
                          routing_key=queue_name,
                          properties=pika.BasicProperties(headers=properties.headers),
                          body=body)
    ch.basic_ack(
        delivery_tag=method.delivery_tag
    )
    print("Channel Summary Done")


def callback_summ_channel(ch, method, properties, body):
    summ_channel(ch, method, properties, body)
    make_callback_summ_channel(ch, method, properties, body)


def start_consuming_summ_channel():
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.basic_consume(
        queue=summ_channels_queue,
        on_message_callback=callback_summ_channel,
        auto_ack=False,
    )
    print("Fourth queue consuming \n")
    channel.start_consuming()


if __name__ == '__main__':

    parser_thread = threading.Thread(target=start_consuming_parser)
    classification_thread = threading.Thread(target=start_consuming_classification)
    summ_posts_thread = threading.Thread(target=start_consuming_summ_post)
    summ_channel_thread = threading.Thread(target=start_consuming_summ_channel)

    parser_thread.start()
    classification_thread.start()
    summ_posts_thread.start()
    summ_channel_thread.start()

    parser_thread.join()
    classification_thread.join()
    summ_posts_thread.join()
    summ_channel_thread.join()
