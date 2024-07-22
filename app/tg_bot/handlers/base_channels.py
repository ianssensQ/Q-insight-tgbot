from aiogram import F, Router, Bot
from decouple import config
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, Chat

from app.tg_bot.states.summ import Summ
from app.tg_bot.states.base import Base
from app.services.crud.users import User
from app.tg_bot.keyboards.inline import list_and_base_edit, channel_list_urls, make_inline_keyboard
from app.services.rabbit.utils.parser_init import client
from app.tg_bot.handlers.common import cmd_help
router = Router()
bot = Bot(token=config('BOT_TOKEN'))


async def del_mess(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception as e:
        pass

@router.callback_query(StateFilter(Summ.no_base), F.data == "no_base")
async def no_base_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await del_mess(callback)
    await callback.message.answer(
        text="Перенаправляем в меню базовых каналов.🔜"
             "У вас нет отслеживаемых каналов.",
        reply_markup=make_inline_keyboard([("▪️Добавить отслеживаемый канал", "first_add")])
    )
    await state.set_state(Base.add)


@router.message(Command(commands=["base_channels"]))
async def base_channels(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    await state.update_data(tg_id=user_id)
    user = User(tg_id=user_id)
    channel_list = user.get_tg_trackable_channels()[0]

    if not channel_list:
        await message.answer(
            text="У вас нет отслеживаемых каналов.",
            reply_markup=make_inline_keyboard([("▪️Добавить отслеживаемый канал", "first_add")])
        )

        await state.set_state(Base.add)
    else:
        await state.set_state(Base.base_menu)
        await base_menu_func(message, state)


@router.callback_query(StateFilter(Base.edit), F.data == "add")
async def add_channel_callback(callback: CallbackQuery, state: FSMContext):
    await del_mess(callback)
    await callback.message.answer(
        text=" Чтобы добавить канал, вставьте ссылку на него в поле ввода. \n\n"
             "▫️Для упрощения поиска можете воспользоваться поиском при помощи @SearcheeBot. \n"
             "▫️Введите @SearcheeBot \t <Название канала>. \n"
             "▫️Выберите нужный канал из списка, и скопируйте ссылку из кнопки ниже (Перейти в канал). \n"
             "▫️Вставьте ее в поле ввода. \n",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Base.catch_channel)


@router.callback_query(StateFilter(Base.add), F.data == "first_add")
@router.callback_query(StateFilter(Base.add))
async def add_channel_message(callback: CallbackQuery, state: FSMContext):
    await del_mess(callback)
    await callback.message.answer(
        text=" Чтобы добавить канал, вставьте ссылку на него в поле ввода. \n\n"
             "▫️Для упрощения поиска можете воспользоваться поиском при помощи @SearcheeBot. \n"
             "▫️Введите @SearcheeBot \t <Название канала>. \n"
             "▫️Выберите нужный канал из списка, и скопируйте ссылку из кнопки ниже (Перейти в канал). \n"
             "▫️Вставьте ее в поле ввода. \n",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Base.catch_channel)


@router.message(StateFilter(Base.catch_channel), F.text.startswith("http://t.me/joinchat"))
@router.message(StateFilter(Base.catch_channel), F.text.startswith("https://t.me/joinchat"))
async def catch_privat_channels(message: Message, state: FSMContext):
    try:
        await message.delete()
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
        # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-2)
    except Exception as e:
        pass
    await message.answer(
        text="🟥 Канал приватный 🔚",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Base.base_menu)
    await base_menu_func(message, state)

@router.message(StateFilter(Base.catch_channel), F.text.startswith("http://t.me/"))
@router.message(StateFilter(Base.catch_channel), F.text.startswith("https://t.me/"))
async def catch_channels(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(tg_id=user_id)
    user = User(tg_id=user_id)
    """
    await message.answer(
        text=f"{message.from_user.is_bot}"
    )
    """
    try:
        await message.delete()
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
        # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-2)
    except Exception as e:
        pass

    if user.add_channels([message.text]):
        await message.answer(
            text="🟥 Канал уже добавлен!",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text="☑️ Канал успешно добавлен!",
            reply_markup=ReplyKeyboardRemove()
        )
    await state.set_state(Base.base_menu)
    await base_menu_func(message, state)


@router.callback_query(StateFilter(Base.edit), F.data == "delete")
async def delete_channel_callback(callback: CallbackQuery, state: FSMContext):
    await del_mess(callback)
    user_data = await state.get_data()
    user_id = user_data['tg_id']
    user = User(tg_id=user_id)
    channel_list = user.get_tg_trackable_channels()[0]

    channels = []
    for channel in channel_list:
        async with client:
            channel_entity = await client.get_entity(channel)
            channels.append(channel_entity)

    res_ch = list(zip(channels, channel_list))
    keyboard, ch_names = channel_list_urls(res_ch)

    await callback.message.answer(
        text=" Чтобы удалить канал, выберете его из списка: \n",
        reply_markup=keyboard
    )
    await state.set_state(Base.delete)


@router.callback_query(StateFilter(Base.delete))
async def delete_channel(callback: CallbackQuery, state: FSMContext):
    await del_mess(callback)
    channel_link = callback.data
    user_data = await state.get_data()
    user_id = user_data['tg_id']
    user = User(tg_id=user_id)
    user.remove_channels([channel_link])
    await callback.message.answer(
        text="☑️ Канал успешно удален!",
        reply_markup=ReplyKeyboardRemove()
    )
    if user.get_tg_trackable_channels()[0]:
        await state.set_state(Base.base_menu)
        await base_menu_func(callback.message, state)
    else:
        await cmd_help(callback.message, state)


@router.callback_query(StateFilter(Base.edit), F.data == "reset")
async def reset_channels_callback(callback: CallbackQuery, state: FSMContext):
    await del_mess(callback)
    user_data = await state.get_data()
    user_id = user_data['tg_id']
    user = User(tg_id=user_id)
    user.delete_channels()
    await callback.message.answer(
        text="☑️ Все каналы были удалены \n",
        reply_markup=ReplyKeyboardRemove()
    )
    await cmd_help(callback.message, state)


@router.message(StateFilter(Base.base_menu))
async def base_menu_func(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data['tg_id']
    user = User(tg_id=user_id)

    channels = []
    channels_link = []
    async def get_channel_entity(channel):
        async with client:
            return await client.get_entity(channel)


    for channel in user.get_tg_trackable_channels():
        channel_entity = await get_channel_entity(channel)

        for i in range(len(channel)):
            channels_link.append(channel[i])

    channels = list(zip(channels_link, channel_entity))
    keyboard = list_and_base_edit(channels)

    await message.answer(
        text=f"Вот список отслеживаемых каналов: ",
        reply_markup=keyboard
    )
    await state.set_state(Base.edit)
