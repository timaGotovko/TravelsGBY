
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from bot.states.tour_state import TourSearchState
from bot.services.tour_api import search_tours_to_file
from bot.keyboards.main import main_keyboard, main_menu_button
import re
from datetime import datetime, date
from bot.keyboards.main import country_keyboard, country_keyboard_for_Moskov
from bot.constants.countries import COUNTRIES
from bot.keyboards.price_keyboard import price_keyboard
from bot.keyboards.city_keyboard import generate_city_keyboard
from bot.keyboards.hotel_category_keyboard import hotel_category_keyboard
from bot.keyboards.hotel_category_keyboard import HOTEL_CATEGORIES
from bot.utils.tour_utils import build_tour_params
from bot.keyboards.departure_city_keyboard import departure_city_keyboard


router = Router()
user_tour_results = {}

@router.callback_query(F.data == "tours")
async def ask_departure_city(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("🛫 Выберите город вылета:", reply_markup=departure_city_keyboard())
    await state.set_state(TourSearchState.departure_city)



@router.callback_query(F.data.startswith("country_"))
async def handle_country_selection(call: CallbackQuery, state: FSMContext):
    country_name = call.data.replace("country_", "")
    country_id = COUNTRIES[country_name]["id"]
    await state.update_data(countryId=country_id, countryName=country_name)
    # await call.message.edit_text(f"✅ Страна выбрана: {country_name}")
    try:
        await call.message.delete()
    except Exception as e:
        print(f"[ERROR] Не удалось удалить сообщение: {e}")
    msg = await call.message.answer("📅 Введите диапазон дат когда вы хотите вылететь в формате ДД.ММ.ГГГГ - ДД.ММ.ГГГГ:", reply_markup=main_menu_button())
    await state.update_data(prompt_id=msg.message_id)
    await state.set_state(TourSearchState.date)
    try:
        await call.answer()
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")

@router.callback_query(F.data.startswith("dep_"))
async def handle_departure_city(call: CallbackQuery, state: FSMContext):
    city_id = int(call.data.replace("dep_", ""))
    city_name = {
        448: "Минск",
        1: "Москва",
    }.get(city_id, "Город")

    await state.update_data(departCityId=city_id, departCityName=city_name)

    try:
        await call.message.delete()
    except:
        pass

    # 👇 Выбор нужной клавиатуры
    if city_id == 1:  # Москва
        keyboard = country_keyboard_for_Moskov()
    else:  # Минск и всё остальное по умолчанию
        keyboard = country_keyboard()

    await call.message.answer("🌍 Выберите страну по кнопке ниже:", reply_markup=keyboard)
    await call.message.answer("ℹ️ Или нажмите, чтобы вернуться в главное меню:", reply_markup=main_menu_button())
    await state.set_state(TourSearchState.country)

    try:
        await call.answer()
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")



@router.message(TourSearchState.date)
async def ask_nights_range(message: Message, state: FSMContext):
    text = message.text.strip()
    match = re.match(r"(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})", text)
    if not match:
        try:
            await message.delete()
            data = await state.get_data()
            if "prompt_id" in data:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=data["prompt_id"])
        except Exception as e:
            print(f"[ERROR] При удалении сообщений: {e}")

        msg = await message.answer("❗ Неверный формат. Введите как: 22.06.2025 - 22.08.2025", reply_markup=main_menu_button())
        await state.update_data(prompt_id=msg.message_id)
        return

    date_from_str, date_to_str = match.groups()

    try:
        date_from = datetime.strptime(date_from_str, "%d.%m.%Y").date()
        date_to = datetime.strptime(date_to_str, "%d.%m.%Y").date()
    except ValueError:
        await message.answer("❗ Неверные даты. Проверьте формат.", reply_markup=main_menu_button())
        return

    # 🚫 Проверка на прошедшие даты
    if date_from < date.today():
        try:
            await message.delete()
            data = await state.get_data()
            if "prompt_id" in data:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=data["prompt_id"])
        except Exception as e:
            print(f"[ERROR] При удалении сообщений: {e}")

        msg = await message.answer("❗ Дата начала поездки уже прошла. Введите актуальные даты.", reply_markup=main_menu_button())
        await state.update_data(prompt_id=msg.message_id)
        return

    await state.update_data(dateFrom=date_from_str, dateTo=date_to_str)

    try:
        await message.delete()
        data = await state.get_data()
        if "prompt_id" in data:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data["prompt_id"])
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")

    # await message.answer(f"📅 Вы выбрали даты отправления: <b>{date_from_str}</b> – <b>{date_to_str}</b>")
    msg = await message.answer("🏨 Введите диапазон ночей  (например, 7-12):", reply_markup=main_menu_button())
    await state.update_data(prompt_id=msg.message_id)
    await state.set_state(TourSearchState.nights)

