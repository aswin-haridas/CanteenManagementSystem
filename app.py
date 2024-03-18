import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///canteen.db"
app.secret_key = "your_secret_key_here"

def get_items_from_database():
    conn = sqlite3.connect("canteen.db")
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, price FROM menu")
    items = cursor.fetchall()
    conn.close()
    return items

@app.route('/')
def home():
    items = get_items_from_database()
    return render_template('home.html', items=items)

if __name__ == "__main__":
    app.run(debug=True)

