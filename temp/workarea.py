import sqlite3

# Create a new SQLite database or connect to an existing one
conn = sqlite3.connect('canteen.db')
cursor = conn.cursor()

# Create Menu table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Menu (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        image_url TEXT
    )
''')

# Sample snack and drink items from Kerala
menu_items = [
    {
        'name': 'Samosa',
        'price': 20.0,
        'image_url': 'static/samosa.jpg'
    },
    {
        'name': 'Banana Chips',
        'price': 50.0,
        'image_url': 'static/banana_chips.jpg'
    },
    {
        'name': 'Masala Dosa',
        'price': 70.0,
        'image_url': 'static/masala_dosa.jpg'
    },
    {
        'name': 'Tea',
        'price': 15.0,
        'image_url': 'static/tea.jpg'
    },
    {
        'name': 'Appam',
        'price': 60.0,
        'image_url': 'static/appam.jpg'
    },
    {
        'name': 'Uzhunnu Vada',
        'price': 40.0,
        'image_url': 'static/uzhunnu_vada.jpg'
    },
    {
        'name': 'Pazham Pori (Banana Fritters)',
        'price': 30.0,
        'image_url': 'static/pazham_pori.jpg'
    },
    {
        'name': 'Lemon Soda',
        'price': 25.0,
        'image_url': 'static/lemon_soda.jpg'
    },
    {
        'name': 'Thannermathan joos',
        'price': 40.0,
        'image_url': 'static/coconut_water.jpg'
    }
]

# Insert sample menu items into Menu table
for item in menu_items:
    cursor.execute('''
        INSERT INTO Menu (name, price, image_url)
        VALUES (?, ?, ?)
    ''', (item['name'], item['price'], item['image_url']))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Menu items added successfully!")
