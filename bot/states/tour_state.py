from aiogram.fsm.state import StatesGroup, State

class TourSearchState(StatesGroup):
    country = State()
    city = State()
    date = State()
    nights = State() 
    kids = State()
    priceMax = State()
    people = State()
    resort = State()
    hotel_category = State()
    show_results = State()
