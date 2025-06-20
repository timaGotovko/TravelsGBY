from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.constants.countries import COUNTRIES, COUNTRIESFORMOSKOV


def country_keyboard():
    keyboard = []
    row = []
    for i, name in enumerate(COUNTRIES.keys()):
        row.append(InlineKeyboardButton(text=name, callback_data=f"country_{name}"))
        if len(row) == 3:  # 3 кнопки в строке
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="exit_tours")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def country_keyboard_for_Moskov():
    keyboard = []
    row = []
    for i, name in enumerate(COUNTRIESFORMOSKOV.keys()):
        row.append(InlineKeyboardButton(text=name, callback_data=f"country_{name}"))
        if len(row) == 3:  # 3 кнопки в строке
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="exit_tours")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


share_contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Поделиться номером", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Онлайн консультация", callback_data="chat")],
        [InlineKeyboardButton(text="🎯 Подбор туров", callback_data="tours")],
        [InlineKeyboardButton(text="💬 Контакт менеджера", url="https://t.me/pln_iva")]
    ])

def main_menu_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="exit_tours")]
    ])
