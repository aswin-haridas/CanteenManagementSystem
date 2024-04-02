import sqlite3

DATABASE = 'database.db'

def create_users_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Menu (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    price real NOT NULL,
                    image_url text NOT NULL
                    )''')

    conn.commit()
    conn.close()

def add_users_with_roles():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    users_with_roles = [
        ('Appam', 50, 'static/images/appam.jpg'),
        ('Idiyappam', 45, 'static/images/idiyappam.jpg'),
        ('Puttu', 40, 'static/images/puttu.jpg'),
        ('Kerala Parotta', 45, 'static/images/porotta.jpg'),
        ('Thalassery Biriyani', 120, 'static/images/biriyani.jpg'),
        ('Kerala Fish Curry', 150, 'static/images/fishcurry.jpg'),
        ('Avial', 80, 'static/images/avial.jpg'),
        ('Sadya', 200, 'static/images/sadya.jpg')
    ]

    cursor.executemany("INSERT INTO Menu (name, price, image_url) VALUES (?, ?, ?)", users_with_roles)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_users_table()
    add_users_with_roles()
