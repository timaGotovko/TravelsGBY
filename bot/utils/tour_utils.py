def build_tour_params(data: dict) -> dict:
    params = {
        "adults": data.get("adults"),
        "kids": data.get("kids"),
        "count": 50,
        "currencyId": 1,
        "countryId": data.get("countryId"),
        "dateFrom": data.get("dateFrom"),
        "dateTo": data.get("dateTo"),
        "departCityId": 448,
        "ticketsIncluded": 1,
        "nightsMin": data.get("nightsMin"),
        "nightsMax": data.get("nightsMax"),
        "hotelIsNotInStop": 1,
        "hasTickets": 0,
        "priceMax": data.get("priceMax")
    }

    if data.get("resorts"):
        params["resorts"] = data["resorts"]

    if data.get("hotelCategories"):
        params["hotelCategories"] = data["hotelCategories"]

    return params
