import sqlite3
import logging


class Materials:
    def __init__(self, db_file: str = "database/data.db"):
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
        res = self.cursor.execute(
            """SELECT * FROM materials"""
        ).fetchall()
        return res[0]

    """ Getting values from Materials"""

    def get_headers(self, olymp: int, material_type: int) -> list:
        res = self.cursor.execute(
            """SELECT header FROM materials WHERE olymp = ? and type = ?""",
            (olymp, material_type)).fetchall()
        return res[0]

    def get_years(self, olymp: int, material_type: int, header: str) -> list:
        res = self.cursor.execute(
            """SELECT year FROM materials WHERE olymp = ? and type = ? and header = ?""",
            (olymp, material_type, header)).fetchall()
        return res[0]

    def get_material(self, olymp: int, material_type: int, header: str, year: int) -> str:
        res = self.cursor.execute(
            """SELECT material FROM materials WHERE olymp = ? and type = ? and header = ? and year = ?""",
            (olymp, material_type, header, year)).fetchone()  # fetchall()
        return res[0]

    def get_materials_by_userid(self, author_id: int) -> list:
        res = self.cursor.execute("""SELECT * FROM materials WHERE author = ?""", (author_id,)).fetchall()
        return res[0]

    """ Checking functions """

    @staticmethod
    def check_type_of_material(material: str) -> bool:
        if material.startswith("file:"):
            return True
        return False

    """ Posting and deleting """

    def post_materials(self, author: int, date_created: str,
                       olymp: int, material_type: int, header: str, year: int, material: str) -> None:
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
        try:
            self.cursor.execute("""DELETE FROM materials WHERE id = ?""", (material_id,))
            self.connection.commit()
            logging.info(f"Материал {material_id} был удалён.")
        except Exception as e:
            logging.error(f"Ошибка удаления {material_id}- {e}")


materials = Materials()
