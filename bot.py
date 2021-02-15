import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup



token = ''

start_message = """
👋Добро пожаловать, {}
Подайте заявку чтобы присоединиться к
"""


request_accept = """
✅ Вы были успешно приняты. ✅

Наш бот: @favoritbet_bot

Наш чат: https://t.me/joinchat/H_wdJZFnXvpEtIMd

Канал с выплатами: https://t.me/joinchat/WK3mfuS_jc2ssEah
"""


accept_message = """
⛔️ Правилами запрещено:
✖️Использовать свои кошельки для приёма платежей.
✖️Пытаться обмануть администрацию в разных аспектах
✖️Неадекватное поведение
✖️Реклама сторонних проектов/услуг
✖️Попрошайничество
✖️Распространение запрещённых материалов
✖️Дизинформация о проектах
✖️Отправка гифок, стикеров, фотографий, видео 18+, c: шокирующем контентом
"""

request_message = """
Активная заявка 📱
Узнали от/в: {0}
Опыт работы: {1}
Готовы уделять время: {2}
ID воркера: {3}
"""


main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('📝Подать заявку')).add(types.KeyboardButton('⚙️Отмена'))

cancel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('⚙️Отмена'))

accept_button = types.InlineKeyboardButton('Принять', callback_data='accept_user')

reject_button = types.InlineKeyboardButton('Отклонить', callback_data='reject_user')

accept_keyboard = types.InlineKeyboardMarkup().add(accept_button).add(reject_button)

bot = Bot(token=token)

dp = Dispatcher(bot, storage=MemoryStorage())


admin = 1412541991




class request_user(StatesGroup):
    info = State()
    exp = State()
    hours = State()



@dp.message_handler(commands=['start'])
async def start_func(message: types.Message):
    await bot.send_message(message.chat.id, start_message.format(message.from_user.first_name), reply_markup=main_keyboard)


@dp.message_handler(text='📝Подать заявку')
async def send_request(message: types.Message):
    acc_button = types.InlineKeyboardButton('Принять правила✅', callback_data='accept')
    accept_keyboard = types.InlineKeyboardMarkup().add(acc_button)
    await bot.send_message(message.chat.id, accept_message, reply_markup=accept_keyboard)


@dp.message_handler(text='⚙️Отмена')
async def cancel_func(message: types.Message):
    request_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('📝Подать заявку'))
    await bot.send_message(message.chat.id, '🚫Подача заявки отменена', reply_markup= request_keyboard)



@dp.callback_query_handler(text='accept', state="*")
async def accept_rules(query: types.CallbackQuery):
    await bot.send_message(query.message.chat.id, '🕵️Откуда вы о нас узнали?', reply_markup=cancel_keyboard)
    await request_user.info.set()

@dp.message_handler(state=request_user.info, content_types=types.ContentTypes.TEXT)
async def get_info(message: types.Message, state: FSMContext):
    await state.update_data(info=message.text)
    await bot.send_message(message.chat.id, '🧠Есть ли опыт работы? Если да то какой?', reply_markup=cancel_keyboard)
    await request_user.exp.set()


@dp.message_handler(state=request_user.exp, content_types=types.ContentTypes.TEXT)
async def get_exp(message: types.Message, state: FSMContext):
    await state.update_data(exp=message.text)
    await bot.send_message(message.chat.id,'Сколько времени готовы уделять работе?', reply_markup=cancel_keyboard)
    await request_user.hours.set()

@dp.message_handler(state=request_user.hours, content_types=types.ContentTypes.TEXT)
async def get_hours(message: types.Message, state: FSMContext):
    await state.update_data(hours=message.text)
    request = await state.get_data()
    info = request['info']
    exp = request['exp']
    hours = request['hours']
    await state.finish()
    await bot.send_message(message.chat.id, '✅Ваша заявка отправлена✅\nОжидайте⏳')
    await bot.send_message(admin, request_message.format(info, exp, hours, message.chat.id), reply_markup=accept_keyboard)


@dp.callback_query_handler(text="accept_user")
async def send_welcome_message(query: types.CallbackQuery):
    message_id = query.message.message_id
    telegram_id = query.message.text.split("\n")[4].replace('ID воркера:', '').replace(' ', '')
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f'UPDATE users SET worker = ? WHERE telegram_id = ?;', (1, telegram_id))
    conn.commit()
    await bot.delete_message(query.message.chat.id,  message_id)
    await bot.send_message(query.message.chat.id, f'Заявка {telegram_id} принята')
    await bot.send_message(telegram_id, request_accept)


@dp.callback_query_handler(text="reject_user")
async def send_reject_message(query: types.CallbackQuery):
    message_id = query.message.message_id
    telegram_id = query.message.text.split("\n")[4].replace('ID воркера:', '').replace(' ', '')
    await bot.delete_message(query.message.chat.id,  message_id)
    await bot.send_message(query.message.chat.id, f'Заявка {telegram_id} отклонена')
    await bot.send_message(telegram_id, 'Ваша заявка отклонена')






executor.start_polling(dp)
