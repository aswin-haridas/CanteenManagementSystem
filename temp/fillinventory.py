import sqlite3


with sqlite3.connect('canteen.db') as conn:
    conn.execute("UPDATE Menu SET quantity = 20 WHERE quantity != 20")
    conn.commit()
conn.close()
