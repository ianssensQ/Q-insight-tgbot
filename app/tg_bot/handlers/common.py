from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove
from app.services.crud.users import User

router = Router()


@router.message(Command(commands=["start"]))
@router.message(F.text.in_(["Начать", "Начало",
                            "начать", "начало",
                            "Start", "start"]))
async def cmd_start(message: Message, state: FSMContext):
    user = User(tg_id=message.from_user.id)
    if not user.check_user():
        user.create_user()
    await state.clear()
    await message.answer(
        text="Здравствуйте!\n"
             "Я готов помочь вам с аггрегацией информации. \n"
             "Вот список доступных команд:\n \n"
             "• /summarize:  Суммаризация по каналам 💻\n"
             "• /base_channels:  Показать перечень отслеживаемых каналов с опцией редактирования 📕\n"
             "• /help:  Выводит список команд 🛟\n"
             "• /cancel:  Отменяет действие ( Можете использовать в любой момент времени ) 🚨\n"
             "• /about:  Информация о проекте 💳",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.in_(["Отмена", "Отменить",
                            "отмена", "отменить",
                            "Cancel", "cancel"]))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )
    await cmd_help(message, state)

@router.message(Command(commands=["help"]))
@router.message(F.text.in_(["Помощь", "Помоги",
                            "помощь", "помоги",
                            "Help", "help",
                            "Menu", "menu",
                            "Меню", "меню"]))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Возвращаемся в меню. \n"
             "Вот список доступных команд:\n\n"
             "• /summarize:  Суммаризация по каналам 💻\n"
             "• /base_channels:  Вывести/изменить список отслеживаемых каналов 📕\n"
             "• /help:  Вывести список команд 🛟\n"
             "• /cancel:  Отменить действие 🚨\n"
             "• /about:  Информация о проекте 💳"
        ,
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["about"]))
async def cmd_cancel(message: Message):
    await message.answer(
        text =
        """
        Проект создан для облегчения работы с аггрегацией информации***. \n
        """
        ,
        reply_markup=ReplyKeyboardRemove()
    )
