from aiogram.dispatcher.filters.state import StatesGroup, State

class kinostate(StatesGroup):
    name = State()
    janr = State()
    category = State()
    yil = State()
    age = State()
    rating = State()
    video = State()

class searchkino(StatesGroup):
    id = State()
    nomi = State()

class deletekino(StatesGroup):
    id = State()

class BroadcastState(StatesGroup):
    number = State()
    text = State()
    image = State()

class kanaladd(StatesGroup):
    channel_id = State()
    channel_url = State()