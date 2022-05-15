from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def ranges_price() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('до 50'))
    keyboard.add(KeyboardButton('50-80'))
    keyboard.add(KeyboardButton('80-100'))
    keyboard.add(KeyboardButton('100-150'))
    keyboard.add(KeyboardButton('свыше 150'))
    return keyboard
