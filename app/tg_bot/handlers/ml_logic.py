from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from app.services.rabbit.utils.parametrs import connection_params
from app.tg_bot.states.summ import Summ

import joblib
import pickle
import datetime
import uuid
import pika
import asyncio

router = Router()


@router.callback_query(StateFilter(Summ.Redirect))
async def predict_redirect(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    task_list = user_data['task_list']
    task_id = user_data['task_id']
    channel_ids = user_data['channel_info']
    interval = user_data['interval']

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
    check = str(uuid.uuid4())

    queues = [classification_queue,
              summ_posts_queue,
              summ_channels_queue,
              close_queue]

    channels_urls_ids = list(zip(channel_ids, task_list))

    await asyncio.gather(*[send_channel_to_queue(channel,
                                                 open_queue,
                                                 pickle.dumps({"channel_id": task[0], "url": task[1]}),
                                                 task_id,
                                                 interval,
                                                 check,
                                                 queues)
                           for task in channels_urls_ids])

    def close_callback(ch, method, properties, body):
        message = properties.headers['check']
        if message == check:
            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )
            print("Closing Done")
            connection.close()

    channel.basic_consume(
        queue=close_queue,
        on_message_callback=close_callback,
        auto_ack=False,
    )
    channel.start_consuming()

    await callback.message.answer(
        text="Перехватил ✔️"
        "Суммируем 🤖 ",
    )


async def send_channel_to_queue(channel,
                                queue,
                                url,
                                task_id,
                                interval,
                                check,
                                queues):
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=url,
        properties=pika.BasicProperties(
            headers={'task_id': task_id,
                     'interval': interval,
                     'check': check,
                     'queues': queues
                     }
        )
    )
