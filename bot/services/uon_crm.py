import aiohttp
import asyncio
from bot.config import UON_TOKEN, UON_BASE_URL, GROUP_CHAT_ID
from aiogram import Bot

async def create_lead(name: str, phone: str, comment: str = "", bot: Bot = None, retries: int = 2):
    url = f"{UON_BASE_URL}{UON_TOKEN}/request/create.json"
    payload = {
        "u_name": name,
        "u_phone": phone,
        "source": "Telegram-бот",
        "source_id": 1,
        "manager_id": 3,
    }

    timeout = aiohttp.ClientTimeout(
        total=30,
        connect=10,
        sock_read=10,
        sock_connect=10
    )

    for attempt in range(1, retries + 2):  # Первая попытка + retries
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, data=payload, ssl=False) as response:
                    text = await response.text()
                    print("📤 Отправили в U-ON:", payload)
                    print("📥 Ответ от U-ON:", text)
                    if response.status == 200:
                        return {"success": True, "response": text}
                    else:
                        raise Exception(f"Статус {response.status}, тело: {text}")
        except (asyncio.TimeoutError, aiohttp.ClientError, Exception) as e:
            error_text = f"❌ Ошибка при отправке в U-ON на попытке {attempt}:\n{e}"

            # лог в консоль
            print(error_text)

            # отправка ошибки в группу, если есть bot
            if bot:
                await bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=(
                        "🚨 <b>Ошибка отправки заявки в CRM</b>\n"
                        f"👤 <b>Имя:</b> {name}\n"
                        f"📱 <b>Телефон:</b> {phone}\n"
                        f"💬 <b>Комментарий:</b>\n{comment}\n\n"
                        f"<b>Ошибка:</b>\n<code>{str(e)}</code>"
                    ),
                    parse_mode="HTML"
                )

            if attempt >= retries + 1:
                return {"error": str(e)}
            await asyncio.sleep(2)  # пауза между попытками
