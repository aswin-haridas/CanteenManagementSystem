import sqlite3

# Create a new SQLite database or connect to an existing one
conn = sqlite3.connect('canteen.db')
cursor = conn.cursor()

# Create Menu table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Report (
        id INTEGER PRIMARY KEY,
        item_name TEXT,
        item_price REAL,
        item_quantity INTEGER,
        ordered_by TEXT,
        timestamp TEXT
    )
''')
# Commit the changes and close the connection
conn.commit()
conn.close()

print("Menu items added successfully!")
