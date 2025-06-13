import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import BOT_TOKEN
from bot.handlers import start, gpt_chat, tour_search, booking
from aiogram.client.default import DefaultBotProperties

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        start.router,
        gpt_chat.router,
        tour_search.router,
        booking.router,
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
