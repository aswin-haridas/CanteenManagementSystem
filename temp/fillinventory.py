import random
import sqlite3

# Connect to the SQLite database
with sqlite3.connect('canteen.db') as conn:
    # Fetch all rows from the Menu table
    cursor = conn.cursor()
    cursor.execute("SELECT rowid FROM Menu")
    rows = cursor.fetchall()
    
    # Update each row with a different random demerit value
    for row in rows:
        demerit = random.randint(1, 10)
        conn.execute("UPDATE Menu SET demerit = ? WHERE rowid = ?", (demerit, row[0]))
    
    # Commit the changes
    conn.commit()
