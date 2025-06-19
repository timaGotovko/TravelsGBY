from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def price_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="2000", callback_data="price_2000")],
        [InlineKeyboardButton(text="2500", callback_data="price_2500")],
        [InlineKeyboardButton(text="3000", callback_data="price_3000")],
        [InlineKeyboardButton(text="3500", callback_data="price_3500")],
        [InlineKeyboardButton(text="4000", callback_data="price_4000")]
    ])