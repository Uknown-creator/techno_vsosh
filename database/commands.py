import sqlite3
from config import admins

conn = sqlite3.connect("database/data.db")
cur = conn.cursor()


def add_user(user_id: int, username: str, olymp_role: str):
    if not check_existing(user_id):
        cur.execute("INSERT INTO users VALUES(?, ?, 0, ?)", (user_id, username, convert_role(olymp_role)))
    conn.commit()


def add_teacher(user_id: int):
    if check_existing(user_id):
        cur.execute("UPDATE users SET teacher = 1 WHERE id = ?", (user_id,))
    conn.commit()


def is_admin(user_id: int):
    if user_id in admins:
        return True
    return False


def is_teacher(user_id: int):
    res = cur.execute("SELECT teacher FROM users WHERE id = ?", (user_id,)).fetchall()
    if len(res[0]) > 0:
        return True
    return False


def get_role(user_id: int):
    return cur.execute("SELECT olymp_role FROM users WHERE id = ?", (user_id,)).fetchall()


def add_admin(user_id: int):
    admins.append(user_id)


def get_users():
    return cur.execute("SELECT * FROM users").fetchall()


def check_existing(user_id: int):
    is_user_exist = cur.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchall()
    if len(is_user_exist) != 0:
        return True
    return False


def convert_role(user_direction: str):
    user_directions_dict = {
        0: "tt",
        1: "ib",
        2: "kd",
        3: "rt"
    }
    if str(user_direction) in '0123':
        return user_directions_dict[int(user_direction)]
    # Reverse to previous, returning keys by values
    return list(user_directions_dict.keys())[list(user_directions_dict.values()).index(user_direction)]


def get_types(olymp, direction):
    return cur.execute('SELECT type FROM materials WHERE olymp = ? and direction = ?', (olymp, direction)).fetchall()


def get_headers(olymp: int, direction: int, type_of_material: str):
    res = cur.execute('SELECT header FROM materials WHERE olymp = ? and direction = ? and type = ?',
                      (olymp, direction, type_of_material)).fetchall()
    return res


def get_headers_byid(content_id: int):  # Necessary?
    res = cur.execute('SELECT header FROM materials WHERE id = ?', (content_id,)).fetchall()
    return res


def get_content_id(user_id: int, direction: int, type_of_material: str, header: str):  # Necessary?
    olymp = get_role(user_id)[0][0]
    res = cur.execute('SELECT id FROM materils WHERE olymp = ? and direction = ? and type = ? and header = ?',
                      (olymp, direction, type_of_material, header)).fetchall()
    return res


def get_materials(header: str):
    res = cur.execute(
        """SELECT material FROM materials WHERE header = ?""",
        (header,)).fetchall()
    return res


def post_materials(olymp, direction, type_of_material, header, material):
    cur.execute("INSERT INTO materials(olymp, direction, type, header, material) VALUES(?, ?, ?, ?, ?)",
                (olymp, direction, type_of_material, header, material))
    conn.commit()
