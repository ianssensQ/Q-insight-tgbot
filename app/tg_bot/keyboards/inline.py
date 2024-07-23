from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def make_inline_keyboard(buttons):
    """
    Создает клавиатуру с произвольным количеством кнопок.

    :param buttons: Список пар (текст кнопки, callback_data), которые нужно добавить
    :return: Обновленная клавиатура
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    return add_buttons_to_keyboard(keyboard, buttons)


def add_buttons_to_keyboard(keyboard, buttons):
    """
    Добавляет произвольное количество кнопок к существующей клавиатуре.

    :param keyboard: Экземпляр InlineKeyboardMarkup, к которому нужно добавить кнопки
    :param buttons: Список пар (текст кнопки, callback_data), которые нужно добавить
    :return: Обновленная клавиатура
    """
    new_buttons = [[InlineKeyboardButton(text=text, callback_data=callback_data)] for text, callback_data in buttons]
    for button in new_buttons:
        keyboard.inline_keyboard.append(button)
    return keyboard


def list_and_base_edit(channels_urls):
    """
    Создает меню выбора действий к списку каналов.

    :param channels_urls: Dict URL TG каналов и их entity, имена которых нужно вывести
    :return: Обновленная клавиатура
    """
    buttons = []
    for channel in channels_urls:
        name = channel[1].title
        link = channel[0]
        buttons.append([InlineKeyboardButton(text=name, callback_data=name, url=link)])

    buttons.append([InlineKeyboardButton(text="▪️Добавить канал", callback_data="add"),
                    InlineKeyboardButton(text="▪️Удалить канал", callback_data="delete")])
    buttons.append([InlineKeyboardButton(text="▪️Сбросить все отслеживаемые каналы", callback_data="reset")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def channel_list_urls(channels_):
    """
    Выводит список каналов в виде клавиатуры
    и ссылки каналов передаются в виде callback_data

    :param channels_:(channels_entities, channels_urls) Список URL TG каналов, имена которых можно удалить
    :return: InlineKeyboardMarkup
    """
    keyboard = []
    channel_names = []
    for channel in channels_:
        name = channel[0].title
        url = channel[1]
        keyboard.append([InlineKeyboardButton(text=name, callback_data=url)])
        channel_names.append(name)
    return InlineKeyboardMarkup(inline_keyboard=keyboard), channel_names


def channel_list_view(channels_):
    """
    Выводит список каналов в виде клавиатуры
    и ссылки каналов передаются в виде url

    :param channels_:(channels_entities, channels_urls) Список URL TG каналов, имена которых можно удалить
    :return: InlineKeyboardMarkup
    """
    keyboard = []
    channel_names = []
    for channel in channels_:
        name = channel[0].title
        url = channel[1]
        keyboard.append([InlineKeyboardButton(text=name, url=url)])
        channel_names.append(name)
    return InlineKeyboardMarkup(inline_keyboard=keyboard), channel_names


def date_keyboard():
    """
    Создает клавиатуру с кнопками "1 день", "3 дня", "7 дней".

    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="▪️1 день", callback_data='1'),
            InlineKeyboardButton(text="▪️3 дня", callback_data='3'),
            InlineKeyboardButton(text="▪️7 дней", callback_data='7'),
        ]
    ])
