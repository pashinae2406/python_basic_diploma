import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('hello_world', "Вывести сообщение 'Привет, мир!'"),
    ('lowprice', "Поиск топ самых дешёвых отелей в городе"),
    ('highprice', "Поиск топ самых дорогих отелей в городе"),
    ('bestdeal', "Поиск топ отелей, наиболее подходящих по цене и расположению от центра"),
    ('history', "Вывести историю поиска отелей")
)
