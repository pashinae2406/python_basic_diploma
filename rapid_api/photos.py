import json
import re
from typing import Dict, List
from rapid_api.request import request_to_api


def search_photos(results: List, count_photos: int) -> List:
    """Функция вывода фотографий отелей"""

    for i_value in results:
        i_value.update({'photos': list()})
        request_3 = request_to_api("https://hotels4.p.rapidapi.com/properties/get-hotel-photos", {'id': i_value['id']})
        data_3: Dict = json.loads(request_3)
        for i_photo in data_3['hotelImages'][:count_photos]:
            jmg = re.sub('_{size}', '', i_photo['baseUrl'])
            i_value['photos'].append(jmg)

    return results
