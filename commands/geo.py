import webbrowser
from geopy.geocoders import Nominatim

# Создаём один экземпляр геокодера, чтобы не плодить объекты при каждом вызове
_geolocator = Nominatim(user_agent="jarvis_geo_assistant")


def search(query: str) -> str:
    """
    Ищет координаты по запросу и открывает точку в Яндекс Картах.

    :param query: текст запроса (адрес, название места и т.п.)
    :return: строка с подтверждением (для отображения в HUD/LCD)
    """
    # В твоём main.py условие выглядит так: if ('где находится' in text): search(text)
    # Поэтому тут можно аккуратно вырезать фразу-триггер, чтобы искать только суть.
    triggers = [
        "где находится",
        "найди где",
        "покажи где",
    ]
    cleaned_query = query
    for t in triggers:
        if t in cleaned_query:
            cleaned_query = cleaned_query.replace(t, "", 1).strip()
            break

    if not cleaned_query:
        raise ValueError("Не указан адрес для поиска.")

    location = _geolocator.geocode(cleaned_query)
    if not location:
        raise ValueError(f"Не удалось найти место: {cleaned_query}")

    # Яндекс Карты: ll=долгота,широта (сначала долгота!)
    url = f"https://yandex.ru/maps/?ll={location.longitude},{location.latitude}&z=16"
    webbrowser.open(url)

    return f"Открыл {cleaned_query} на карте"
