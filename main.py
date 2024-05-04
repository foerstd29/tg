from googleapiclient.discovery import build

import sqlite3
import re

from config import API_KEY, CX, sites_dict


class Database:
    __instance = None
    DB_NAME = r"history.db"
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
        self._date = None

    @staticmethod
    def search_links(api_key, query, num_results=5):
        service = build('customsearch', 'v1', developerKey=api_key)
        res = service.cse().list(
            q=query,
            cx=CX,
            num=num_results
        ).execute()

        return res.get('items', [])

    def engine(self, query, *, num_res=10, s=1):
        api_key = API_KEY
        num_results = num_res
        results = self.search_links(api_key, query, num_results)

        for i, result in enumerate(results, start=s):
            title = result.get('title', 'Нет заголовка').replace('– Telegraph', '').replace('— Teletype', '')
            link = result.get('link', 'Нет ссылки')

            total_title = f"{title}\n{i}. {link}"
            if self.db.check_visited(link):
                total_title = f"[+] {title}\n{i}. {link}"

            print(total_title)
            print()
            self.db.insert(title=title, link=link)

    def search_api(self):
        print()
        print(f'` ~ ~ - - - Поиск - - - ~ ~ `\n'
              f'0. Назад {"[Результаты после " + self._date + "]" if self._date else ""}')
        while True:
            io = input('Введите запрос: ')
            if io == '0':
                print()
                break
            sites_dorks = ' | '.join([f'site:{site}' for site, value in sites_dict.items() if value])

            dorks_payload = f"{f"after:{self._date}" if self._date else ''} ({io} | intext:({io})) {sites_dorks}"
            # СТАРЫЙ ЗАПРОС
            # dorks_payload = f"{io} | intext:({io}) {' | '.join([f'site:{site}' for site, value in sites_dict.items() if value])} {f"AFTER:{self._date}" if self._date else None}"
            self.engine(dorks_payload)

    def settings_api(self):
        while True:
            print()
            print('` ~ ~ - - - Настройки - - - ~ ~ `\n'
                  f'Использовать такие сайты как: ')
            for i, (site, value) in enumerate(sites_dict.items(), start=1):
                print(f'{i}. {site} | {value}')
            print('0. Назад')
            choice = input('Выберите действие: ')
            if choice == '0':
                print()
                break
            if choice.isdecimal() and int(choice) > 0:
                sites = list(sites_dict)
                site = sites[int(choice) - 1]
                sites_dict[site] = not sites_dict[site]

    def set_data_api(self):
        while True:
            print()
            io = input('0. Назад\nНажмите Enter чтобы поставить 2023-01-01\nИли введите свою дату в формате ГГГГ-ММ-ДД, вместе с тире: ')
            if io == '0':
                break

            if io == '':
                self._date = '2023-01-01'
                print('Дата задана, можно искать информацию!')
                break
            pattern = r'\d{4}-\d{2}-\d{2}'
            match = re.findall(pattern, io)
            if match:
                self._date = match[0]
                print('Дата задана, можно искать информацию!')
            else:
                print("\nВы ввели неправильный формат даты,"
                      "\nФормат: ГГГГ-ММ-ДД"
                      "\nПример: 2023-01-01\n")

    def get_dorks_api(self):
        print()
        io = input('Введите запрос: ')

        sites_dorks = ' | '.join([f'site:{site}' for site, value in sites_dict.items() if value])
        dorks_payload = f"{f"after:{self._date} " if self._date else ''}({io} | intext:({io})) {sites_dorks}"
        print(dorks_payload)

    def interface(self):
        while True:
            print()
            print('~ * - * - Меню - * - * ~')
            print('1. Поиск')
            print('2. Настройки')
            print(f'3. Сортировать по дате')
            print(f'4. Дорк пэйлоад')
            if self._date:
                print('5. Очистить дату')

            choice = input('Выберите действие: ')
            match choice:
                case '1':
                    self.search_api()
                case '2':
                    self.settings_api()
                case '3':
                    self.set_data_api()
                case '4':
                    self.get_dorks_api()
                case '5':
                    self._date = None


if __name__ == "__main__":
    try:
        search = DorksSearch()
        search.interface()
    except KeyboardInterrupt:
        exit('\nПока')
    except Exception:
        raise
