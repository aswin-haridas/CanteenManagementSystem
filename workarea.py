import sqlite3

# Connect to the database
conn = sqlite3.connect('canteen.db')
cursor = conn.cursor()

# Create a menu table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS menu (
                    id INTEGER PRIMARY KEY,
                    item_name TEXT NOT NULL,
                    price TEXT NOT NULL
                )''')

# Insert menu items
menu_items = [
    ("Puttu", "₹20"),
    ("Idiyappam", "₹30"),
    ("Dosa", "₹15"),
    ("Pazhampozhi", "₹20"),
    ("Appam", "₹15"),
    ("Kanji", "₹10"),
    ("Kaadayirachi", "₹25"),
    ("Fish Curry", "₹40"),
    ("Avial", "₹35"),
    ("Kappa and Meen Curry", "₹45"),
    ("Thalassery Biryani", "₹50"),
    ("Kerala Porotta", "₹25"),
    ("Prawn Fry", "₹60"),
    ("Erachi Varutharacha Curry", "₹40"),
    ("Kozhikode Halwa", "₹20")
]

cursor.executemany('''INSERT INTO menu (item_name, price)
                      VALUES (?, ?)''', menu_items)

# Commit changes and close the connection
conn.commit()
conn.close()
