import sqlite3
from hashlib import md5


class UsedGosuslugi:
    def __init__(self, db_file: str = "database/data.db"):
        """
        Docstring for __init__
        
        :param self: Description
        :param db_file: Description
        :type db_file: str
        """
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "used_gosuslugi" (
                                "hash"	TEXT NOT NULL
                            );""")

        self.connection.commit()

    @staticmethod
    def hash_person_id(person_id: str) -> str:
        """
        Docstring for hash_person_id
        
        :param person_id: Description
        :type person_id: str
        :return: Description
        :rtype: str
        """
        hash_object = md5(person_id.encode())
        return hash_object.hexdigest()

    def add_hash(self, person_id: str) -> None:
        """
        Docstring for add_hash
        
        :param self: Description
        :param person_id: Description
        :type person_id: str
        """
        h_person_id = self.hash_person_id(person_id)
        self.cursor.execute("""INSERT INTO used_gosuslugi VALUES (?)""", (h_person_id,))
        self.connection.commit()

    def check_existing(self, h_person_id: str) -> bool:
        """
        Docstring for check_existing
        
        :param self: Description
        :param h_person_id: Description
        :type h_person_id: str
        :return: Description
        :rtype: bool
        """
        res = self.cursor.execute("""SELECT * FROM used_gosuslugi WHERE hash = ?""", (h_person_id,)).fetchall()
        if len(res) != 0:
            return True
        return False


used_gosuslugi = UsedGosuslugi()
