from aiogram.fsm.state import StatesGroup, State


class Base(StatesGroup):
    add = State()
    catch_channel = State()
    edit = State()
    base_menu = State()
    delete = State()
