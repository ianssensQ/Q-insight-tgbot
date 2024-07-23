from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from app.services.rabbit.utils.parametrs import connection_params
from app.tg_bot.states.summ import Summ
from app.services.crud.channels import Channel


import pickle
import uuid
import pika
import asyncio

router = Router()


@router.callback_query(StateFilter(Summ.Redirect))
async def predict_redirect(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=" Перехватил задачу ✔️ \n"
             "Суммирую 🤖 \n"
             "Это может занять несколько минут ⏳ ",
    )

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
    await state.set_state(Summ.Predict)
    await callback.message.answer('Просуммировал 👀😤')
    await predict_return(callback.message, state)


@router.message(StateFilter(Summ.Predict))
async def predict_return(message: Message, state: FSMContext):
    user_data = await state.get_data()
    channel_ids = user_data['channel_info']

    for channel_id in channel_ids:
        channel = Channel(channel_id=channel_id)
        result = channel.load_channel_result()[0]
        result = await escape_markdown_v1(result)
        if len(result) > 4090:
            results = await split_text(result, 4090)
            await message.answer(
                text=f'**Результаты суммирования по каналу {channel_id}**:\n',
                parse_mode=ParseMode.MARKDOWN_V2
            )
            for result in results:
                await message.answer(
                    text=result,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
        else:
            if result == 'No data':
                await message.answer(
                    text=f'Нет данных по данному каналу {channel_id} за этот промежуток времени. \n',
                )
            else:
                await message.answer(
                    text=f'**Результаты суммирования по каналу {channel_id}**:\n',
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                await message.answer(
                    text=result,
                    parse_mode=ParseMode.MARKDOWN_V2
                )


async def escape_markdown_v1(text):
    """
    Функция для экранирования специальных символов в тексте для Markdown v2 в Telegram.
    """
    text = text.replace('#', '')
    special_chars = ['\\', '=', '`', '_', '{', '}', '[', ']', '(', ')', '>', '#', '+', '-', '.', '!', '|']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


async def split_text(text: str, length: int) -> list:
    """
    Функция для разбития текста на части, не превышающие заданную длину телеграма
    """
    return [text[i:i + length] for i in range(0, len(text), length)]


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
