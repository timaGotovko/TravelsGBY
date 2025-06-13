from datetime import datetime, timedelta
import aiohttp
import asyncio
import json
import time

BASE_URL = "https://mw.intercity.by:9000/TourSearchOwin2/searchApi"

async def fetch_tours_for_day(session, params, date):
    query = params.copy()
    query.update({
        "action": "GetTours",
        "version": "1.08",
        "dateFrom": date.strftime("%d.%m.%Y"),
        "dateTo": date.strftime("%d.%m.%Y"),
    })

    start = time.perf_counter()
    async with session.get(BASE_URL, params=query, ssl=False) as response:
        data = await response.json()
    duration = time.perf_counter() - start
    tours = data.get("tours", [])
    print(f"📅 Поиск туров на {date.date()} | Найдено: {len(tours)} | ⏱️ {duration:.2f} сек.")
    return tours

def priority_score(tour):
    return sum([
        int(tour.get("ticketsIncluded") == 1),
        int(tour.get("hasEconomTicketsDpt") == 1),
        int(tour.get("hasEconomTicketsRtn") == 1)
    ])

async def search_tours_to_file(params: dict, output_file="all_tours.json", max_concurrent=15):
    date_from = datetime.strptime(params["dateFrom"], "%d.%m.%Y")
    date_to = datetime.strptime(params["dateTo"], "%d.%m.%Y")
    days = [(date_from + timedelta(days=i)) for i in range((date_to - date_from).days + 1)]
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_and_score(date):
        async with semaphore:
            tours = await fetch_tours_for_day(session, params, date)
            return sorted(tours, key=priority_score, reverse=True)

    async with aiohttp.ClientSession() as session:
        print(f"🔁 Всего дней поиска: {len(days)}")
        start_all = time.perf_counter()
        results = await asyncio.gather(*[fetch_and_score(day) for day in days])

        # 🕒 Замер времени фильтрации и удаления дубликатов
        filter_start = time.perf_counter()

        seen_hotels = set()
        unique_tours = []
        for day_tours in results:
            for tour in day_tours:
                hotel = tour.get("hotelName")
                if hotel and hotel not in seen_hotels:
                    seen_hotels.add(hotel)
                    unique_tours.append(tour)

        filter_duration = time.perf_counter() - filter_start
        print(f"⚙️ Время фильтрации и удаления дубликатов: {filter_duration:.2f} сек.")
        print(f"📊 Уникальных туров после сортировки: {len(unique_tours)}")

        total_duration = time.perf_counter() - start_all
        print(f"💾 Общее время обработки всех дат: {total_duration:.2f} сек.")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_tours, f, ensure_ascii=False, indent=2)
        print(f"📦 Всего туров сохранено: {len(unique_tours)} в {output_file}")

    return unique_tours
