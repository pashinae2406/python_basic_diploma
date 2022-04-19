from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date
from loader import bot
from states.requests import UserInfoState
from typing import Any
from telebot.types import Message, CallbackQuery


@bot.message_handler(state=UserInfoState.arrival_date)
def date_in(message: Message):
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()
    LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    bot.send_message(message.chat.id, f" Теперь выбери дату заезда: {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal1(call: CallbackQuery):
    result, key, step = DetailedTelegramCalendar(calendar_id=1).process(call.data)
    if not result and key:
        LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
        bot.edit_message_text(f"Календарь 1: Дата заезда: {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.send_message(call.message.chat.id, f"Дата заезда: {result}")

        with bot.retrieve_data(call.from_user.id) as querystring:
            querystring['date_in'] = call.data


@bot.message_handler(state=UserInfoState.departure_date)
def date_aut(message):
    calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=date.today()).build()
    bot.send_message(message.chat.id, f"{step}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal2(call: CallbackQuery):
    result, key, step = DetailedTelegramCalendar(calendar_id=2).process(call.data)
    if not result and key:
        LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
        bot.edit_message_text(f"Календарь 2: Дата выезда: {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.send_message(call.message.chat.id, f"Дата выезда: {result}")

        with bot.retrieve_data(call.from_user.id) as querystring:
            querystring['date_aut'] = call.data

