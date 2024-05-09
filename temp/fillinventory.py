import sqlite3


with sqlite3.connect('canteen.db') as conn:
    conn.execute("UPDATE Menu SET quantity = 20 WHERE quantity != 20")
    conn.commit()
conn.close()

#fill random demerits 0-10 in menu
with sqlite3.connect('canteen.db') as conn:
    conn.execute("UPDATE Menu SET demerit = random() * 10")
    conn.commit()
conn.close()