from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    check_in = State()
    check_out = State()
    city = State()
    count_hotels = State()
    city_search = State()
    photos = State()
    arrival_date = State()
    departure_date = State()
    no_state = None
