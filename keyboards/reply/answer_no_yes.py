from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def answer() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('Нет'))
    keyboard.add(KeyboardButton('Да'))
    return keyboard
