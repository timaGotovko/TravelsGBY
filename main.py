import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

from bot.config import BOT_TOKEN
from bot.handlers import start, gpt_chat, tour_search, booking

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH
PORT = int(os.getenv("PORT", 8000))  # Railway использует PORT

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    print("🧹 Webhook удалён")

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    # Роутеры
    dp.include_routers(
        start.router,
        gpt_chat.router,
        tour_search.router,
        booking.router,
    )

    app = web.Application()
    app["bot"] = bot

    # Регистрируем хендлер webhook
    async def handler(request):
        data = await request.json()
        update = dp.bot.session.telegram.parse_update(data)
        await dp.feed_update(bot, update)
        return web.Response()

    app.router.add_post(WEBHOOK_PATH, handler)

    # Запуск
    await on_startup(bot)
    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
        await site.start()
        print(f"🚀 Webhook-сервер запущен на порту {PORT}")
        while True:
            await asyncio.sleep(3600)
    finally:
        await on_shutdown(bot)

if __name__ == "__main__":
    asyncio.run(main())
