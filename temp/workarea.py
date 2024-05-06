import sqlite3

# Create a new SQLite database or connect to an existing one
conn = sqlite3.connect('student.db')
cursor = conn.cursor()

# Create Purchase table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Purchase (
        id INTEGER PRIMARY KEY,
        username TEXT,
        purchase_count INTEGER
    )
''')
# Commit the changes and close the connection
conn.commit()
conn.close()

print("Purchase table created successfully!")
