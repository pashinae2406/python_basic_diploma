from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date, timedelta
from loader import bot
from states.requests import UserInfoState
from telebot.types import CallbackQuery


def get_calendar(is_process=False, callback_data=None, **kwargs):
    if is_process:
        result, key, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                     current_date=kwargs.get('current_date'),
                                                     min_date=kwargs['min_date'],
                                                     max_date=kwargs['max_date'],
                                                     locale=kwargs['locale']).process(callback_data.data)
        return result, key, step
    else:
        calendar, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                  current_date=kwargs.get('current_date'),
                                                  min_date=kwargs['min_date'],
                                                  max_date=kwargs['max_date'],
                                                  locale=kwargs['locale']).build()
        return calendar, step


ALL_STEPS = {'y': 'год', 'm': 'месяц', 'd': 'день'}


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def handle_arrival_date(call: CallbackQuery):
    today = date.today()
    result, key, step = get_calendar(calendar_id=1,
                                     current_date=today,
                                     min_date=today,
                                     max_date=today + timedelta(days=365),
                                     locale="ru",
                                     is_process=True,
                                     callback_data=call)
    if not result and key:

        bot.edit_message_text(f"Выбери {ALL_STEPS[step]}",
                              call.from_user.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_in'] = result

            bot.edit_message_text(f"Дата заезда {result}",
                                  call.message.chat.id,
                                  call.message.message_id)

            bot.send_message(call.from_user.id, "Теперь выбери дату выезда")
            calendar, step = get_calendar(calendar_id=2,
                                          min_date=result + timedelta(days=1),
                                          max_date=result + timedelta(days=365),
                                          locale="ru",
                                          )

            bot.send_message(call.from_user.id,
                             f"Выбери {ALL_STEPS[step]}",
                             reply_markup=calendar)

            bot.set_state(call.from_user.id, UserInfoState.check_out, call.message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def handle_arrival_date(call: CallbackQuery):
    today = date.today()
    result, key, step = get_calendar(calendar_id=2,
                                     current_date=today,
                                     min_date=today + timedelta(days=1),
                                     max_date=today + timedelta(days=365),
                                     locale="ru",
                                     is_process=True,
                                     callback_data=call
                                     )

    if not result and key:
        bot.edit_message_text(f"Выбери {ALL_STEPS[step]}",
                              call.from_user.id,
                              call.message.message_id,
                              reply_markup=key)

    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_out'] = result
            data['count_days'] = data['check_out'] - data['check_in']

            bot.edit_message_text(f"Дата выезда {result}",
                                  call.message.chat.id,
                                  call.message.message_id)

        bot.set_state(call.from_user.id, UserInfoState.city, call.message.chat.id)
        bot.send_message(call.from_user.id, "В каком городе будем искать отели?")
