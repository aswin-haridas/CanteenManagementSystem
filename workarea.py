import sqlite3

db = sqlite3.connect("student.db")

cursor = db.cursor()

sql_create_users = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
"""

# Execute the SQL statement to create 'users' table
cursor.execute(sql_create_users)

sql_insert = """
INSERT INTO users (username, password)
SELECT University_Reg_No, University_Reg_No
FROM students;
"""

cursor.execute(sql_insert)

db.commit()

db.close