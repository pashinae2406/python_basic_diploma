from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    check_in = State()
    check_out = State()
    city = State()
    count_hotels = State()
    city_search = State()
    price_range = State()
    distance_range = State()
    photos = State()
    no_state = None
