from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def departure_city_keyboard():
    cities = [
        ("Минск", 448),
        ("Москва", 1)
    ]
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"dep_{id}")]
        for name, id in cities
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="exit_tours")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
