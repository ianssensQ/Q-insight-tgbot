import pika
from app.services.rabbit.utils.parametrs import connection_params


def open_queue(conn_params=connection_params, queue_name='parsing_queue'):
    connection = pika.BlockingConnection(conn_params)

    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    return channel
