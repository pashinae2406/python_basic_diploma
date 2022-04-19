from typing import List
from telebot.types import Message
from telebot import types
from loader import bot
from datetime import date, timedelta
from states.requests import UserInfoState
from keyboards.сalendar.dates import get_calendar, ALL_STEPS
from keyboards.reply.answer_no_yes import answer
from rapid_api.search_city import search_city
from rapid_api.search_hotel import search_hotel
from rapid_api.photos import search_photos

"""Команда для поиска топ самых дорогих отелей в выбранном городе"""


@bot.message_handler(commands=['highprice'])
def calendar_command(message: Message) -> None:
    """Функция, запрашивающая у пользователя даты заезда и выезда"""
    calendar, step = get_calendar(calendar_id=1,
                                  min_date=date.today(),
                                  max_date=date.today() + timedelta(days=365),
                                  locale="ru",
                                  )

    bot.set_state(message.from_user.id, UserInfoState.check_in, message.chat.id)
    bot.send_message(message.from_user.id, f"Привет! Тебя приветствует Телеграмм-бот по поиску самых дорогих отелей! \n"
                                           f"Давай выберем дату заезда: \n"
                                           f"Выбери {ALL_STEPS[step]}", reply_markup=calendar)


@bot.message_handler(state=UserInfoState.city)
def highprice(message: Message) -> None:
    """Функция, запрашивающая у пользователя город для поиска отелей"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['query'] = message.text
    bot.set_state(message.from_user.id, UserInfoState.count_hotels, message.chat.id)
    bot.send_message(message.from_user.id, "Спасибо, записал. Сколько отелей показать (не более 10)?")


@bot.message_handler(state=UserInfoState.count_hotels)
def bot_count_hotels(message: Message) -> None:
    """Функция, запрашивающая у пользователя необходимость вывода фотографий"""

    if message.text.isdigit() and int(message.text) <= 10:
        bot.send_message(message.from_user.id, 'Спасибо, записал. '
                                               'Нужно выводить фотографии отеля? (Нажми "Да" или "Нет")',
                         reply_markup=answer())
        bot.set_state(message.from_user.id, UserInfoState.city_search, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count_hotels'] = message.text

    elif message.text.isdigit() and int(message.text) > 10:
        bot.send_message(message.from_user.id, 'Количество отелей не должно превышать 10')
    else:
        bot.send_message(message.from_user.id, 'Количество отелей должно быть числом')


@bot.message_handler(state=UserInfoState.city_search)
def bot_search(message: Message) -> None:
    """Функция вывода информации по самым дорогим отелям"""

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['need_for_photos'] = message.text

    try:
        if message.text.lower() == 'да':
            bot.send_message(message.from_user.id, 'Сколько фотографий показать? (Не более 5)')
            bot.set_state(message.from_user.id, UserInfoState.photos, message.chat.id)
        elif message.text.lower() == 'нет':
            result: List = search_hotel(search_city(data['query']), data)
            for i_res in result[
                         -int(data['count_hotels']):]:  # Не понимаю, почему ответы все равно выводятся с начала списка
                bot.send_message(message.from_user.id, i_res['answer'])
            bot.set_state(message.from_user.id, UserInfoState.no_state, message.chat.id)
        else:
            bot.send_message(message.from_user.id, 'Выбери "Да" или "Нет"')
    except KeyError:
        print()


@bot.message_handler(state=UserInfoState.photos)
def bot_search(message: Message) -> None:
    """Функция, которая выводит фотографии отелей"""

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photos'] = message.text

    if message.text.isdigit() and int(message.text) <= 5:
        result: List = search_photos(search_hotel(search_city(data['query']),
                                                  data), int(message.text))

        try:
            for i_res in result[-int(data['count_hotels']):]:
                bot.send_message(message.from_user.id, i_res['answer'])
                media = [types.InputMediaPhoto(media=i_photo) for i_photo in i_res['photos']]
                bot.send_media_group(chat_id=message.chat.id, media=media)
        except KeyError:
            print()

        bot.set_state(message.from_user.id, UserInfoState.no_state, message.chat.id)

    elif message.text.isdigit() and int(message.text) > 5:
        bot.send_message(message.from_user.id, 'Число фотографий не должно быть больше 5')
    else:
        bot.send_message(message.from_user.id, 'Введите количество фотографий')
