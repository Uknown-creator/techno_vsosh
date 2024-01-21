import string
import sqlite3
import secrets


class Invites:
    def __init__(self, db_file: str = "database/data.db"):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "invite_codes" (
                                "id"	INTEGER NOT NULL,
                                "code"	TEXT NOT NULL
                            );""")
        self.connection.commit()

    def add_invite(self, user_id: str) -> None:
        if not self.check_existing(user_id):
            random_code = ''.join(
                secrets.choice(string.ascii_letters + string.digits + string.punctuation)
                for _ in range(10))
            self.cursor.execute("""INSERT INTO invite_codes VALUES(?, ?)""",
                                (user_id, random_code))
            self.connection.commit()

    def remove_invite(self, user_id: str) -> None:
        self.cursor.execute("""DELETE FROM invite_codes WHERE id = ?""", (user_id,))

    def check_existing(self, user_id: str) -> bool:
        is_code_exist = self.cursor.execute('SELECT * FROM invite_codes WHERE id = ?', (user_id,)).fetchall()
        if len(is_code_exist) != 0:
            return True
        return False

    def get_invite(self, user_id: str) -> str | None:
        result = self.cursor.execute("""SELECT * FROM invite_codes WHERE id = ?""", (user_id,)).fetchall()
        if len(result[0]) > 0:
            print(result)
            return '_'.join(str(i) for i in result[0])  # [0] - id, [1] - code, id code
        return


# invites = Invites()
if __name__ == "__main__":
    invites = Invites('data.db')
    invites.add_invite('00000')
    print(invites.get_invite('00000'))
