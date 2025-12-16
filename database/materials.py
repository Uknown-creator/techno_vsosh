import sqlite3
import logging


class Materials:
    def __init__(self, db_file: str = "database/data.db"):
        """
        Docstring for __init__
        
        :param self: Description
        :param db_file: Description
        :type db_file: str
        """
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "materials" (
                            "id"	INTEGER,
                            "author"	TEXT NOT NULL,
                            "date_created"	TEXT NOT NULL,
                            "olymp"	INTEGER NOT NULL,
                            "type"	INTEGER NOT NULL,
                            "header"	TEXT NOT NULL,
                            "year"	INTEGER NOT NULL,
                            "material"	TEXT NOT NULL,
                            PRIMARY KEY("id" AUTOINCREMENT)
                        );""")
        self.connection.commit()

    def get_all_materials(self) -> list:
        """
        Docstring for get_all_materials
        
        
        """
        res = self.cursor.execute(
            """SELECT * FROM materials"""
        ).fetchall()
        return res


    def get_headers(self, olymp: int, material_type: int) -> list:
        """
        Docstring for get_headers
        
        :param olymp: Description
        :type olymp: int
        :param material_type: Description
        :type material_type: int
        :return: Description
        :rtype: list
        """
        res = self.cursor.execute(
            """SELECT header FROM materials WHERE olymp = ? and type = ?""",
            (olymp, material_type)).fetchall()
        if len(res) > 0:
            return res
        return []

    def get_years(self, olymp: int, material_type: int, header: str) -> list:
        """
        Docstring for get_years
        
        :param self: Description
        :param olymp: Description
        :type olymp: int
        :param material_type: Description
        :type material_type: int
        :param header: Description
        :type header: str
        :return: Description
        :rtype: list
        """
        res = self.cursor.execute(
            """SELECT year FROM materials WHERE olymp = ? and type = ? and header = ?""",
            (olymp, material_type, header)).fetchall()
        if len(res) > 0:
            return res
        return []

    def get_material(self, olymp: int, material_type: int, header: str, year: int) -> str:
        """
        Docstring for get_material
        
        :param self: Description
        :param olymp: Description
        :type olymp: int
        :param material_type: Description
        :type material_type: int
        :param header: Description
        :type header: str
        :param year: Description
        :type year: int
        :return: Description
        :rtype: str
        """
        res = self.cursor.execute(
            """SELECT material FROM materials WHERE olymp = ? and type = ? and header = ? and year = ?""",
            (olymp, material_type, header, year)).fetchone()  # fetchall()
        return res[0]

    def get_materials_by_userid(self, author_id: int) -> list:
        """
        Docstring for get_materials_by_userid
        
        :param self: Description
        :param author_id: Description
        :type author_id: int
        :return: Description
        :rtype: list
        """
        res = self.cursor.execute("""SELECT * FROM materials WHERE author = ?""", (author_id,)).fetchall()
        return res

    """ Checking functions """

    @staticmethod
    def check_type_of_material(material: str) -> bool:
        """
        Docstring for check_type_of_material
        
        :param material: Description
        :type material: str
        :return: Description
        :rtype: bool
        """
        if material.startswith("file:"):
            return True
        return False

    def check_existing(self, olymp: int, material_type: int, header: str, year: int) -> bool:
        """
        Docstring for check_existing
        
        :param olymp: Description
        :type olymp: int
        :param material_type: Description
        :type material_type: int
        :param header: Description
        :type header: str
        :param year: Description
        :type year: int
        """
        res = self.cursor.execute("""
        SELECT * FROM materials WHERE olymp = ? and type = ? and header = ? and year = ?
        """, (olymp, material_type, header, year)).fetchall()
        print(res)
        if len(res) != 0:
            return True
        return False

    def post_materials(self, author: int, date_created: str,
                       olymp: int, material_type: int, header: str, year: int, material: str) -> None:
        """
        Docstring for post_materials
        
        :param self: Description
        :param author: Description
        :type author: int
        :param date_created: Description
        :type date_created: str
        :param olymp: Description
        :type olymp: int
        :param material_type: Description
        :type material_type: int
        :param header: Description
        :type header: str
        :param year: Description
        :type year: int
        :param material: Description
        :type material: str
        """
        try:
            self.cursor.execute(
                "INSERT INTO materials(author, date_created, olymp, type, header, year, material) VALUES(?, ?, "
                "?, ?, ?, ?, ?)",
                (author, date_created, olymp, material_type, header, year, material))
            self.connection.commit()
            logging.info(
                f"Материал опубликован пользователем {author} {date_created}\n"
                f"{olymp} {material_type} {header} {year}")
        except Exception as e:
            logging.error(f"Ошибка создания {author} {header} - \n{e}")

    def delete_material(self, material_id: int) -> None:
        """
        Docstring for delete_material
        
        :param self: Description
        :param material_id: Description
        :type material_id: int
        """
        try:
            self.cursor.execute("""DELETE FROM materials WHERE id = ?""", (material_id,))
            self.connection.commit()
            logging.info(f"Материал {material_id} был удалён.")
        except Exception as e:
            logging.error(f"Ошибка удаления {material_id}- {e}")


materials = Materials()
