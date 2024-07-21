import pika
from decouple import config

user = config("RABBITMQ_DEFAULT_USER")
password = config("RABBITMQ_DEFAULT_PASS")

connection_params = pika.ConnectionParameters(
    host="localhost",
    port=5672,
    virtual_host="/",
    credentials=pika.PlainCredentials(
        username=user,
        password=password,
    ),
    heartbeat=30,
    blocked_connection_timeout=2,
)

"""
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
queue_name = "prediction_queue"
channel.queue_declare(queue=queue_name)
"""
