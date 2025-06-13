from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def price_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="До 1000", callback_data="price_1000")],
        [InlineKeyboardButton(text="До 1500", callback_data="price_1500")],
        [InlineKeyboardButton(text="До 2000", callback_data="price_2000")],
        [InlineKeyboardButton(text="До 2500", callback_data="price_2500")],
        [InlineKeyboardButton(text="3000 и выше", callback_data="price_3000+")]
    ])
