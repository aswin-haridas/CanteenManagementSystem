import sqlite3

DATABASE = 'canteen.db'

def create_users_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL,
                    score INTEGER NOT NULL
                    )''')

    conn.commit()
    conn.close()

def add_users_with_roles():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    users_with_roles = [
        (0, "admin", "admin", 100),
        (1, "canteen_manager", "canteen manager", 100),
        (435034, "manu", "user", 100),  
    ]

    cursor.executemany("INSERT INTO users (id, username, role, score) VALUES (?, ?, ?, ?)", users_with_roles)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_users_table()
    add_users_with_roles()
