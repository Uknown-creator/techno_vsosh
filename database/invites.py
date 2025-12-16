import string
import sqlite3
import secrets


class Invites:
    def __init__(self, db_file: str = "database/data.db"):
        """
        Docstring for __init__
        
        :param self: Description
        :param db_file: Description
        :type db_file: str
        """
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "invite_codes" (
                                "code"	TEXT NOT NULL
                            );""")
        self.connection.commit()

    def add_invite(self) -> str:
        """
        Docstring for add_invite
        
        :param self: Description
        :return: Description
        :rtype: str
        """
        random_code = ''.join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(10))
        self.cursor.execute("""INSERT INTO invite_codes(code) VALUES(?)""",
                            (random_code,))
        self.connection.commit()
        return random_code

    def remove_invite(self, code: str) -> None:
        """
        Docstring for remove_invite
        
        :param self: Description
        :param code: Description
        :type code: str
        """
        if self.check_existing(code):
            self.cursor.execute("""DELETE FROM invite_codes WHERE code = ?""", (code,))
            self.connection.commit()

    def check_existing(self, code: str) -> bool:
        """
        Docstring for check_existing
        
        :param self: Description
        :param code: Description
        :type code: str
        :return: Description
        :rtype: bool
        """
        is_code_exist = self.cursor.execute('SELECT * FROM invite_codes WHERE code = ?', (code,)).fetchall()
        if len(is_code_exist) != 0:
            return True
        return False


invites = Invites()
if __name__ == "__main__":
    invites = Invites('data.db')
    invites.add_invite()