@router.message(TourSearchState.nights)
async def ask_adults(message: Message, state: FSMContext):
    text = message.text.strip()
    match = re.match(r"(\d+)-(\d+)", text)
    if not match:
        try:
            await message.delete()
            data = await state.get_data()
            if "prompt_id" in data:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=data["prompt_id"])
        except Exception as e:
            print(f"[ERROR] При удалении сообщений: {e}")

        msg = await message.answer("❗ Неверный формат. Введите как: 7-12", reply_markup=main_menu_button())
        await state.update_data(prompt_id=msg.message_id)
        return

    nights_min, nights_max = map(int, match.groups())
    await state.update_data(nightsMin=nights_min, nightsMax=nights_max)
    try:
        await message.delete()
        data = await state.get_data()
        if "prompt_id" in data:
            await message.bot.delete_message(message.chat.id, data["prompt_id"])
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")

    # await message.answer(f"🌙 Вы выбрали продолжительность: <b>{nights_min}–{nights_max}</b> ночей")
    msg = await message.answer("👥 Укажите количество взрослых:", reply_markup=main_menu_button())
    await state.update_data(prompt_id=msg.message_id)
    await state.set_state(TourSearchState.people)

@router.message(TourSearchState.people)
async def ask_kids(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        adults = int(text)
        await state.update_data(adults=adults)
    except ValueError:
        try:
            await message.delete()
            data = await state.get_data()
            if "prompt_id" in data:
                await message.bot.delete_message(message.chat.id, data["prompt_id"])
        except Exception as e:
            print(f"[ERROR] При удалении сообщений: {e}")

        msg = await message.answer("❗ Введите число.", reply_markup=main_menu_button())
        await state.update_data(prompt_id=msg.message_id)
        return

    try:
        await message.delete()
        data = await state.get_data()
        if "prompt_id" in data:
            await message.bot.delete_message(message.chat.id, data["prompt_id"])
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")

    # await message.answer(f"👥 Взрослых: <b>{adults}</b>")
    msg = await message.answer("🧒 Укажите количество детей (0, если нет):", reply_markup=main_menu_button())
    await state.update_data(prompt_id=msg.message_id)
    await state.set_state(TourSearchState.kids)

@router.message(TourSearchState.kids)
async def ask_price(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        kids = int(text)
        await state.update_data(kids=kids)
    except ValueError:
        try:
            await message.delete()
            data = await state.get_data()
            if "prompt_id" in data:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=data["prompt_id"])
        except Exception as e:
            print(f"[ERROR] При удалении сообщений: {e}")

        msg = await message.answer("❗ Введите число.", reply_markup=main_menu_button())
        await state.update_data(prompt_id=msg.message_id)
        return

    try:
        await message.delete()
        data = await state.get_data()
        if "prompt_id" in data:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data["prompt_id"])
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")

    # await message.answer(f"🧒 Детей: <b>{kids}</b>")
    msg = await message.answer("💵 Укажите максимальную сумму в долларах:", reply_markup=price_keyboard())
    await message.answer("ℹ️ Или нажмите, чтобы вернуться в главное меню:", reply_markup=main_menu_button())
    await state.update_data(prompt_id=msg.message_id)
    await state.set_state(TourSearchState.priceMax)


