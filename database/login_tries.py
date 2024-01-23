import sqlite3


class LoginTries:
    def __init__(self, db_file: str = "database/data.db"):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "login_tries" (
                                "id"	INTEGER NOT NULL,
                                "tries"	INTEGER NOT NULL
                            );""")

        self.connection.commit()

    def add_try(self, user_id: int) -> None:
        if not self.check_existing(user_id):
            self.cursor.execute("""INSERT INTO login_tries VALUES(?, 1)""", (user_id,))
            self.connection.commit()
        else:
            tries = self.get_tries(user_id) + 1
            self.cursor.execute("""UPDATE login_tries SET tries = ?""", (tries,))
            self.connection.commit()

    def check_existing(self, user_id: int) -> bool:
        is_user_exist = self.cursor.execute('SELECT * FROM login_tries WHERE id = ?', (user_id,)).fetchall()
        if len(is_user_exist) != 0:
            return True
        return False

    def get_users(self) -> list:
        res = self.cursor.execute("""SELECT * FROM login_tries""").fetchall()
        return res

    def get_tries(self, user_id) -> int:
        if self.check_existing(user_id):
            res = self.cursor.execute("""SELECT tries FROM login_tries WHERE id = ?""", (user_id,)).fetchall()
            return int(res[0][0])
        return 0


login_tries = LoginTries()
