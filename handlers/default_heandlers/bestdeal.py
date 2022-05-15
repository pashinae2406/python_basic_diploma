from telebot.types import Message
from loader import bot
from states.requests import UserInfoState
from keyboards.reply.answer_no_yes import answer
from keyboards.reply.distance_range import ranges_dinst


@bot.message_handler(state=UserInfoState.price_range)
def bot_range(message: Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if message.text.split(' ')[0] == 'до':
            data['min_price'] = 0
            data['max_price'] = int(message.text.split(' ')[1])
        elif message.text.split(' ')[0] == 'свыше':
            data['min_price'] = int(message.text.split(' ')[1])
            data['max_price'] = 9999
        else:
            data['min_price'] = int(message.text.split('-')[0])
            data['max_price'] = int(message.text.split('-')[1])

    bot.send_message(message.from_user.id, 'Теперь выбери диапазон расстояний удаленности от центра: ',
                     reply_markup=ranges_dinst())
    bot.set_state(message.from_user.id, UserInfoState.distance_range, message.chat.id)


@bot.message_handler(state=UserInfoState.distance_range)
def bot_range(message: Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if message.text.split(' ')[0] == 'до':
            data['min_distance'] = 0
            data['max_distance'] = int(message.text.split(' ')[1])
        elif message.text.split(' ')[0] == 'свыше':
            data['min_distance'] = int(message.text.split(' ')[1])
            data['max_distance'] = 9999
        else:
            data['min_distance'] = int(message.text.split('-')[0])
            data['max_distance'] = int(message.text.split('-')[1])

    bot.send_message(message.from_user.id, 'Спасибо, записал.\n'
                                           'Выводить фотографии отеля? (Нажми "Да" или "Нет")',
                     reply_markup=answer())
    bot.set_state(message.from_user.id, UserInfoState.city_search, message.chat.id)
