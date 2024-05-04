# КОД МОЖЕТ БЫТЬ КРИВЫМ, ТАК ЖЕ БОТ СОЗДАВАЛСЯ ПОД 1-2 ЧЕЛОВЕКА, НЕ БОЛЬШЕ, иначе может лагать тк бот синхронный

import telebot
from telebot import types
from googleapiclient.discovery import build
from config import API_KEY, CX, TG_API, ALLOWED_USERS, sites_dict
import sqlite3
import re


class Config:
    start_search_text = '🔍 Начать поиск'
    settings_text = '⚙ Настройки'
    change_date_text = '📅 Фильтровать по дате'
    dorks_payload_text = '💬 Пейлод'
    clear_date = '🧹 Очистить дату'


bot = telebot.TeleBot(TG_API)
_data = None


class Database:
    __instance = None
    DB_NAME = r"browser_history.db"
    TABLE_NAME = 'requests'

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def create_db(cls):
        with sqlite3.connect(cls.DB_NAME) as con:
            cursor = con.cursor()
            cursor.execute(F'''
            CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(256),
                link VARCHAR(256)
            );
            ''')

    @classmethod
    def insert(cls, *, title, link):
        with sqlite3.connect(cls.DB_NAME) as con:
            try:
                cursor = con.cursor()
                cursor.execute('BEGIN')
                cursor.execute(f'INSERT INTO {cls.TABLE_NAME} (title, link) VALUES (?, ?)', (title, link))
            except:
                con.rollback()
                raise

    @classmethod
    def check_visited(cls, link):
        with sqlite3.connect(cls.DB_NAME) as con:
            cur = con.cursor()
            cur.execute(f'SELECT * FROM requests WHERE link="{link}";')
            return cur.fetchall()


class DorksSearch:
    def __init__(self):
        self.db = Database()
        self.db.create_db()

    @staticmethod
    def search_links(api_key, query, num_results=5):
        service = build('customsearch', 'v1', developerKey=api_key)
        res = service.cse().list(
            q=query,
            cx=CX,
            num=num_results
        ).execute()

        return res.get('items', [])

    def main(self, query, *, num_res=10, s=1):
        api_key = API_KEY
        num_results = num_res
        results = self.search_links(api_key, query, num_results)

        total_text = ''

        for i, result in enumerate(results, start=s):
            title = result.get('title', 'No title available').replace(' – Telegraph', '').replace(' — Teletype', '')
            link = result.get('link', 'No link available')

            total_title = f"{title}\n{i}. {link}"
            if self.db.check_visited(link):
                total_title = f"[+] {title}\n{i}. {link}"

            total_text += total_title + '\n\n'

            self.db.insert(title=title, link=link)
        return total_text


class Keyboards:
    # SEARCH #
    search_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    search_itembtn1 = types.KeyboardButton(Config.start_search_text)
    search_itembtn2 = types.KeyboardButton(Config.settings_text)
    search_itembtn3 = types.KeyboardButton(Config.dorks_payload_text)
    search_itembtn4 = types.KeyboardButton(Config.change_date_text)
    search_itembtn5 = types.KeyboardButton(Config.clear_date)
    search_markup.add(search_itembtn1, search_itembtn2, search_itembtn4, search_itembtn3, search_itembtn5, row_width=3)

    # BACK #
    back_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_itembtn1 = types.KeyboardButton("Назад")
    back_markup.add(back_itembtn1)

    back_markup_and_date = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_itembtn2 = types.KeyboardButton("2023-01-01")
    back_markup_and_date.add(back_itembtn2, back_itembtn1)


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id in ALLOWED_USERS:
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=Keyboards.search_markup)


@bot.message_handler(func=lambda message: message.text == "Назад" and message.chat.id in ALLOWED_USERS)
def back(message):
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=Keyboards.search_markup)


@bot.message_handler(func=lambda message: message.text == Config.start_search_text and message.chat.id in ALLOWED_USERS)
def start_search(message):
    data = f'[Результаты после {_data}]' if _data else ''
    bot.send_message(message.chat.id, f"Введите запрос {data}:", reply_markup=Keyboards.back_markup)
    bot.register_next_step_handler(message, search_process_query)


