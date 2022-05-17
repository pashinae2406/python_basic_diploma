from typing import Dict
from config_data.config import RAPID_API_KEY
import requests


def request_to_api(url: str, data: Dict) -> str:
    """Функция запроса к api по заданным параметрам"""

    headers: Dict = {
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
        "X-RapidAPI-Key": RAPID_API_KEY
    }

    try:
        response = requests.request("GET", url, headers=headers, params=data, timeout=30)
        if response.status_code == requests.codes.ok:
            return response.text
        else:
            print('Ошибка: ', response)
    except TimeoutError:
        print('Исключение - TimeoutError')
