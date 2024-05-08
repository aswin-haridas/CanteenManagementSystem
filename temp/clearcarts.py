import sqlite3

with sqlite3.connect('canteen.db') as conn:
    conn.execute("DELETE FROM Orders")
    conn.commit()

with sqlite3.connect('student.db') as conn:
    conn.execute("UPDATE users SET score = 100, purchasecount = 0")
    conn.commit()
conn.close()
