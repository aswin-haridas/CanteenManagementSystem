import sqlite3

conn = sqlite3.connect('canteen.db')
c = conn.cursor()

c.execute("DELETE FROM Orders")
conn.commit()

conn.close()
