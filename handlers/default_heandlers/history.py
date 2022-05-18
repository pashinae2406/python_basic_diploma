from telebot.types import Message
from loader import bot
import os


@bot.message_handler(commands=['history'])
def bot_history(message: Message) -> None:

    path = os.path.abspath(os.path.join('history.txt'))
    request_history = ''

    with open(path, 'r', encoding='utf-8') as file:
        for i_request in file:
            request_history += i_request

    bot.reply_to(message, request_history)
