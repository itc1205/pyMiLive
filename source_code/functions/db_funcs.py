import os
import shutil
import sqlite3


def check_db_exists():
    """Метод для проверки наличия рабочей базы данных и папки с шрифтами"""
    if not os.path.exists("fonts"):
        os.mkdir("fonts")

    if not os.path.exists("fonts/music_fonts_db.sqlite"):
        with open("fonts/music_fonts_db.sqlite", "w"):
            pass

        con = sqlite3.connect("fonts/music_fonts_db.sqlite")

        cur = con.cursor()

        cur.execute(f"""CREATE TABLE music_fonts (
        id        INTEGER PRIMARY KEY AUTOINCREMENT
                          UNIQUE
                          NOT NULL,
        path      STRING  UNIQUE
                          NOT NULL,
        font_name STRING  UNIQUE
                          NOT NULL);
        """).fetchall()
        con.close()


def write_into_database(path):
    """Метод для записи данных в бд и перемещения шрифтов в нужную папку"""
    check_db_exists()
    if not os.path.exists(f"fonts/{path.split('/')[-1]}"):
        shutil.copy(path, f"fonts/{path.split('/')[-1]}")

        con = sqlite3.connect("fonts/music_fonts_db.sqlite")

        cur = con.cursor()

        cur.execute(f""" INSERT INTO music_fonts(path, font_name) 
        VALUES('fonts/{path.split('/')[-1]}','{path.split('/')[-1].split('.')[0]}')
    """)
        con.commit()
        con.close()


def get_items_from_fonts_db():
    """Метод для подгрузки шрифтов из бд в словарь"""
    con = sqlite3.connect("fonts/music_fonts_db.sqlite")

    cur = con.cursor()

    result = cur.execute(f"""SELECT font_name, path FROM music_fonts""").fetchall()
    con.close()
    dict_res = {}
    for i in range(len(result)):
        dict_res[result[i][0]] = result[i][1]
    return dict_res


def delete_from_db(path):
    """Метод для удаления шрифтов из папки"""
    con = sqlite3.connect("fonts/music_fonts_db.sqlite")

    cur = con.cursor()

    cur.execute(f"""DELETE FROM music_fonts WHERE path = '{path}'""").fetchall()

    con.commit()
    con.close()
    if os.path.exists(path):
        os.remove(path)
