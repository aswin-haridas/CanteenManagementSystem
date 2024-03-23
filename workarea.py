import sqlite3

DATABASE = 'canteen.db'

def add_kerala_food_items():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Insert Kerala food items into the menu table
    kerala_food_items = [
        ("Appam", 50),
        ("Puttu", 40),
        ("Idiyappam", 60),
        ("Kerala Parotta", 45),
        ("Thalassery Biriyani", 120),
        ("Kerala Fish Curry", 150),
        ("Avial", 80),
        ("Sadya", 200)
    ]

    cursor.executemany("INSERT INTO menu (name, price) VALUES (?, ?)", kerala_food_items)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_kerala_food_items()
