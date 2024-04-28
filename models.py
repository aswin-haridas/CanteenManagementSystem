import sqlite3


def canteen_db():
    conn = sqlite3.connect('canteen.db')
    conn.row_factory = sqlite3.Row
    return conn

def student_db():
    conn = sqlite3.connect('student.db')
    conn.row_factory = sqlite3.Row
    return conn
