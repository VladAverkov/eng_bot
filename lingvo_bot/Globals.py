from wiktionaryparser import WiktionaryParser
from telebot import TeleBot

parser = WiktionaryParser() #Парсер для поиска значения слова на wiktionary
word = None #слово, которое пользователь хочет выучить
set_of_words = [] #набор слов для повторения
definition = None #определение слова
token = 'Your token here'
bot = TeleBot(token)

#запрос для создания таблицы
create_str = 'CREATE TABLE IF NOT EXISTS words(id INTEGER PRIMARY KEY, word VARCHAR(50), ' \
             'def VARCHAR(100), dttm DATETIME, box INTEGER, user_id INTEGER)'
#запрос для вставки новой строки
insert_str = "INSERT INTO words (word, def, dttm, box, user_id) VALUES ('{}', '{}', '{}', {}, {})"
#запрос для выбора строк для повторения
select_str = "SELECT * FROM words WHERE julianday('{}') - julianday(dttm) >= (CASE box" \
             " WHEN 0 THEN 0" \
             " WHEN 1 THEN 1" \
             " WHEN 2 THEN 7" \
             " WHEN 3 THEN 14" \
             " WHEN 4 THEN 30" \
             " WHEN 5 THEN 60" \
             " WHEN 6 THEN 180" \
             " ELSE NULL" \
             " END) AND user_id = {} AND box < 7 ORDER BY box"
#запрос для обновления статуса (box) изучаемого слова, 0 - новое слово
#чем больше статус, тем лучше пользователь знает слово
update_str = "UPDATE words SET box = box + 1 WHERE id = {}"

