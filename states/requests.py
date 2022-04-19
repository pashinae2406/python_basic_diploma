from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    city = State()
    count_hotels = State()
    city_search = State()
    photos = State()
    arrival_date = State()
    departure_date = State()
    no_state = None
