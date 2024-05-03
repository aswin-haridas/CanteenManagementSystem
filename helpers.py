import random
import string
import sqlite3

def generate_receipt_number():
    receipt_number = ''.join(random.choices(string.digits, k=12))
    return receipt_number

def canteen_db():
    conn = sqlite3.connect('canteen.db')
    conn.row_factory = sqlite3.Row
    return conn
def student_db():
    conn = sqlite3.connect('student.db')
    conn.row_factory = sqlite3.Row
    return conn

