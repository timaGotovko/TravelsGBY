from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.services.uon_crm import create_lead
from bot.config import GROUP_CHAT_ID
from bot.handlers.tour_search import user_tour_results
from bot.keyboards.main import share_contact_keyboard
import re
from bot.keyboards.main import main_keyboard

router = Router()

class BookingState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_username = State()

@router.callback_query(F.data == "book")
async def start_booking(call: CallbackQuery, state: FSMContext):
    await state.set_state(BookingState.waiting_name)
    msg = await call.message.answer("✍️ Введите ваше имя:")
    await state.update_data(prompt_id=msg.message_id)
    try:
        await call.answer()
    except Exception as e:
        print(f"[ERROR] Не удалось удалить сообщение: {e}")

@router.message(BookingState.waiting_name)
async def get_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)
    try:
        await message.delete()
        data = await state.get_data()
        if "prompt_id" in data:
            await message.bot.delete_message(message.chat.id, data["prompt_id"])
    except Exception as e:
        print(f"[ERROR] Не удалось удалить сообщение: {e}")
    await message.answer(f"✅ Вы ввели имя: {name}")
    msg = await message.answer("📞 Пожалуйста, поделитесь номером телефона, нажав кнопку ниже:", reply_markup=share_contact_keyboard)
    await state.update_data(prompt_id=msg.message_id)
    await state.set_state(BookingState.waiting_phone)

@router.message(BookingState.waiting_phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone=phone_number)
    try:
        await message.delete()
        data = await state.get_data()
        if "prompt_id" in data:
            await message.bot.delete_message(message.chat.id, data["prompt_id"])
    except Exception as e:
        print(f"[ERROR] Не удалось удалить сообщение: {e}")

    await message.answer(f"✅ Вы ввели телефон: {phone_number}")
    msg = await message.answer("📱 Введите ваш Telegram username (без @):", reply_markup=ReplyKeyboardRemove())
    await state.update_data(prompt_id=msg.message_id)
    await state.set_state(BookingState.waiting_username)

@router.message(BookingState.waiting_username)
async def get_username(message: Message, state: FSMContext):
    username = message.text.strip()
    if not re.match(r"^\w{3,32}$", username):
        await message.answer("❗ Неверный формат username. Введите без @, только буквы, цифры или подчёркивания.")
        return
    await state.update_data(username=message.text)
    try:
        await message.delete()
        data = await state.get_data()
        if "prompt_id" in data:
            await message.bot.delete_message(message.chat.id, data["prompt_id"])
    except Exception as e:
        print(f"[ERROR] Не удалось удалить сообщение: {e}")
    await message.answer(f"✅ Вы ввели username: @{username}")
    data = await state.get_data()
    user_id = message.from_user.id
    tours = user_tour_results.get(user_id, {}).get("tours", [])
    tour_info = tours[0] if tours else {}

    comment = (
        f"Заявка с Telegram:\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🔗 Username: @{data['username']}\n"
        f"🏨 Отель: {tour_info.get('hotelName', '—')}\n"
        f"🌍 Страна: {tour_info.get('countryName', '—')}\n"
        f"💥Город отправления: {tour_info.get('departCityName', '—')}\n"
        f"📅 Даты тура: {tour_info.get('tourDate', '—')} → {tour_info.get('tourEndDate', '—')}\n"
        f"💰 Цена: {tour_info.get('price', '—')} USD\n"
        f"🔗 Ссылка: {tour_info.get('tourUrl', '—')}"
    )

    # Отправка в CRM с повторной попыткой и логированием в группу
    await create_lead(
        name=data["name"],
        phone=data["phone"],
        comment=comment,
        bot=message.bot  # Передаём объект бота для логов об ошибке
    )

    # Уведомление в группу Telegram
    group_text = (
        f"{comment}"
    )
    await message.bot.send_message(chat_id=GROUP_CHAT_ID, text=group_text)

    await message.answer("✅ Ваша заявка отправлена! С вами свяжется менеджер.", reply_markup=main_keyboard())
    await state.clear()

