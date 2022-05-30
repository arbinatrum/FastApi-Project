import psycopg2
import json
from psycopg2.extras import RealDictCursor
from error import error
from driver import start_driver


class Postgres:
    HOST = '185.46.10.66'
    PORT = 5432
    USER = 'arbinatrum'
    PASS = '123456'
    NAME = 'test_db'

    def __init__(self):
        self.DATABASE_URL = f'postgresql://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}'

    def __enter__(self):
        self.connection = psycopg2.connect(self.DATABASE_URL, cursor_factory=RealDictCursor)
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.connection.close()
        self.cursor.close()


def get_query_status(query):  # статус наличия такого же запроса
    with Postgres() as cursor:
        cursor.execute(f"""
            select time
            from schema.marksdata1
            where name = '{query}';
        """)

        records = cursor.fetchone()

        if records:
            return records['time']
        else:
            return False


def get_data(query):
    with Postgres() as cursor:
        cursor.execute(f"""
            select file
            from schema.marksdata1
            where name = '{query}'        
        """)

        records = cursor.fetchone()

        if records:
            return records['file']
        else:
            return False


def set_data(query, new_item):
    file = start_driver(query)
    if file:
        exit_file = json.dumps(file, indent=3, ensure_ascii=False)

        if new_item == '0':
            with Postgres() as cursor:
                cursor.execute(f"""
                    insert
                    into schema.marksdata1(name, file)
                    values (%s, %s)
                """, (query, exit_file))
                return error(1, "Данные успешно заполнены")
        else:
            with Postgres() as cursor:
                cursor.execute(f"""
                    update schema.marksdata1
                    set file = '{exit_file}', time = now()
                    where name = '{query}'
                """)
                return error(2, "Данные успешно обновлены")
    else:
        return error(0, "Не удалось заполнить данные в set_data")