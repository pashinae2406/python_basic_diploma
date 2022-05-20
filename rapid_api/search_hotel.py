import json
import re
from typing import Dict, List
from rapid_api.request import request_to_api
from loguru import logger
import operator


@logger.catch()
def search_hotel(destination_id: int, data: Dict) -> List:
    """Функция вывода информации по отелям в запрашиваемом у пользователя городе"""

    request_2 = request_to_api("https://hotels4.p.rapidapi.com/properties/list", {'destinationId': destination_id})
    pattern_2: str = r'(?<=,)"results":.+?(?=,"pagination")'
    find_2 = re.search(pattern_2, request_2)

    if find_2:
        data_2: Dict = json.loads(f"{{{find_2[0]}}}")
        result_search: List = [{'name': i_value.get('name', 'Нет'),
                                'address': i_value.get('address', 'Нет').get('streetAddress', 'Нет'),
                                'City center': i_value['landmarks'][0].get('distance', 'Нет'),
                                'current': i_value.get('ratePlan', 'Нет').get('price', 'Нет').get('current',
                                                                                                  'Нет'),
                                'exactCurrent': i_value.get('ratePlan', 'Нет').get('price', 'Нет').get(
                                    'exactCurrent', 'Нет'),
                                'id': i_value.get('id', 'Нет')}
                               for i_value in data_2['results']]
        result_search.sort(key=operator.itemgetter('exactCurrent'))
        result: List = list()

        for i_value in result_search:
            answer: str = f'\nОтель: {i_value["name"]}\nАдрес: {i_value["address"]}\n' \
                          f'Расстояние до центра: {i_value["City center"]}\nЦена за ночь: {i_value["current"]}\n' \
                          f'Стоимость за весь период проживания: {int(i_value["exactCurrent"] * data["count_days"].days)}\n' \
                          f'Ссылка на отель: https://www.hotels.com/ho{i_value["id"]}'
            i_value.update({'answer': answer})

        if data['commands'] == '/lowprice':
            for i_value in result_search[:int(data['count_hotels'])]:
                result.append(i_value)

        elif data['commands'] == '/highprice':
            for i_value in result_search[-int(data['count_hotels']):]:
                result.append(i_value)

        elif data['commands'] == '/bestdeal':
            for i_value in result_search:
                if (i_value["exactCurrent"] >= data['min_price']) and (i_value["exactCurrent"] <= data['max_price'])\
                        and (float(i_value["City center"].split(' ')[0]) >= data['min_distance'])\
                        and (float(i_value["City center"].split(' ')[0]) <= data['max_distance']):
                    if len(result) < int(data['count_hotels']):
                        result.append(i_value)

        return result
