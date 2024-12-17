import logging
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentType
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import get_subscription_keyboard, admin_start_keyboards, kino_keyboards, user_start_keyboards
from database import create_db,is_user_registered,register_user, get_c_id_by_name, add_new_kino ,search_kino_by_id, get_users,del_kino_from_id,search_kino_by_name,is_admin ,add_channel,get_channel_info,del_channel
from state import kinostate, searchkino , BroadcastState , deletekino,kanaladd
from aiogram.dispatcher.filters import Text

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

def check_is_admin(user_id):
    return is_admin(user_id)
    
async def on_startup(dp):
    create_db()
    logging.info("Database initialized successfully.")
    



@dp.message_handler(commands=['start'])
async def subscribe_not(message: types.Message):
    user_id = message.from_user.id

    # Получаем информацию о каналах
    channel_info = get_channel_info()
    if not channel_info:
        await message.answer("Информация о канале недоступна. Обратитесь к администратору.")
        return

    # Переменная для проверки, подписан ли пользователь на все каналы
    all_subscribed = True
    subscription_keyboard = None

    # Проверяем подписку на все каналы
    for channel_id, channel_url in channel_info:
        try:
            member_status = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member_status.status not in ['member', 'creator', 'administrator']:
                all_subscribed = False
                if not subscription_keyboard:
                    subscription_keyboard = get_subscription_keyboard()  # Если кнопка ещё не создана
        except Exception as e:
            logging.error(f"Ошибка проверки подписки на канал {channel_id}: {e}")
            all_subscribed = False

    if check_is_admin(user_id):
        await message.answer("Добро пожаловать, администратор!", reply_markup=admin_start_keyboards)
    elif all_subscribed:
        if is_user_registered(user_id):
            await message.answer(
                text=f"👋 Здравствуйте, {message.from_user.full_name}!\nДобро пожаловать в Geofilm🎥",
                reply_markup=user_start_keyboards
            )
        else:
            register_user(user_id, message.from_user.username or "Неизвестно")
            await message.answer(
                text=f"👋 Здравствуйте, {message.from_user.full_name}!\nВы зарегистрированы в Geofilm🎥",
                reply_markup=user_start_keyboards
            )
    else:
        if subscription_keyboard:
            await message.answer(
                text=f"Чтобы пользоваться ботом Geofilm🎥, подпишитесь на все каналы.",
                parse_mode="Markdown",
                reply_markup=subscription_keyboard
            )
        else:
            await message.answer("Клавиатура для подписки недоступна. Обратитесь к администратору.")

@dp.message_handler(commands=['help'])
async def subscribe_not(message: types.Message):
    await message.answer(f"👋 Здравствуйте, {message.from_user.full_name}!\n❔Хотите задать вопрос или вам нужна помощь — обратитесь к @Az1zov1ch_A")
    
@dp.message_handler(commands=['info'])
async def subscribe_not(message: types.Message):
    await message.answer(f"👋 Здравствуйте, {message.from_user.full_name}!\nДобро пожаловать в Geofilm🎥\n🎥 GeoFilm — бесплатный бот для поиска и просмотра фильмов по названию или коду")

