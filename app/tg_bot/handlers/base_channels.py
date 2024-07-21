from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, Chat

from app.tg_bot.states.summ import Summ
from app.tg_bot.states.base import Base
from app.services.crud.users import User
from app.tg_bot.keyboards.inline import list_and_base_edit, channel_list_view, channel_list_urls
from app.tg_bot.keyboards.summ_main import make_row_keyboard
from app.services.rabbit.utils.parser_init import client

router = Router()


@router.message(Command(commands=["base_channels"]))
@router.message(StateFilter(Summ.no_base), F.text.in_(["Добавить отслеживаемые каналы"]))
async def base_channels(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    await state.update_data(tg_id=user_id)
    user = User(tg_id=user_id)
    channel_list = user.get_tg_trackable_channels()[0]

    if not channel_list:
        await message.answer(
            text="У вас нет отслеживаемых каналов.",
            reply_markup=make_row_keyboard(["Добавить отслеживаемый канал"])
        )
        await state.set_state(Base.add)
    else:
        await state.set_state(Base.base_menu)
        await base_menu_func(message, state)





@router.callback_query(StateFilter(Base.edit), F.data == "add")
async def add_channel_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=" Чтобы добавить канал, вставьте ссылку на него в поле ввода. \n\n"
             "▪️Для упрощения поиска можете воспользоваться поиском при помощи @SearcheeBot. \n"
             "▪️Введите @SearcheeBot \t <Название канала>. \n"
             "▪️Выберите нужный канал из списка, и скопируйте ссылку из кнопки ниже (Перейти в канал). \n"
             "▪️Вставьте ее в поле ввода. \n",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Base.catch_channel)


@router.message(StateFilter(Base.add), F.text.in_(["Добавить отслеживаемый канал"]))
async def add_channel_message(message: Message, state: FSMContext):
    await message.answer(
        text=" Чтобы добавить канал, вставьте ссылку на него в поле ввода. \n\n"
             "▪️Для упрощения поиска можете воспользоваться поиском при помощи @SearcheeBot. \n"
             "▪️Введите @SearcheeBot \t <Название канала>. \n"
             "▪️Выберите нужный канал из списка, и скопируйте ссылку из кнопки ниже (Перейти в канал). \n"
             "▪️Вставьте ее в поле ввода. \n",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Base.catch_channel)


@router.message(StateFilter(Base.catch_channel), F.text.startswith("http://t.me/joinchat"))
@router.message(StateFilter(Base.catch_channel), F.text.startswith("https://t.me/joinchat"))
async def catch_privat_channels(message: Message, state: FSMContext):
    await message.answer(
        text="Канал приватный,",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(StateFilter(Base.catch_channel), F.text.startswith("http://t.me/"))
@router.message(StateFilter(Base.catch_channel), F.text.startswith("https://t.me/"))
async def catch_channels(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data['tg_id']
    user = User(tg_id=user_id)
    if user.add_channels([message.text]):
        await message.answer(
            text="Канал уже добавлен!",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Base.base_menu)
        await base_menu_func(message, state)
    else:
        await message.answer(
            text="Канал успешно добавлен!",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Base.base_menu)
        await base_menu_func(message, state)


@router.callback_query(StateFilter(Base.edit), F.data == "delete")
async def delete_channel_callback(callback: CallbackQuery, state: FSMContext):
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
    channel_link = callback.data
    user_data = await state.get_data()
    user_id = user_data['tg_id']
    user = User(tg_id=user_id)
    user.remove_channels([channel_link])
    await callback.message.answer(
        text="Канал успешно удален!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Base.base_menu)
    await base_menu_func(callback.message, state)


@router.callback_query(StateFilter(Base.edit), F.data == "reset")
async def reset_channels_callback(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data['tg_id']
    user = User(tg_id=user_id)
    user.delete_channels()
    await callback.message.answer(
        text="Все каналы были удалены \n",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Base.base_menu)
    await base_menu_func(callback.message, state)

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