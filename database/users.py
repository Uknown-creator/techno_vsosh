import sqlite3
import logging

from config import ADMINS_IDS


class Users:
    def __init__(self, db_file: str = "database/data.db"):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "users" (
                            "id"	INTEGER NOT NULL UNIQUE,
                            "username"	TEXT,
                            "teacher"	INTEGER NOT NULL,
                            "olymp_role"	INTEGER NOT NULL
                        );""")
        self.user_directions_dict = {
            0: "tt",
            1: "ib",
            2: "kd",
            3: "rt"
        }
        self.connection.commit()

    def add_user(self, user_id: int, username: str, olymp_role: str) -> None:
        if not self.check_existing(user_id):
            self.cursor.execute("INSERT INTO users VALUES(?, ?, 0, ?)",
                                (user_id, username, self.convert_role(olymp_role)))
            self.connection.commit()
            logging.info(f"Пользователь {user_id} зарегестрирован\n{username}, {olymp_role}")
            return
        else:
            logging.warning("Попытка зарегестрировать существующего пользователя")
            return

    def add_teacher(self, user_id: int, username: str = "teacher", olymp_role: str = "tt") -> None:
        if self.check_existing(user_id):
            self.cursor.execute("UPDATE users SET teacher = 1 WHERE id = ?", (user_id,))
            self.connection.commit()
            logging.info(f"Преподаватель {user_id} зарегистрирован")
            return
        else:
            self.add_user(user_id, username, olymp_role)
            self.add_teacher(user_id, username, olymp_role)
            logging.info(f"Преподаватель {user_id} зарегистрирован")
            return

    def change_role(self, user_id: int, olymp_role: str) -> None:
        if self.check_existing(user_id):
            role = self.convert_role(olymp_role)
            self.cursor.execute("UPDATE users SET olymp_role = ? WHERE id = ?", (role, user_id))
            self.connection.commit()
            logging.info(f"Пользователь {user_id} изменил роль на {olymp_role}")

    def is_admin(self, user_id: int) -> bool:
        if self.check_existing(user_id):
            if user_id in ADMINS_IDS:
                return True
        return False

    def is_teacher(self, user_id: int) -> bool:
        if self.check_existing(user_id):
            res = self.cursor.execute("SELECT teacher FROM users WHERE id = ?", (user_id,)).fetchall()
            if res[0][0] == '1':
                return True
        return False

    def check_existing(self, user_id: int) -> bool:
        is_user_exist = self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchall()
        if len(is_user_exist) != 0:
            return True
        return False

    def get_role(self, user_id: int) -> int:
        return self.cursor.execute("SELECT olymp_role FROM users WHERE id = ?", (user_id,)).fetchall()[0][0]

    def get_users(self) -> list:
        return self.cursor.execute("SELECT * FROM users").fetchall()

    def convert_role(self, user_direction: str) -> str | int:
        if str(user_direction) in '0123':
            return self.user_directions_dict[int(user_direction)]
        return list(self.user_directions_dict.keys())[list(self.user_directions_dict.values()).index(user_direction)]


users = Users()
