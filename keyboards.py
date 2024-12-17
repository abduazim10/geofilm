from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_all_categories,get_channel_info

def get_subscription_keyboard():
    # Получаем информацию о каналах
    channel_info = get_channel_info()
    if not channel_info:
        return None  # Если каналы не заданы, кнопки не создаются

    # Создаём клавиатуру
    markup = InlineKeyboardMarkup()
    number = 1
    # Проходим по всем каналам и создаем для каждого кнопку
    for channel_id, channel_url in channel_info:
        subscribe_button = InlineKeyboardButton(
            f"Подписаться на Канал {number}",  # Уникальный текст для каждого канала
            url=channel_url  # Используем URL из базы данных
            
        )
        number+=1
        markup.add(subscribe_button)

    # Кнопка проверки
    check_button = InlineKeyboardButton(
        text=f'✅Проверить', callback_data='check'
    )
    markup.add(check_button)

    return markup



admin_start_keyboards = ReplyKeyboardMarkup(resize_keyboard=True, 
    keyboard=[
        [KeyboardButton('🔍Искать фильм по Коду')],
        [KeyboardButton('Kino ✏️/➕'), KeyboardButton('Kino ochirish ❌')],
        [KeyboardButton('Kanal ✏️/➕'), KeyboardButton('Kanal ochirish ❌')],
        [KeyboardButton('Userlarga jonatish')]
])
user_start_keyboards = ReplyKeyboardMarkup(resize_keyboard=True, 
    keyboard=[
        [KeyboardButton('🔍Искать фильм по Коду'), KeyboardButton('🔍Искать фильм по Названию')],
        
])
def kino_keyboards():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    categories = get_all_categories()
    for category in categories:
        keyboard.add(KeyboardButton(category['name']))
    return keyboard


# def movie_keyboards(category_name):
#     # Получаем список фильмов из базы данных
#     movies = get_movies_by_category(category_name)
#     if not movies:
#         return False  # Если фильмов нет, возвращаем False
    
#     # Создаем клавиатуру
#     keyboard2 = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    
#     # Генерируем кнопки
#     buttons = [KeyboardButton(movie['name']) for movie in movies]  # Убедитесь, что `movie` содержит поле `name`
#     keyboard2.add(*buttons)

#     return keyboard2