@router.callback_query(F.data.startswith("price_"))
async def handle_price_selection(call: CallbackQuery, state: FSMContext):
    price_text = call.data.replace("price_", "")

    # Определение диапазонов по кнопке
    ranges = {
        "2000": (1600, 2300),
        "2500": (2300, 2800),
        "3000": (2800, 3300),
        "3500": (3300, 3800),
        "4000": (3800, 999999),
    }

    if price_text not in ranges:
        await call.message.answer("❗ Неизвестный диапазон цен.", reply_markup=main_menu_button())
        return

    price_min, price_max = ranges[price_text]
    await state.update_data(priceMin=price_min, priceMax=price_max)

    data = await state.get_data()

    summary = (
        f"⌛ Мы подбираем для вас идеальный тур по вашим параметрам.\n"
        f"При большой нагрузке поиск может занимать около 1 минуты❣️\n\n"
        f"✅ <b>Выбранные параметры:</b>\n"
        f"🌍 Страна: {data.get('countryName', '—')}\n"
        f"💥 Город отправления: {data.get('departCityName', '—')}\n"
        f"📅 Даты: {data.get('dateFrom')} – {data.get('dateTo')}\n"
        f"🌙 Ночи: {data.get('nightsMin')}–{data.get('nightsMax')}\n"
        f"👥 Взрослых: {data.get('adults')}, Детей: {data.get('kids')}\n"
        f"💵 Бюджет: {price_min}–{price_max} USD\n\n"
        f"⌛ Ищем туры, подождите..."
    )
    await call.message.edit_text(summary)

    params = build_tour_params(data)

    tours = await search_tours_to_file(params, output_file="all_tours.json")

    for tour in tours:
        tour["departCityName"] = data.get("departCityName", "—")

    if not tours:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В главное меню", callback_data="exit_tours")]
        ])
        await call.message.edit_text(
            "🙁 Туров по заданным параметрам не найдено. Вернитесь в подбор туров и расширьте фильтр.",
            reply_markup=markup
        )
        await call.message.answer("ℹ️ Или нажмите, чтобы вернуться в главное меню:", reply_markup=main_menu_button())
        await state.clear()
        return

    user_tour_results[call.from_user.id] = {"tours": tours, "index": 0}
    await state.set_state(TourSearchState.show_results)
    await send_tour_info(call.message, tours[0], 0, len(tours))

    try:
        await call.answer()
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")




async def send_tour_info(message: Message, tour: dict, index: int, total: int):

    text = (
        f"🏖 <b>Тур {index + 1} из {total}</b>\n"
        f"🌍 <b>Страна:</b> {tour.get('countryName', '—')}\n"
        f"💥Город отправления: {tour.get('departCityName', '—')}\n"
        f"🏨 <b>Отель:</b> {tour.get('hotelName', '—')}\n"
        f"🏙 <b>Город:</b> {tour.get('resortName', '—')}\n"
        f"📅 <b>Даты:</b> {tour.get('tourDate', '—')} → {tour.get('tourEndDate', '—')}\n"
        f"🔗 <b>Ссылка:</b> {tour.get('hotelUrl') or tour.get('tourUrl', '—')}\n"
        f"💰 <b>Цена:</b> {tour.get('price', '—')} USD *\n"
        f"* Цены могут немного отличаться. Точную стоимость подтверждает менеджер при бронировании."
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="prev"),
            InlineKeyboardButton(text="▶️ Вперёд", callback_data="next")
        ],
        [InlineKeyboardButton(text="🛎 Забронировать", callback_data="book")],
        [InlineKeyboardButton(text="➕ Добавить параметры", callback_data="add_params")],
        [InlineKeyboardButton(text="🔙 Выйти в меню", callback_data="exit_tours")]
    ])

    await message.answer(text, reply_markup=markup)

@router.callback_query(F.data.in_(["next", "prev"]))
async def navigate_tours(call: CallbackQuery):
    user_id = call.from_user.id
    results = user_tour_results.get(user_id)
    if not results:
        try:
            await call.answer("Нет туров")
        except Exception as e:
            print(f"[ERROR] call.answer() failed: {e}")
        return

    index = results["index"]
    index = (index + 1) % len(results["tours"]) if call.data == "next" else (index - 1) % len(results["tours"])
    results["index"] = index

    try:
        await call.message.delete()
    except Exception as e:
        print(f"[ERROR] message.delete() failed: {e}")

    await send_tour_info(call.message, results["tours"][index], index, len(results["tours"]))

    try:
        await call.answer()
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")


@router.callback_query(F.data == "exit_tours")
async def exit_tours_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    user_tour_results.pop(call.from_user.id, None)
    await call.message.edit_text("🔙 Вы вернулись в главное меню", reply_markup=main_keyboard())
    try:
        await call.answer()
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")

