import string
import sqlite3
import secrets


class Invites:
    def __init__(self, db_file: str = "database/data.db"):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "invite_codes" (
                                "code"	TEXT NOT NULL
                            );""")
        self.connection.commit()

    def add_invite(self) -> str:
        random_code = ''.join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(10))
        self.cursor.execute("""INSERT INTO invite_codes(code) VALUES(?)""",
                            (random_code,))
        self.connection.commit()
        return random_code

    def remove_invite(self, code: str) -> None:
        if self.check_existing(code):
            self.cursor.execute("""DELETE FROM invite_codes WHERE code = ?""", (code,))
            self.connection.commit()

    def check_existing(self, code: str) -> bool:
        is_code_exist = self.cursor.execute('SELECT * FROM invite_codes WHERE code = ?', (code,)).fetchall()
        if len(is_code_exist) != 0:
            return True
        return False


invites = Invites()
if __name__ == "__main__":
    invites = Invites('data.db')
    invites.add_invite()
