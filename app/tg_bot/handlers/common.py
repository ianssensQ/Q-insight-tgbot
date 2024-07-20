from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Здравствуйте!\n"
             "Я готов помочь вам с аггрегацией информации. \n"
             "Вот список доступных команд:\n"
             "• /summaries:  Суммаризация по каналам\n"
             "• /base_channels:  Вывести/изменить список отслеживаемых каналов\n"
             "• /help:  Вывести список команд \n"
             "• /cancel:  Отменить действие \n"
             "• /about:  Информация о проекте",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["help"]))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Возвращаемся в меню \n"
             "Вот список доступных команд:\n"
             "• /summaries:  Суммаризация по каналам\n"
             "• /base_channels:  Вывести/изменить список отслеживаемых каналов\n"
             "• /help:  Вывести список команд \n"
             "• /cancel:  Отменить действие \n"
             "• /about:  Информация о проекте"
        ,
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["about"]))
async def cmd_cancel(message: Message):
    await message.answer(
        text="Возвращаемся в меню \n"
             "Вот список доступных команд:\n"
             "• /summaries:  Суммаризация по каналам\n"
             "• /base_channels:  Вывести/изменить список отслеживаемых каналов\n"
             "• /help:  Вывести список команд \n"
             "• /cancel:  Отменить действие \n"
             "• /about:  Информация о проекте"
        ,
        reply_markup=ReplyKeyboardRemove()
    )