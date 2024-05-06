import sqlite3

# Create a new SQLite database or connect to an existing one
conn = sqlite3.connect('canteen.db')
cursor = conn.cursor()
# Create PurchaseRecords table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS PurchaseRecords (
        id INTEGER PRIMARY KEY,
        menu_id INTEGER
    )
''')
# Commit the changes and close the connection
conn.commit()
conn.close()
print("PurchaseRecords table created successfully!")
