from typing import List
from telebot.types import Message
from loader import bot
from states.requests import UserInfoState
from keyboards.сalendar.dates import date_in, date_aut
from keyboards.reply.answer_no_yes import answer
from rapid_api.search_city import search_city
from rapid_api.search_hotel import search_hotel
from rapid_api.photos import search_photos

"""Команда для поиска топ самых дешевых и самых дорогих отелей в выбранном городе"""


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    """Функция, запрашивающая у пользователя город для поиска отелей"""
    bot.set_state(message.from_user.id, UserInfoState.arrival_date, message.chat.id)
    bot.send_message(message.from_user.id, "В каком городе будем искать отели?")


@bot.message_handler(state=UserInfoState.arrival_date)
def arrival(message: Message) -> None:
    """Функция, запрашивающая у пользователя дату заезда"""

    with bot.retrieve_data(message.from_user.id, message.chat.id) as querystring:
        querystring['query'] = message.text
    date_in(message)
    bot.set_state(message.from_user.id, UserInfoState.departure_date, message.chat.id)


@bot.message_handler(state=UserInfoState.departure_date)
def departure(message: Message) -> None:
    """Функция, запрашивающаю у пользователя дату выезда"""

    date_aut(message)
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)


@bot.message_handler(state=UserInfoState.city)
def bot_city(message: Message) -> None:
    """Функция запрашивающая у пользователя количество отелей для вывода"""

    bot.send_message(message.from_user.id, 'Спасибо, записал. Сколько отелей показать (не более 20)?')
    bot.set_state(message.from_user.id, UserInfoState.count_hotels, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as querystring:
        querystring['check_aut'] = message.text
        print(querystring)


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
    """Функция вывода информации по самым дешевым отелям"""

    with bot.retrieve_data(message.from_user.id, message.chat.id) as querystring:
        querystring['need_for_photos'] = message.text

    if message.text.lower() == 'да':
        bot.send_message(message.from_user.id, 'Сколько фотографий показать? (Не более 10)')
        bot.set_state(message.from_user.id, UserInfoState.photos, message.chat.id)
    elif message.text.lower() == 'нет':
        result: List = search_hotel(search_city(querystring['query']), int(querystring['count_hotels']))
        for i_res in result:
            bot.send_message(message.from_user.id, i_res['answer'])
        bot.set_state(message.from_user.id, UserInfoState.no_state, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Выбери "Да" или "Нет"')


@bot.message_handler(state=UserInfoState.photos)
def bot_search(message: Message) -> None:
    """Функция, которая выводит фотографии отелей"""

    with bot.retrieve_data(message.from_user.id, message.chat.id) as querystring:
        querystring['count_photos'] = message.text

    if message.text.isdigit() and int(message.text) <= 10:
        result: List = search_photos(search_hotel(search_city(querystring['query']),
                                                  int(querystring['count_hotels'])), int(message.text))
        for i_res in result:
            bot.send_message(message.from_user.id, i_res['answer'])

            for i_jmg in i_res['photos']:
                bot.send_photo(message.chat.id, i_jmg)

        bot.set_state(message.from_user.id, UserInfoState.no_state, message.chat.id)

    elif message.text.isdigit() and int(message.text) > 10:
        bot.send_message(message.from_user.id, 'Число фотографий не должно быть больше 10')
    else:
        bot.send_message(message.from_user.id, 'Введите количество фотографий')
