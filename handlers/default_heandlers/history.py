from telebot.types import Message
from loader import bot
from database.request_history import db, User
from loguru import logger


@logger.catch()
@bot.message_handler(commands=['history'])
def bot_history(message: Message) -> None:
    with db:
        history_list = User.select().where(User.telegram_id == message.from_user.id)
        request_history = ''
        for i_request in history_list:
            request_history += (f'Комманда: {i_request.command}\n'
                                f'Дата и время ввода команды: {i_request.date_time}\n'
                                f'Город: {i_request.city.title()}\nНайденные отели: ')
            for i_hotel in i_request.hotels[1:-1].split(', '):
                request_history += f'{i_hotel[1:-1]}\n                 '
            request_history += '\n======================================================\n'

    bot.reply_to(message, request_history)
