from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from app.services.rabbit.utils.open_summ_queue import open_queue
from app.tg_bot.keyboards.summ_main import make_row_keyboard
from app.tg_bot.keyboards.inline import channel_list_urls, add_buttons_to_keyboard, date_keyboard
from app.tg_bot.states.summ import Summ
from app.services.crud.users import User
from app.services.crud.tasks import Task
from app.services.rabbit.utils.parser_init import client
from app.tg_bot.bot import bot

router = Router()


@router.message(Command(commands=["summarize"]))
async def summ_catch(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="По каким каналам хотите получить суммаризацию?",
        reply_markup=make_row_keyboard(["Выбрать каналы самостоятельно", "По отслеживаемым каналам"])
    )
    await state.update_data(tg_id=message.from_user.id)
    await state.set_state(Summ.choosing_what_base_summ)


@router.message(StateFilter(Summ.choosing_what_base_summ), F.text.in_(["По отслеживаемым каналам"]))
async def summ_base(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data['tg_id']
    user = User(tg_id=user_id)
    channel_list = user.get_tg_trackable_channels()[0]
    await state.update_data(channel_list=channel_list)
    if not channel_list:
        await message.answer(
            text="У вас нет отслеживаемых каналов",
            reply_markup=make_row_keyboard(["Выбрать каналы самостоятельно",
                                            "Добавить отслеживаемые каналы"])
        )
        await state.set_state(Summ.no_base)

    else:
        task_list = []
        await state.update_data(task_list=task_list)
        await state.set_state(Summ.choosing_what_summ)
        await summ_base_func(message, state)


@router.message(StateFilter(Summ.choosing_what_summ))
async def summ_base_func(message: Message, state: FSMContext):
    await message.answer(
        text="📕📕📕📕📕",
        reply_markup=ReplyKeyboardRemove())
    await summ_base_func_2(message, state)


@router.message(StateFilter(Summ.choosing_what_summ))
async def summ_base_func_2(message: Message, state: FSMContext):
    user_data = await state.get_data()
    channel_list = user_data['channel_list']
    await state.update_data(chat_id=message.chat.id)
    channels = []
    for channel in channel_list:
        async with client:
            channel_entity = await client.get_entity(channel)
            channels.append(channel_entity)

    res_ch = list(zip(channels, channel_list))
    keyboard, ch_names = channel_list_urls(res_ch)

    new_buttons = [("▪️Выбор промежутка времени", "date"),
                   ("▪️Выбрать все и перейти к выбору времени", "date_all")]
    keyboard = add_buttons_to_keyboard(keyboard, new_buttons)

    await bot.send_message(
        chat_id=message.chat.id,
        text="По каким каналам хотите получить суммаризацию? \n"
             "Выберите нужные каналы, после чего выбирайте нужный промежуток времени:",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

    await state.set_state(Summ.choosing)


@router.callback_query(StateFilter(Summ.choosing), F.data != "date", F.data != "date_all")
async def choose_channels(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    channel_link = callback.data
    task_list = user_data['task_list']
    task_list.append(channel_link)
    channel_list = user_data['channel_list']
    chat_id = user_data['chat_id']
    if channel_link in channel_list:
        channel_list.remove(channel_link)
    if not channel_list:
        formatted_string = '\n 🔘'.join(f'{item}' for item in task_list)
        formatted_string = '🔘' + formatted_string
        await bot.send_message(
            chat_id=chat_id,
            text=f"Добавленны все каналы для суммаризации:\n {formatted_string}",
            reply_markup=ReplyKeyboardRemove(),
            disable_web_page_preview=True
        )
        await state.set_state(Summ.choosing_date)
        await choose_date(callback, state)
    else:
        channels = []
        for channel in channel_list:
            async with client:
                channel_entity = await client.get_entity(channel)
                channels.append(channel_entity)
        res_ch = list(zip(channels, channel_list))
        keyboard, ch_names = channel_list_urls(res_ch)

        new_buttons = [("▪️Выбор промежутка времени", "date"),
                       ("▪️Выбрать все и перейти к выбору времени", "date_all")]
        keyboard = add_buttons_to_keyboard(keyboard, new_buttons)

        formatted_string = '\n 🔘'.join(f'{item}' for item in task_list)
        formatted_string = '🔘' + formatted_string
        await state.update_data(task_list=task_list)
        await callback.message.delete()
        await bot.send_message(
            chat_id=chat_id,
            text=f"Добавленные каналы:\n {formatted_string}"
                 "\n Выберете нужные каналы, после чего выбирайте нужный промежуток времени:",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        await state.set_state(Summ.choosing)


@router.callback_query(StateFilter(Summ.choosing), F.data != "date", F.data == "date_all")
async def choose_all_channels(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    channel_list = user_data['channel_list']
    chat_id = user_data['chat_id']
    task_list = channel_list
    await state.update_data(task_list=task_list)
    formatted_string = '\n 🔘'.join(f'{item}' for item in task_list)
    formatted_string = '🔘' + formatted_string
    await bot.send_message(
        chat_id=chat_id,
        text=f"Добавленны все каналы для суммаризации:\n {formatted_string}",
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True
    )
    await state.set_state(Summ.choosing_date)
    await choose_date(callback, state)


@router.callback_query(StateFilter(Summ.choosing), F.data == "date", F.data != "date_all")
@router.callback_query(StateFilter(Summ.choosing_date))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    keyboard = date_keyboard()
    await callback.message.answer(
        text="Выберите нужный промежуток времени:",
        reply_markup=keyboard
    )

    await state.set_state(Summ.generate_task)


@router.callback_query(StateFilter(Summ.generate_task))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    interval = int(callback.data)
    user_data = await state.get_data()
    task_list = user_data['task_list']
    user_id = user_data['tg_id']
    task = Task(user_id=user_id, tg_tasked_channels=task_list, interval=interval)
    task.create_task()


@router.message(StateFilter(Summ.choosing_what_base_summ), F.text.in_(["Выбрать каналы самостоятельно"]))
@router.message(StateFilter(Summ.no_base), F.text.in_(["Выбрать каналы самостоятельно"]))
async def choose_channels(message: Message, state: FSMContext):
    await message.answer(
        text="По каким каналам хотите получить суммаризацию? \n"
             "▪️Выберете нужные каналы: скопируйте и вставьте ссылку на канал в поле ниже. \n"
             "▪️Для упрощения поиска можете воспользоваться поиском при помощи @SearcheeBot. \n"
             "▪️Введите @SearcheeBot <Название канала>. \n"
             "▪️Выберите нужный канал из списка, и скопируйте ссылку из кнопки ниже. \n"
             "▪️Вставьте ее в поле ввода. \n"
             "▪️После чего выбирайте нужный промежуток времени.",
        reply_markup=ReplyKeyboardRemove()
    )

    # channel = open_queue()
    # new_buttons = [("Приступим к суммаризации", "summ")]
