from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['hello_world'])
def bot_hello_world(message: Message):
    bot.reply_to(message, "Привет, мир!")
