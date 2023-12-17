import sqlite3

conn = sqlite3.connect("database/data.db")
cur = conn.cursor()


# TODO: adding admins
def add_user(user_id: int, username: str, olymp_role: str):
    if not check_existing(user_id):
        cur.execute("INSERT INTO users VALUES(?, ?, 0, ?)", (user_id, username, convert_role(olymp_role)))
    conn.commit()


def add_admin(user_id: int, username: str, olymp_role: str = "tt"):
    if check_existing(user_id):
        cur.execute("UPDATE users SET bot_role = 1 WHERE id = ?", (user_id,))
    else:
        cur.execute("INSERT INTO users VALUES(?, ?, 1, ?)", (user_id, username, convert_role(olymp_role)))
    conn.commit()

def get_users():
    return cur.execute("SELECT * FROM users").fetchall()


def get_admins():
    return cur.execute("SELECT * FROM users WHERE bot_role = 1").fetchall()


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


def get_roles(user_id: int):
    res = cur.execute('SELECT bot_role, olymp_role FROM users WHERE id = ?', (user_id,)).fetchall()
    return res




# if __name__ == "__main__":
