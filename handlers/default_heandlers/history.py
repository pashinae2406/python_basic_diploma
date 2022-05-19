from telebot.types import Message
from loader import bot
import sqlite3


@bot.message_handler(commands=['history'])
def bot_history(message: Message) -> None:

    request_history = ''
    con = sqlite3.connect('people.db')
    cur = con.cursor()
    history_list = cur.execute(f"SELECT * FROM user WHERE telegram_id = {message.from_user.id}").fetchall()

    for i_request in history_list:
        request_history += f'Комманда: {i_request[1]}\nДата и время ввода команды: {i_request[3]}\n' \
                                          f'Город: {i_request[4].title()}\nНайденные отели: '

        for i_hotel in i_request[5][1:-1].split(', '):
            request_history += f'{i_hotel[1:-1]}\n                 '
        request_history += '\n======================================================\n'

    bot.reply_to(message, request_history)
