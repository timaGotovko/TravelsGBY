from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from openai import AsyncOpenAI
from bot.config import OPENAI_API_KEY
from bot.states.gpt_state import GPTDialog
from datetime import datetime
import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

memory_storage = {}  # user_id: [messages]

# Загружаем справку по визам
with open("bot/data/visa_combined_prompt.txt", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

@router.callback_query(F.data == "chat")
async def start_chat(call: CallbackQuery, state: FSMContext):
    await call.message.answer("💬 Вы можете задать свой вопрос туристическому консультанту.")
    await state.set_state(GPTDialog.chatting)
    try:
        await call.answer()
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")

@router.message(GPTDialog.chatting)
async def handle_chat_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_text = message.text.strip()
    memory = memory_storage.setdefault(user_id, [])

    # Установка системного промта, если он ещё не задан
    if not memory or memory[0].get("role") != "system":
        memory.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

        # Добавим уточнение про климат только при первом обращении
        memory.append({
            "role": "user",
            "content": (
                f"Сегодня: {datetime.now().strftime('%d.%m.%Y')}.Если дата поездки ближе, чем через 10 дней, можно примерно оценить климат, сезон и погодные условия."
            )
        })

    memory.append({"role": "user", "content": user_text})
    await message.chat.do("typing")

    log_message(user_id, f"[USER] {user_text}")

    # Обрезка истории по длине
    MAX_HISTORY_MESSAGES = 30
    if len(memory) > MAX_HISTORY_MESSAGES:
        system = memory[0] if memory[0]["role"] == "system" else None
        memory = [system] + memory[-(MAX_HISTORY_MESSAGES - 1):] if system else memory[-MAX_HISTORY_MESSAGES:]
        memory_storage[user_id] = memory

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=memory,
            temperature=0.5,
        )
        answer = response.choices[0].message.content.strip()
        memory.append({"role": "assistant", "content": answer})

        menu_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В главное меню", callback_data="exit_tours")]
        ])
        cleaned_answer = answer.replace("**", "")
        await message.answer(cleaned_answer, reply_markup=menu_markup)
        log_message(user_id, f"[BOT] {answer}")

    except Exception as e:
        error_text = "⚠️ Произошла ошибка при обращении к ИИ. Нажмите /start для повторного запуска"
        await message.answer(error_text)
        print(f"[ERROR] OpenAI API failed: {e}")
        log_message(user_id, f"[ERROR] {str(e)}")


# 🔹 Функция логирования
def log_message(user_id, text):
    os.makedirs("dialog_logs", exist_ok=True)
    log_file = f"dialog_logs/{user_id}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {text}\n")
