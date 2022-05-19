from typing import List
from telebot.types import Message
from telebot import types
from loader import bot
from datetime import date, timedelta, datetime
from states.requests import UserInfoState
from keyboards.сalendar.dates import get_calendar, ALL_STEPS
from keyboards.reply.answer_no_yes import answer
from keyboards.reply.price_range import ranges_price
from rapid_api.search_city import search_city
from rapid_api.search_hotel import search_hotel
from rapid_api.photos import search_photos
from telebot.apihelper import ApiTelegramException
from database.request_history import db, user


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def calendar_command(message: Message) -> None:
    """Функция, запрашивающая у пользователя даты заезда и выезда"""

    calendar, step = get_calendar(calendar_id=1,
                                  min_date=date.today(),
                                  max_date=date.today() + timedelta(days=365),
                                  locale="ru",
                                  )

    bot.set_state(message.from_user.id, UserInfoState.check_in, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['commands'] = message.text

    bot.send_message(message.from_user.id, f"Привет! Тебя приветствует Телеграмм-бот по поиску отелей!\n"
                                           f"Давай выберем дату заезда:\n"
                                           f"Выбери {ALL_STEPS[step]}", reply_markup=calendar)


@bot.message_handler(state=UserInfoState.city)
def bot_city(message: Message) -> None:
    """Функция, запрашивающая у пользователя город для поиска отелей"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['query'] = message.text
    bot.set_state(message.from_user.id, UserInfoState.count_hotels, message.chat.id)
    bot.send_message(message.from_user.id, "Спасибо, записал. Сколько отелей показать (не более 10)?")


@bot.message_handler(state=UserInfoState.count_hotels)
def bot_count_hotels(message: Message) -> None:
    """Функция, запрашивающая у пользователя необходимость вывода фотографий"""

    if message.text.isdigit() and int(message.text) <= 10:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count_hotels'] = message.text

        if data['commands'] == '/lowprice' or data['commands'] == '/highprice':
            bot.send_message(message.from_user.id, 'Спасибо, записал.\n'
                                                   'Выводить фотографии отеля? (Нажми "Да" или "Нет")',
                             reply_markup=answer())
            bot.set_state(message.from_user.id, UserInfoState.city_search, message.chat.id)
        elif data['commands'] == '/bestdeal':
            bot.send_message(message.from_user.id, 'Выбери диапазон цен: ',
                             reply_markup=ranges_price())
            bot.set_state(message.from_user.id, UserInfoState.price_range, message.chat.id)

    elif message.text.isdigit() and int(message.text) > 10:
        bot.send_message(message.from_user.id, 'Количество отелей не должно превышать 10')
    else:
        bot.send_message(message.from_user.id, 'Количество отелей должно быть числом')


@bot.message_handler(state=UserInfoState.city_search)
def bot_search(message: Message) -> None:
    """Функция вывода информации по отелям"""

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['need_for_photos'] = message.text

        hotels: List = list()
        if message.text.lower() == 'да':
            bot.send_message(message.from_user.id, 'Сколько фотографий показать? (Не более 5)')
            bot.set_state(message.from_user.id, UserInfoState.photos, message.chat.id)
        elif message.text.lower() == 'нет':
            result: List = search_hotel(search_city(data['query']), data)
            if result:
                for i_res in result:
                    hotels.append(i_res['name'])
                    bot.send_message(message.from_user.id, i_res.get('answer'),
                                     disable_web_page_preview=True)

            else:
                bot.send_message(message.from_user.id, 'По заданным параметрам ничего не найдено.\n'
                                                       'Попробуйте еще раз, выберите нужную команду.')
                hotels = ['По заданным параметрам ничего не найдено']

            user.create_table()
            with db:
                user.create(command=data['commands'], telegram_id=message.from_user.id,
                            date_time=datetime.now(), city=data['query'], hotels=hotels)
            bot.set_state(message.from_user.id, UserInfoState.no_state, message.chat.id)
        else:
            bot.send_message(message.from_user.id, 'Выбери "Да" или "Нет"')


@bot.message_handler(state=UserInfoState.photos)
def bot_search(message: Message) -> None:
    """Функция, которая выводит фотографии отелей"""

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photos'] = int(message.text)

    hotels: List = list()
    if message.text.isdigit() and int(message.text) <= 5:
        result: List = search_photos(search_hotel(search_city(data['query']),
                                                  data))
        bot.set_state(message.from_user.id, UserInfoState.no_state, message.chat.id)

        if result:

            for i_res in result:
                hotels.append(i_res['name'])
                media = [types.InputMediaPhoto(i_res['photos'][i_photo], caption=i_res.get('answer'))
                         if i_photo == 0 else types.InputMediaPhoto(i_res['photos'][i_photo])
                         for i_photo in range(len(i_res['photos'][:data['count_photos']]))]
                try:
                    bot.send_media_group(chat_id=message.chat.id, media=media)
                except ApiTelegramException:
                    bot.send_photo(message.from_user.id,
                                   'https://go.skillbox.ru/media/files/'
                                   'ba09b8e3-e01b-4a15-b361-3c5b88f5b876/1648452936327.png',
                                   caption=i_res.get('answer'))

        else:
            bot.send_message(message.from_user.id, 'По заданным параметрам ничего не найдено.\n'
                                                   'Попробуйте еще раз, выберите нужную команду.')
            hotels = ['По заданным параметрам ничего не найдено']
    elif message.text.isdigit() and int(message.text) > 5:
        bot.send_message(message.from_user.id, 'Число фотографий не должно быть больше 5')
    else:
        bot.send_message(message.from_user.id, 'Введите количество фотографий')

    user.create_table()
    with db:
        user.create(command=data['commands'], telegram_id=message.from_user.id,
                    date_time=datetime.now(), city=data['query'], hotels=hotels)