@router.callback_query(F.data == "add_params")
async def add_optional_filters(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    country_id = data.get("countryId")

    await call.message.edit_text(
        "🏙 Выберите город для фильтрации:",
        reply_markup=generate_city_keyboard(country_id)
    )
    await state.set_state(TourSearchState.resort)

@router.callback_query(F.data.startswith("resort_"))
async def handle_resort_selection(call: CallbackQuery, state: FSMContext):
    resort_id = call.data.replace("resort_", "")
    if resort_id != "skip":
        await state.update_data(resorts=resort_id)
    else:
        await state.update_data(resorts=None)

    data = await state.get_data()

    if resort_id != "skip":
        resort_name = next(
            (
                btn.text
                for row in generate_city_keyboard(data["countryId"]).inline_keyboard
                for btn in row
                if f"resort_{resort_id}" in btn.callback_data
            ),
            "Город"
        )
        await state.update_data(resorts=resort_id, resortName=resort_name)
    else:
        await state.update_data(resorts=None, resortName=None)

    try:
        await call.message.delete()
    except Exception as e:
        print(f"[ERROR] Не удалось удалить клавиатуру с городами: {e}")

    # Переход к выбору категории отеля
    await call.message.answer("🏨 Выберите категорию отеля:", reply_markup=hotel_category_keyboard())
    await call.message.answer("ℹ️ Или нажмите, чтобы вернуться в главное меню:", reply_markup=main_menu_button())
    await state.set_state(TourSearchState.hotel_category)

@router.callback_query(F.data.startswith("hotelcat_"))
async def handle_hotel_category(call: CallbackQuery, state: FSMContext):
    cat_id = call.data.replace("hotelcat_", "")
    if cat_id != "skip":
        await state.update_data(hotelCategories=cat_id)
        category_name = next(
            (c["name"] for c in HOTEL_CATEGORIES if str(c["id"]) == cat_id),
            "Неизвестно"
        )
        await state.update_data(hotelCategories=cat_id, hotelCategoryName=category_name)
    else:
        await state.update_data(hotelCategories=None, hotelCategoryName=None)

    try:
        await call.message.delete()
    except Exception as e:
        print(f"[ERROR] Не удалось удалить клавиатуру со звездами: {e}")

    data = await state.get_data()
    summary = (
    f"⌛ Мы подбираем для вас идеальный тур по расширенным параметрам.\n При большой нагрузке поиск может занимать около 1 минут❣️\n"
    f"✅ <b>Параметры для фильтрации:</b>\n"
    f"🌍 Страна: {data.get('countryName', '—')}\n"
    f"💥Город отправления: {data.get('departCityName', '—')}\n"
    f"📅 Даты: {data.get('dateFrom')} – {data.get('dateTo')}\n"
    f"🌙 Ночи: {data.get('nightsMin')}–{data.get('nightsMax')}\n"
    f"👥 Взрослых: {data.get('adults')}, Детей: {data.get('kids')}\n"
    f"🏙️ Город: {data.get('resortName', '—')}\n"
    f"💫 Категория отеля: {data.get('hotelCategoryName', '—')}\n"
    f"💵 Бюджет: {data.get('priceMax', '—')} USD\n\n"
    f"⌛ Ищем туры по дополнительным параметрам..."
    )

    await call.message.answer(summary)  

    params = build_tour_params(data) # Параметры

    print("🔍 Отправка с параметрами:", params)

    tours = await search_tours_to_file(params, output_file="all_tours.json")

    for tour in tours:
        tour["departCityName"] = data.get("departCityName", "—")

    if not tours:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В главное меню", callback_data="exit_tours")]
        ])
        await call.message.edit_text("🙁 Туров по заданным параметрам не найдено. Вернитесь в подбор туров и расширьте фильтр.", reply_markup=markup)
        await call.message.answer("ℹ️ Или нажмите, чтобы вернуться в главное меню:", reply_markup=main_menu_button())
        await state.clear()
        return

    user_tour_results[call.from_user.id] = {"tours": tours, "index": 0}
    await state.set_state(TourSearchState.show_results)
    await send_tour_info(call.message, tours[0], 0, len(tours))
    try:
        await call.answer()
    except Exception as e:
        print(f"[ERROR] call.answer() failed: {e}")