@dp.callback_query_handler(lambda c: c.data == "check")
async def process_callback_check(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or "Неизвестно"
    subscription_keyboard = get_subscription_keyboard()
    channel_info = get_channel_info()

    # Переменная для проверки подписки на все каналы
    all_subscribed = True

    for channel_id, channel_url in channel_info:
        try:
            is_channel_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if is_channel_member.status not in ['member', 'creator']:
                all_subscribed = False
        except Exception as e:
            logging.error(f"Ошибка проверки подписки на канал {channel_id}: {e}")
            all_subscribed = False

    # Проверяем, является ли пользователь администратором
    if check_is_admin(callback_query.from_user.id):
        await callback_query.message.answer(
            'Admin akkauntga xush kelbsiz', 
            reply_markup=admin_start_keyboards
        )
    elif all_subscribed:
        # Проверяем, зарегистрирован ли пользователь
        if is_user_registered(user_id):
            await callback_query.message.answer(
                text=f"👋 Здравствуйте {callback_query.from_user.full_name}\nДобро пожаловать в наш бот Geofilm🎥", reply_markup=user_start_keyboards
            )
        else:
            register_user(user_id, username)
            await callback_query.message.answer(
                text=f"👋 Здравствуйте {callback_query.from_user.full_name}\nДобро пожаловать в наш бот Geofilm🎥", reply_markup=user_start_keyboards
            )
    else:
        # Если не подписан на все каналы
        await callback_query.message.answer(
            text="Вы не подписались на все каналы", 
            reply_markup=subscription_keyboard  # Здесь должен быть ваш InlineKeyboardMarkup
        )


@dp.message_handler(lambda message: message.text == 'Kanal ✏️/➕')
async def add_kino(message: types.Message):
    if check_is_admin(message.from_user.id):
        await message.answer("Kanal idsini kiriting:")
        await kanaladd.channel_id.set()

@dp.message_handler(state=kanaladd.channel_id)
async def save_category(message: types.Message, state):
    await state.update_data(channel_id=message.text)
    await message.answer('Kanal urlni kiriting:')
    await kanaladd.next()

@dp.message_handler(state=kanaladd.channel_url)
async def save_rating(message: types.Message, state: FSMContext):
    await state.update_data(channel_url = message.text)
    user_data = await state.get_data()
    add_channel(channel_id=user_data["channel_id"], url=user_data["channel_url"])
    await state.finish()
    await message.answer("Kanal qoshildi!", reply_markup=admin_start_keyboards)

@dp.message_handler(lambda message: message.text =='Kanal ochirish ❌')
async def delete_kino(message: types.Message):
    if check_is_admin(message.from_user.id):
        await message.answer("Kanalni id sini yuboring!")
        await deletekino.id.set()

@dp.message_handler(state=deletekino.id)
async def save_category(message: types.Message, state):
    channel_id = message.text
    await state.update_data(id = message.text)
    del_channel(id=channel_id)
    await message.answer("kanal ochirildi!")
    user_data = await state.get_data()
    await state.finish()
    

@dp.message_handler(lambda message: message.text == 'Kino ✏️/➕')
async def add_kino(message: types.Message):
    if check_is_admin(message.from_user.id):
        await message.answer("Kino nomini kiriting:")
        await kinostate.name.set()

@dp.message_handler(state=kinostate.name)
async def save_category(message: types.Message, state):
    await state.update_data(name=message.text)
    await message.answer('Kino janrini kiriting:')
    await kinostate.next()

@dp.message_handler(state=kinostate.janr)
async def save_category(message: types.Message, state):
    await state.update_data(janr = message.text)
    await message.answer('Kino categorysini kiriting:' , reply_markup=kino_keyboards())
    await kinostate.next()

@dp.message_handler(state=kinostate.category)
async def save_category(message: types.Message, state: FSMContext):
    c_id = get_c_id_by_name(message.text)
    if c_id:
        await state.update_data(category=c_id)
        await message.answer("Film chiqarilgan yilni kiriting:")
        await kinostate.next()
    else:
        await message.answer("Kategoriya topilmadi!")

@dp.message_handler(state=kinostate.yil)
async def save_year(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Yilni to'g'ri kiriting (raqam bo'lishi kerak).")
        return
    await state.update_data(yil=int(message.text))
    await message.answer("Filmning yosh chegarasini kiriting (masalan, 16+):")
    await kinostate.next()

@dp.message_handler(state=kinostate.age)
async def save_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Filmning reytingini kiriting (masalan, 8.5):")
    await kinostate.next()

@dp.message_handler(state=kinostate.rating)
async def save_rating(message: types.Message, state: FSMContext):
    await state.update_data(rating=message.text)
    await message.answer("Filmni yuklang (video):")
    await kinostate.next()

@dp.message_handler(content_types=ContentType.VIDEO, state=kinostate.video)
async def save_video(message: Message, state: FSMContext):
    await state.update_data(video=message.video.file_id)
    user_data = await state.get_data()
    add_new_kino(
        user_data['name'], user_data['janr'], user_data['category'], user_data['video'],
        user_data['yil'], user_data['age'], user_data['rating']
    )
    await state.finish()
    await message.answer("Film muvaffaqiyatli qo'shildi!", reply_markup=admin_start_keyboards)

@dp.message_handler(lambda message: message.text == '🔍Искать фильм по Коду')
async def search_kino_by_code(message: types.Message):
    user_id = message.from_user.id
    channel_info = get_channel_info()
    all_subscribed = True
    subscription_keyboard = get_subscription_keyboard()

    for channel_id, channel_url in channel_info:
        try:
            member_status = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member_status.status not in ['member', 'creator', 'administrator']:
                all_subscribed = False
        except Exception as e:
            logging.error(f"Ошибка проверки подписки на канал {channel_id}: {e}")
            all_subscribed = False

    if all_subscribed:
        await message.reply('🎥 Напишите код фильма или сериала.\nЕсли вы не знаете код, загляните на наш канал — там вы найдете всю информацию!')
        await searchkino.id.set()
    else:
        await message.answer("Чтобы пользоваться функцией поиска, подпишитесь на все каналы.", 
                             reply_markup=subscription_keyboard)


@dp.message_handler(state=searchkino.id)
async def save_category(message: types.Message, state):
    kino = search_kino_by_id(message.text)
    if kino:
        await message.answer_video(
            kino['video'],  # file_id видео
            caption = f"<b>Название:</b> {kino['name']}\n<b>Жанр:</b> {kino['janr']}\n<b>Дата выхода:</b> {kino['yil']}год\n<b>Возраст:</b> {kino['age']}\n<b>Рейтинг:</b> {kino['rating']}",  # Текст в одном сообщении с видео
            parse_mode="HTML",
        )
    else:
        await message.answer("Фильм не найден!")
    await state.update_data(id=message.text)
    user_data = await state.get_data()
    await state.finish()

@dp.message_handler(lambda message: message.text == '🔍Искать фильм по Названию')
async def search_kino_by_name_function(message: types.Message):
    user_id = message.from_user.id
    channel_info = get_channel_info()
    all_subscribed = True
    subscription_keyboard = get_subscription_keyboard()

    for channel_id, channel_url in channel_info:
        try:
            member_status = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member_status.status not in ['member', 'creator', 'administrator']:
                all_subscribed = False
        except Exception as e:
            logging.error(f"Ошибка проверки подписки на канал {channel_id}: {e}")
            all_subscribed = False

    if all_subscribed:
        await message.reply('🎥 Напишите название фильма или сериала.\nЕсли вы не знаете название, загляните на наш канал @geofilm_ru — там вы найдете всю информацию!')
        await searchkino.nomi.set()
    else:
        await message.answer("Чтобы пользоваться функцией поиска, подпишитесь на все каналы.", 
                             reply_markup=subscription_keyboard)


@dp.message_handler(state=searchkino.nomi)
async def save_category(message: types.Message, state):
    kino = search_kino_by_name(message.text)
    if kino:
        await message.answer_video(
            kino['video'],  # file_id видео
            caption = f"<b>Название:</b> {kino['name']}\n<b>Жанр:</b> {kino['janr']}\n<b>Дата выхода:</b> {kino['yil']}год\n<b>Возраст:</b> {kino['age']}\n<b>Рейтинг:</b> {kino['rating']}",  # Текст в одном сообщении с видео
            parse_mode="HTML",
        )
    else:
        await message.answer("Фильм не найден!")
    await state.finish()

@dp.message_handler(Text('Userlarga jonatish'))
async def start_broadcast(message: types.Message):
    if check_is_admin(message.from_user.id):
        await message.answer("Nechta odamga yuborishni xohlaysiz?")
        await BroadcastState.number.set()


@dp.message_handler(state=BroadcastState.number)
async def ask_text(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Faqat raqam kiriting!")
        return
    await state.update_data(number=int(message.text))
    await message.answer("Yuboriladigan matnni yuboring:")
    await BroadcastState.text.set()


@dp.message_handler(state=BroadcastState.text)
async def ask_image(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Rasmni yuboring yoki yubormasangiz, 'Yo'q' deb yozing.")
    await BroadcastState.image.set()

@dp.message_handler(state=BroadcastState.image, content_types=types.ContentType.ANY)
async def send_to_users(message: types.Message, state: FSMContext):
    data = await state.get_data()
    number = data['number']
    text = data['text']
    image = message.photo[-1].file_id if message.photo else None

    # Foydalanuvchilarni olish
    users = get_users(limit=number)

    count = 0
    for user_id in users:
        try:
            if image:
                await bot.send_photo(user_id, photo=image, caption=text)
            else:
                await bot.send_message(user_id, text)
            count += 1
        except Exception:
            continue  # Agar user bloklagan bo'lsa, xatolikni o'tkazib yuboradi.

    await message.answer(f"{count} ta foydalanuvchiga muvaffaqiyatli yuborildi!")
    await state.finish()


@dp.message_handler(lambda message: message.text =='Kino ochirish ❌')
async def delete_kino(message: types.Message):
    if check_is_admin(message.from_user.id):
        await message.answer("Kinoni ochirish uchun kino kodini kiriting!")
        await deletekino.id.set()

@dp.message_handler(state=deletekino.id)
async def save_category(message: types.Message, state):
    kino_id = message.text

    # Kino mavjudligini tekshirish
    kino = search_kino_by_id(kino_id)
    if not kino:
        await message.answer("Bunday IDga ega kino topilmadi. Qayta tekshiring!")
        await state.finish()
        return

    # Kinoni o'chirish
    del_kino_from_id(kino_id)

    # Tasdiqlash
    kino_check = search_kino_by_id(kino_id)
    if not kino_check:
        await message.answer(f"Kino (ID: {kino_id}) muvaffaqiyatli o'chirildi!")
    else:
        await message.answer(f"Kino (ID: {kino_id}) o'chirib bo'lmadi. Qayta urinib ko'ring!")

    await state.finish()






   





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)