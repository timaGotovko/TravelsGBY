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
    return InlineKeyboardMarkup(inline_keyboard=buttons)
