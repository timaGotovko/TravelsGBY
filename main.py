import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from bot.config import BOT_TOKEN
from bot.handlers import start, gpt_chat, tour_search, booking
from aiogram.types import Update  # не забудь импортировать вверху

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = 8080

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(start.router, gpt_chat.router, tour_search.router, booking.router)

async def handle_webhook(request):
    raw_data = await request.json()
    update = Update.model_validate(raw_data)
    await dp.feed_update(bot=bot, update=update)
    return web.Response()



async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()

async def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBAPP_PORT)
    await site.start()

    print(f"🌐 Webhook запущен на {WEBAPP_HOST}:{WEBAPP_PORT}")

    # Keep the service running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
