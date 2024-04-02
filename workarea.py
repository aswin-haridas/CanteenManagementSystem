import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')
cursor.executemany('''
    INSERT INTO users (id, name, email, role) VALUES (?, ?, ?, ?)
''', [
    (5041, 'gayathri', 'gayathri@cse', 'customer'),
    (5042, 'devika', 'devika@cse', 'customer'),
    (5043, 'kavya', 'kavya@cse', 'customer'),
    (5044, 'manu', 'manu@cse', 'customer'),
    (5045, 'neha', 'neha@cse', 'customer'),
    (5046, 'rahan', 'rahan@cse', 'customer'),
    (5047, 'anagha', 'anagha@cse', 'customer'),
    (5048, 'prarthana', 'prarthana@cse', 'customer'),
    (5049, 'farhan', 'farhan@cse', 'customer'),
    (5050, 'tony', 'tony@cse', 'customer'),
    (5051, 'arun', 'arun@cse', 'customer'),
    (5052, 'lakshmi', 'lakshmi@cse', 'customer'),
    (5053, 'manoj', 'manoj@cse', 'manager'),
    (5054, 'anjali', 'anjali@cse', 'customer'),
    (5055, 'sreejith', 'sreejith@cse', 'customer'),
    (5056, 'nikhil', 'nikhil@cse', 'admin')
])

conn.commit()
conn.close()
