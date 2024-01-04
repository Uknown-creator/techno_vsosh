import sqlite3
import logging

conn = sqlite3.connect("database/data.db")
cur = conn.cursor()


def get_types(olymp, direction) -> list:
    return cur.execute('SELECT type FROM materials WHERE olymp = ? and direction = ?', (olymp, direction)).fetchall()


def get_headers(olymp: int, direction: int, type_of_material: str) -> list:
    res = cur.execute('SELECT header FROM materials WHERE olymp = ? and direction = ? and type = ?',
                      (olymp, direction, type_of_material)).fetchall()
    return res


def get_materials_by_header(header: str) -> str:
    """
    Soon will be replaced with full getting of materials(with olymp, direction, and etc)
    """
    res = cur.execute(
        """SELECT material FROM materials WHERE header = ?""",
        (header,)).fetchall()
    return res[0][0]


def get_materials():
    res = cur.execute(
        """SELECT * FROM materials"""
    ).fetchall()
    return res


def get_materials_by_userid(user_id):
    res = cur.execute("SELECT * FROM materials WHERE author = ?", (user_id,)).fetchall()
    return res


def post_materials(author, date_created, olymp, direction, type_of_material, header, material):
    """
    Posting materials with SQLite.
    Olymp - ib/tt/kd/rt, direction - theory/practice/project(0/1/2)
    """
    try:
        cur.execute(
            "INSERT INTO materials(author, date_created, olymp, direction, type, header, material) VALUES(?, ?, "
            "?, ?, ?, ?, ?)",
            (author, date_created, olymp, direction, type_of_material, header, material))
        conn.commit()
        logging.info(
            f"Материал опубликован пользователем {author} {date_created}\n"
            f"{olymp} {direction} {type_of_material} {header}")
    except Exception as e:
        logging.warning(f"Ошибка создания {author} {header}- {e}")


def delete_material(material_id):
    try:
        cur.execute("""DELETE FROM materials WHERE id = ?""", (material_id,))
        conn.commit()
        logging.info(f"Материал {material_id} был удалён.")
    except Exception as e:
        logging.warning(f"Ошибка удаления {material_id}- {e}")
