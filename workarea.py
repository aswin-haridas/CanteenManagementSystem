import sqlite3

conn = sqlite3.connect('canteen.db')
cursor = conn.cursor()

cursor.execute("UPDATE customers SET id = id + 5040 - 1")

# Commit changes  
conn.commit()

# Close connection
conn.close()
