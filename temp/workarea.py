import sqlite3

# Connect to the first database
conn1 = sqlite3.connect('canteen.db')
c1 = conn1.cursor()

# Connect to the second database
conn2 = sqlite3.connect('student.db')
c2 = conn2.cursor()

# Create a new database to store the merged data
conn3 = sqlite3.connect('merged.db')
c3 = conn3.cursor()

# Create tables in the merged database
c3.execute("CREATE TABLE IF NOT EXISTS canteen (id INTEGER PRIMARY KEY, item TEXT, price REAL)")
c3.execute("CREATE TABLE IF NOT EXISTS student (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")

# Copy data from the first database to the merged database
for row in c1.execute("SELECT * FROM canteen"):
    c3.execute("INSERT INTO canteen VALUES (?, ?, ?)", row)

# Copy data from the second database to the merged database
for row in c2.execute("SELECT * FROM student"):
    c3.execute("INSERT INTO student VALUES (?, ?, ?)", row)

# Commit the changes and close the connections
conn3.commit()
conn1.close()
conn2.close()
conn3.close()
