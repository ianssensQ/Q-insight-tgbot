from aiogram.fsm.state import StatesGroup, State


class Summ(StatesGroup):
    choosing_what_summ = State()
    choosing_what_base_summ = State()
    choosing_date = State()
    no_base = State()
    choosing = State()
    generate_task = State()
    catch_channel = State()
    choosing_custom = State()
    Redirect = State()
    Predict = State()
