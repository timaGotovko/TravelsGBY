import json
from pathlib import Path
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

with open(Path("bot/data/cities_by_country.json"), encoding="utf-8") as f:
    CITIES_BY_COUNTRY = json.load(f)

def generate_city_keyboard(country_id: int):
    cities = CITIES_BY_COUNTRY.get(str(country_id), [])
    keyboard = [
        [InlineKeyboardButton(text=city["name"], callback_data=f"resort_{city['id']}")]
        for city in cities
    ]
    keyboard.append([InlineKeyboardButton(text="🏙 Город не важен", callback_data="resort_skip")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)