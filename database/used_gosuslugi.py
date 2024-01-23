import sqlite3
from hashlib import md5


class UsedGosuslugi:
    def __init__(self, db_file: str = "database/data.db"):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "used_gosuslugi" (
                                "hash"	TEXT NOT NULL
                            );""")

        self.connection.commit()

    @staticmethod
    def hash_person_id(person_id: str) -> str:
        hash_object = md5(person_id.encode())
        return hash_object.hexdigest()

    def add_hash(self, person_id: str) -> None:
        h_person_id = self.hash_person_id(person_id)
        self.cursor.execute("""INSERT INTO used_gosuslugi VALUES (?)""", (h_person_id,))
        self.connection.commit()

    def check_existing(self, h_person_id: str) -> bool:
        res = self.cursor.execute("""SELECT * FROM used_gosuslugi WHERE hash = ?""", (h_person_id,)).fetchall()
        if len(res) != 0:
            return True
        return False


used_gosuslugi = UsedGosuslugi()