def search_process_query(message):
    if message.chat.id in ALLOWED_USERS:
        query = message.text.strip()
        if query in ('0', 'Назад'):
            bot.send_message(message.chat.id, "Возвращаюсь назад.", reply_markup=Keyboards.search_markup)

        elif query in (Config.start_search_text, 'Начать поиск'):
            bot.send_message(message.chat.id, text='Введите запрос:')
            bot.register_next_step_handler(message, search_process_query)

        else:
            search = DorksSearch()
            sites_dorks = ' | '.join([f'site:{site}' for site, value in sites_dict.items() if value])
            dorks_payload = f"{f"after:{_data}" if _data else ''} ({query}|intext:({query})) {sites_dorks}"

            result = search.main(dorks_payload)
            if not result:
                bot.send_message(message.chat.id, text='Ничего не найдено')
                bot.register_next_step_handler(message, search_process_query)
            else:
                bot.send_message(message.chat.id, text=result, disable_web_page_preview=True)
                print(result)

                bot.send_message(message.chat.id, "Введите запрос:")
                bot.register_next_step_handler(message, search_process_query)


@bot.message_handler(func=lambda message: message.text == Config.settings_text and message.chat.id in ALLOWED_USERS)
def settings(message):
    print('settings')
    sites = ''
    for i, (site, value) in enumerate(sites_dict.items(), start=1):
        sites += f"{i}. {'🟢' if value else '🔴'} | {site}\n"
    sites += 'Выберите действие: '
    bot.send_message(message.chat.id, "` ~ ~ - - - Настройки - - - ~ ~ `\n"
                                      "Использовать такие сайты как:\n"
                     + sites, reply_markup=Keyboards.back_markup)
    bot.register_next_step_handler(message, settings_process_query)


def settings_process_query(message):
    if message.chat.id in ALLOWED_USERS:
        sites = list(sites_dict)

        query = message.text.strip()
        if query in ('0', 'Назад'):
            bot.send_message(message.chat.id, text='Возвращаюсь в главное меню...',
                             reply_markup=Keyboards.search_markup)
        elif len(sites) < int(query):
            bot.send_message(message.chat.id, text='❌ Цифра слишком большая')
            settings(message)
        elif query.isdecimal() and int(query) > 0:
            site = sites[int(query) - 1]
            sites_dict[site] = not sites_dict[site]
            settings(message)


@bot.message_handler(func=lambda message: message.text == Config.change_date_text and message.chat.id in ALLOWED_USERS)
def change_data(message: types.Message):
    bot.send_message(chat_id=message.chat.id,
                     text='Нажмите Enter чтобы поставить 2023-01-01\nИли введите свою дату в формате ГГГГ-ММ-ДД, вместе с тире: ',
                     reply_markup=Keyboards.back_markup_and_date)
    bot.register_next_step_handler(message, change_date_process_query)


def change_date_process_query(message: types.Message):
    pattern = r'\d{4}-\d{2}-\d{2}'
    match = re.findall(pattern, message.text)
    if match:
        global _data
        _data = match[0]
        bot.send_message(chat_id=message.chat.id, text='Дата задана, можно искать информацию!',
                         reply_markup=Keyboards.search_markup)
    else:
        bot.send_message(chat_id=message.chat.id, text="\nВы ввели неправильный формат даты,"
                                                       "\nФормат: ГГГГ-ММ-ДД"
                                                       "\nПример: 2023-01-01\n",
                         reply_markup=Keyboards.search_markup)


@bot.message_handler(
    func=lambda message: message.text == Config.dorks_payload_text and message.chat.id in ALLOWED_USERS)
def get_dorks_payload(message):
    data = f'[Результаты после {_data}]' if _data else ''
    bot.send_message(message.chat.id, f"Введите запрос {data}:", reply_markup=Keyboards.back_markup)
    bot.register_next_step_handler(message, dorks_process_query)


def dorks_process_query(message):
    if message.chat.id in ALLOWED_USERS:
        query = message.text.strip()
        if query in ('0', 'Назад'):
            bot.send_message(message.chat.id, "Возвращаюсь назад.", reply_markup=Keyboards.search_markup)
        elif query in (Config.start_search_text, 'Начать поиск'):
            bot.send_message(message.chat.id, text='Введите запрос:')
            bot.register_next_step_handler(message, dorks_process_query)
        else:
            sites_dorks = ' | '.join([f"site:{site}" for site, value in sites_dict.items() if value])
            dorks_payload = f"{f"after:{_data}" if _data else ''} ({query}|intext:({query})) {sites_dorks}"
            bot.send_message(message.chat.id, text=dorks_payload, disable_web_page_preview=True)

            bot.send_message(message.chat.id, "Введите запрос:")
            bot.register_next_step_handler(message, dorks_process_query)


@bot.message_handler(func=lambda message: message.text == Config.clear_date and message.chat.id in ALLOWED_USERS)
def clear_date(message):
    global _data
    _data = None
    bot.send_message(chat_id=message.chat.id, text='Успешно!')


if __name__ == '__main__':
    bot.polling(skip_pending=False)

