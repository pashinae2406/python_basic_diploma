from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def ranges_dinst() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('до 5'))
    keyboard.add(KeyboardButton('5-10'))
    keyboard.add(KeyboardButton('10-15'))
    keyboard.add(KeyboardButton('15-20'))
    keyboard.add(KeyboardButton('свыше 20'))
    return keyboard