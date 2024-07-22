import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from handlers import common, summarize, base_channels, ml_logic
from decouple import config


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/summarize", description="Суммаризация по каналам"),
        BotCommand(command="/base_channels", description="Отслеживаемые каналы"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/cancel", description="Отменить действие"),
        BotCommand(command="/about", description="Информация о проекте"),
    ]
    await bot.set_my_commands(commands)

bot = Bot(token=config('BOT_TOKEN'))


async def main(bot):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(common.router,
                       summarize.router,
                       base_channels.router,
                       ml_logic.router)

    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main(bot))
