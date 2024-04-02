
import sqlite3

conn = sqlite3.connect('canteen.db')
cursor = conn.cursor()

cursor.execute('CREATE TABLE Cart (id INTEGER PRIMARY KEY, item_id INTEGER, item_name TEXT, price REAL, quantity INTEGER, ordered_by INTEGER)')


