import json
import re
from typing import Dict, List

from telebot.types import Message
import requests
import operator

from loader import bot
from config_data.config import RAPID_API_KEY
from states.requests import UserInfoState
from keyboards.reply.answer_no_yes import answer

"""Команда для поиска топ самых дешевых отелей в выбранном городе"""


def request_to_api(url: str, querystring: Dict) -> str:
    """Функция запроса к api по заданным параметрам"""

    headers: Dict = {
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
        "X-RapidAPI-Key": RAPID_API_KEY
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=30)
        if response.status_code == requests.codes.ok:
            return response.text
        else:
            raise Exception
    except Exception:
        print('Что-то пошло не так')


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    """Функция, запрашивающая у пользователя город для поиска отелей"""
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    bot.send_message(message.from_user.id, "В каком городе будем искать отели?")


@bot.message_handler(state=UserInfoState.city)
def bot_city(message: Message) -> None:
    """Функция запрашивающая у пользователя количество отелей для вывода"""
    bot.send_message(message.from_user.id, 'Спасибо, записал. Сколько отелей показать (не более 20)?')
    bot.set_state(message.from_user.id, UserInfoState.count_hotels, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as querystring:
        querystring['query'] = message.text


@bot.message_handler(state=UserInfoState.count_hotels)
def bot_count_hotels(message: Message) -> None:
    """Функция, запрашивающая у пользователя необходимость вывода фотографий"""
    if message.text.isdigit() and int(message.text) <= 20:
        bot.send_message(message.from_user.id, 'Спасибо, записал. '
                                               'Нужно выводить фотографии отеля? (Нажми "Да" или "Нет")',
                         reply_markup=answer())
        bot.set_state(message.from_user.id, UserInfoState.city_search, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as querystring:
            querystring['count_hotels'] = message.text

    elif message.text.isdigit() and int(message.text) > 20:
        bot.send_message(message.from_user.id, 'Количество отелей не должно превышать 20')
    else:
        bot.send_message(message.from_user.id, 'Количество отелей должно быть числом')


@bot.message_handler(state=UserInfoState.city_search)
def bot_search(message: Message) -> None:
    """Функция, которая ищет по api нужный город, и выводит информацию по самым дешевым отелям"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as querystring:
        querystring['need_for_photos'] = message.text

    request_1 = request_to_api("https://hotels4.p.rapidapi.com/locations/v2/search", querystring)
    pattern: str = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, request_1)

    if find:
        data: Dict = json.loads(f"{{{find[0]}}}")

        for dest_id in data['entities']:
            if dest_id['type'] == 'CITY' and dest_id['name'].lower() == querystring['query'].lower():
                querystring['destinationId'] = dest_id['destinationId']
                break

    if querystring.get('destinationId'):
        request_2 = request_to_api("https://hotels4.p.rapidapi.com/properties/list", querystring)
        pattern_2: str = r'(?<=,)"results":.+?(?=,"pagination")'
        find_2 = re.search(pattern_2, request_2)

        if find_2:
            data_2: Dict = json.loads(f"{{{find_2[0]}}}")
            result_search: List = [{'name': i_value.get('name', 'Нет'),
                                    'address': i_value.get('address', 'Нет').get('streetAddress', 'Нет'),
                                    'starRating': i_value.get('starRating', 'Нет'),
                                    'City center': i_value['landmarks'][0].get('distance', 'Нет'),
                                    'current': i_value.get('ratePlan', 'Нет').get('price', 'Нет').get('current',
                                                                                                      'Нет'),
                                    'exactCurrent': i_value.get('ratePlan', 'Нет').get('price', 'Нет').get(
                                        'exactCurrent', 'Нет'),
                                    'id': i_value.get('id', 'Нет')}
                                   for i_value in data_2['results']]
            result_search.sort(key=operator.itemgetter('exactCurrent'))
            querystring['results'] = result_search

            for i_value in result_search[:int(querystring['count_hotels'])]:
                answer: str = f'\nОтель: {i_value["name"]}\nАдрес: {i_value["address"]}\n ' \
                              f'Количество звезд: {i_value["starRating"]}\n ' \
                              f'Расстояние до центра: {i_value["City center"]}\nЦена: {i_value["current"]}\n'
                if message.text.lower() == 'нет':
                    bot.send_message(message.from_user.id, answer)
                bot.set_state(message.from_user.id, UserInfoState.no_state, message.chat.id)

            if message.text.lower() == 'да':
                bot.send_message(message.from_user.id, 'Сколько фотографий показать? (Не более 10)')
                bot.set_state(message.from_user.id, UserInfoState.photos, message.chat.id)
            elif message.text.lower() != 'да' and message.text.lower() != 'нет':
                bot.send_message(message.from_user.id, 'Выбери "Да" или "Нет"')


@bot.message_handler(state=UserInfoState.photos)  # Фото вывести у меня не получилось, нужна помощь(
def bot_search(message: Message) -> None:
    """Функция, которая выводит фотографии отелей"""

    with bot.retrieve_data(message.from_user.id, message.chat.id) as querystring:
        querystring['count_photos'] = message.text
    querystring_id: Dict = dict()

    if message.text.isdigit() and int(message.text) <= 10:

        for i_value in querystring['results'][:int(message.text)]:
            answer: str = f'\nОтель: {i_value["name"]}\nАдрес: {i_value["address"]}\n ' \
                          f'Количество звезд: {i_value["starRating"]}\n ' \
                          f'Расстояние до центра: {i_value["City center"]}\nЦена: {i_value["current"]}\n'
            querystring_id['id'] = i_value['id']
            request_3 = request_to_api("https://hotels4.p.rapidapi.com/properties/get-hotel-photos", querystring_id)
            data_3: Dict = json.loads(request_3)
            bot.send_message(message.from_user.id, answer)

            for i_photo in data_3['hotelImages'][:int(message.text)]:
                bot.send_photo(message.chat.id, i_photo['baseUrl'])
        bot.set_state(message.from_user.id, UserInfoState.no_state, message.chat.id)

    elif message.text.isdigit() and int(message.text) > 10:
        bot.send_message(message.from_user.id, 'Число фотографий не должно быть больше 10')
    else:
        bot.send_message(message.from_user.id, 'Введите количество фотографий')
