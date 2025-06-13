from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

HOTEL_CATEGORIES = [
    {"id": 23, "name": "1*"},
    {"id": 56, "name": "2*"},
    {"id": 57, "name": "3*"},
    {"id": 58, "name": "4*"},
    {"id": 59, "name": "5*"}
]

def hotel_category_keyboard():
    keyboard = [
        [InlineKeyboardButton(text=cat["name"], callback_data=f"hotelcat_{cat['id']}")]
        for cat in HOTEL_CATEGORIES
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)