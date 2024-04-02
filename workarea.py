import sqlite3

DATABASE = 'database.db'

def create_users_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Cart (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    price TEXT NOT NULL,
                    quantity TEXT NOT NULL
                    )''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_users_table()
