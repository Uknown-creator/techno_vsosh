import sqlite3
from config import admins
from git import Repo
import logging

conn = sqlite3.connect("database/data.db")
cur = conn.cursor()


def get_hash():
    try:
        hash_ = Repo().head.commit.hexsha
        return f'<a href="https://github.com/Uknown-creator/techno_vsosh/commit/{hash_}">GitHub</a>'
    except Exception:
        return '<a href="https://github.com/Uknown-creator/techno_vsosh">GitHub</a>'


def add_user(user_id: int, username: str, olymp_role: str):
    if not check_existing(user_id):
        cur.execute("INSERT INTO users VALUES(?, ?, 0, ?)", (user_id, username, convert_role(olymp_role)))
    conn.commit()
    logging.info(f"Пользователь {user_id} зарегестрирован\n{username}, {olymp_role}")


def add_teacher(user_id: int):
    if check_existing(user_id):
        cur.execute("UPDATE users SET teacher = 1 WHERE id = ?", (user_id,))
    conn.commit()
    logging.info(f"Преподаватель {user_id} зарегистрирован")


def is_admin(user_id: int):
    if check_existing(user_id):
        if user_id in admins:
            return True
    return False


def is_teacher(user_id: int):
    if check_existing(user_id):
        res = cur.execute("SELECT teacher FROM users WHERE id = ?", (user_id,)).fetchall()
        if res[0][0] == '1':
            return True
    return False


def get_role(user_id: int) -> int:
    return cur.execute("SELECT olymp_role FROM users WHERE id = ?", (user_id,)).fetchall()[0][0]


def add_admin(user_id: int):
    """
    Doesn't work, admins list on memory
    """
    admins.append(user_id)
    logging.info(f"Администратор {user_id} добавлен")


def get_users():
    return cur.execute("SELECT * FROM users").fetchall()


def check_existing(user_id: int):
    is_user_exist = cur.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchall()
    if len(is_user_exist) != 0:
        return True
    return False


def convert_role(user_direction: str):
    """
    Converting role from nums to string and back
    """
    user_directions_dict = {
        0: "tt",
        1: "ib",
        2: "kd",
        3: "rt"
    }
    if str(user_direction) in '0123':
        return user_directions_dict[int(user_direction)]
    # Reverse to previous, returning keys by values
    return list(user_directions_dict.keys())[list(user_directions_dict.values()).index(user_direction)]
