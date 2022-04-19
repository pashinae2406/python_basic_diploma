from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    city = State()
    count_hotels = State()
    city_search = State()
    photos = State()
    no_state = None
