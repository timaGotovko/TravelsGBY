from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from bot.keyboards.main import main_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "👋 Добро пожаловать в турагентство <b>TravelsG.by</b>!\n\n"
        "Вот что я умею:\n"
        "🧠 <b>Онлайн-консультация</b> — отвечу на любые вопросы\n"
        "🎯 <b>Подбор туров</b> — подберу лучший вариант по вашим критериям\n"
        "💬 <b>Связь с менеджером</b>\n\n"
        "👇 Выберите кнопку ниже, чтобы начать:"
    )
    await message.answer(text, reply_markup=main_keyboard())
