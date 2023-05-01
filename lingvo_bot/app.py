from telebot import types
from sqlite3 import connect
from datetime import datetime
from Globals import parser
from Globals import word
from Globals import set_of_words
from Globals import definition
from Globals import create_str
from Globals import insert_str
from Globals import select_str
from Globals import update_str
from Globals import bot


def insert(word, definition, dttm, box, chat_id):
    conn = connect('words.sql')
    cur = conn.cursor()
    cur.execute(insert_str.format(word, definition, dttm, box, chat_id))
    conn.commit()
    cur.close()
    conn.close()


def create():
    """Функкция создает БД при первой регистрации какого-нибудь пользователя"""
    conn = connect('words.sql')
    cur = conn.cursor()
    cur.execute(create_str)
    conn.commit()
    cur.close()
    conn.close()


def update(id):
    """Функция для обновления статуса слова в таблице"""
    conn = connect('words.sql')
    cur = conn.cursor()
    cur.execute(update_str.format(id))
    conn.commit()
    cur.close()
    conn.close()


@bot.message_handler(commands=['start'])
def start(message):
    """Функция для обработки комманды старт"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Добавить слово', callback_data='add_word'))
    bot.send_message(message.chat.id, 'Привет! Я Lingvo_telebot - ваш помощник в изучении английского языка. '
                                      'Выберите действие', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'add_word')
def add_word_callback(call):
    """Обраотка нажатия на кнопку добавить слово"""
    bot.send_message(call.message.chat.id, 'Введите слово')
    bot.register_next_step_handler(call.message, add_word)


def add_word(message):
    """Функция для ввода значения пользователем"""
    global word, definition
    word = message.text
    markup = types.InlineKeyboardMarkup()
    try:
        definitions = parser.fetch(word)
        definition = definitions[0]['definitions'][0]['text'][1]
        markup.add(types.InlineKeyboardButton(definition, callback_data='first_meaning'))
    except:
        pass
    markup.add(types.InlineKeyboardButton('Другое значение', callback_data='other_meaning'))
    bot.send_message(message.chat.id, 'Дайте определение', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'first_meaning')
def add_definition_callback(call):
    """Обработка вызова и вставка строки с данными о слове из сессии пользователя в случае когда пользователь выбрал
        значение, автоматически подобранное ботом"""
    global word, definition
    dttm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    box = 0
    insert(word, definition, dttm, box, call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Добавить слово', callback_data='add_word'))
    markup.add(types.InlineKeyboardButton('Повторить слова', callback_data='repeat_words'))
    bot.send_message(call.message.chat.id, 'Слово добавлено!', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'other_meaning')
def add_definition_callback(call):
    """Обработка вызова в случае когда пользователь решил ввести собственное определение слова"""
    bot.send_message(call.message.chat.id, 'Введите значение слова')
    bot.register_next_step_handler(call.message, add_other_definition)


def add_other_definition(message):
    """Вставка строки с данными о слове из сессии пользователя в случае
        когда пользователь решил ввести собственное определение слова"""
    global word
    other_definition = message.text
    dttm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    box = 0
    insert(word, other_definition, dttm, box, message.chat.id)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Добавить слово', callback_data='add_word'))
    markup.add(types.InlineKeyboardButton('Повторить слова', callback_data='repeat_words'))
    bot.send_message(message.chat.id, 'Слово добавлено!', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'repeat_words')
def repeat_words_callback(call):
    """Обработка нажатия на кнопку повторить слова"""
    bot.send_message(call.message.chat.id, 'Введите количество слов для повторения')
    bot.register_next_step_handler(call.message, repeat_words)


@bot.callback_query_handler(func=lambda call: call.data.split('###')[0] == 'remember')
def remember_callback(call):
    """Обработка случая, когда пользователь помнит слово.
        Уровень слова повышается, и если нужно показать еще слова, то продолжаем показывать"""
    global set_of_words
    chat_id = int(call.data.split('###')[1])
    i = int(call.data.split('###')[2])
    quantity = int(call.data.split('###')[3])
    conn = connect('words.sql')
    update(set_of_words[i][0])
    bot.send_message(chat_id, f"Текущий уровень слова: {set_of_words[i][4] + 1}")
    show(chat_id, i + 1, quantity)


@bot.callback_query_handler(func=lambda call: call.data.split('###')[0] == 'forgot')
def forgot_callback(call):
    """Обработка случая, когда пользователь забыл слово сразу.
        Уровень слова повышается, и если нужно показать еще слова, то продолжаем показывать"""
    global set_of_words
    chat_id = int(call.data.split('###')[1])
    i = int(call.data.split('###')[2])
    quantity = int(call.data.split('###')[3])
    bot.send_message(chat_id, "Определение слова: " + set_of_words[i][2] + "\nТекущий уровень слова: " + str(set_of_words[i][4]))
    show(chat_id, i + 1, quantity)


@bot.callback_query_handler(func=lambda call: call.data.split('###')[0] == 'checked')
def checked_callback(call):
    """Обработка случая, когда пользователь решил посмотреть значение слова, и нажал на кнопку что не помнил значения.
        Уровень слова повышается, и если нужно показать еще слова, то продолжаем показывать"""
    global set_of_words
    chat_id = int(call.data.split('###')[1])
    i = int(call.data.split('###')[2])
    quantity = int(call.data.split('###')[3])
    bot.send_message(chat_id, "Текущий уровень слова: " + str(set_of_words[i][4]))
    show(chat_id, i + 1, quantity)


@bot.callback_query_handler(func=lambda call: call.data.split('###')[0] == 'check_def')
def check_callback(call):
    """Обработка случая, когда пользователь решил посмотреть значение слова.
        Уровень слова повышается, и если нужно показать еще слова, то продолжаем показывать"""
    global set_of_words
    chat_id = int(call.data.split('###')[1])
    i = int(call.data.split('###')[2])
    quantity = int(call.data.split('###')[3])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Помню!', callback_data='###'.join(['remember', str(chat_id), str(i), str(quantity)])))
    markup.add(types.InlineKeyboardButton('Не помню', callback_data='###'.join(['checked', str(chat_id), str(i), str(quantity)])))
    bot.send_message(chat_id, "Определение слова: " + set_of_words[i][2], reply_markup=markup)


def show(chat_id, i, quantity):
    """Функция показывающая пользователю одно слово"""
    global set_of_words
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Помню!', callback_data='###'.join(['remember', str(chat_id), str(i), str(quantity)])))
    markup.add(types.InlineKeyboardButton('Не помню', callback_data='###'.join(['forgot', str(chat_id), str(i), str(quantity)])))
    markup.add(types.InlineKeyboardButton('Посмотреть определение', callback_data='###'.join(['check_def', str(chat_id), str(i), str(quantity)])))
    if i < quantity and i < len(set_of_words):
        bot.send_message(chat_id, set_of_words[i][1], reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Добавить слово', callback_data='add_word'))
        markup.add(types.InlineKeyboardButton('Повторить слова', callback_data='repeat_words'))
        bot.send_message(chat_id, 'Вы повторили все слова!', reply_markup=markup)
        return


def repeat_words(message):
    """Функция обрабатывающая нажатие на кнопку повторить слова"""
    global set_of_words
    conn = connect('words.sql')
    cur = conn.cursor()
    cur.execute(select_str.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message.chat.id))
    quantity = int(message.text)
    set_of_words = cur.fetchall()[:quantity]
    cur.close()
    conn.close()
    show(message.chat.id, 0, quantity)


def app():
    bot.polling(none_stop=True)
    create()

