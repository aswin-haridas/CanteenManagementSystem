import random
import string
import sqlite3
from datetime import datetime

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


def increase_purchase_count(username):
    with student_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM Purchase WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO Purchase (username, purchase_count) VALUES (?, 1)",
                (username,),
            )
        else:
            conn.execute(
                "UPDATE Purchase SET purchase_count = purchase_count + 1 WHERE username = ?",
                (username,),
            )
        conn.commit()