# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'canteen.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM menu')
    menu_items = cursor.fetchall()
    conn.close()
    return render_template('home.html', menu_items=menu_items)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    if request.method == 'POST':
        current_user = 1  # Replace with actual user identification
        conn = get_db_connection()
        existing_item = conn.execute('SELECT * FROM cart WHERE item_id = ? AND user_id = ?', (item_id, current_user)).fetchone()
        if existing_item:
            new_quantity = existing_item['quantity'] + 1
            conn.execute('UPDATE cart SET quantity = ? WHERE id = ?', (new_quantity, existing_item['id']))
        else:
            conn.execute('INSERT INTO cart (item_id, quantity, user_id) VALUES (?, ?, ?)', (item_id, 1, current_user))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if request.method == 'POST':
        current_user = 1  # Replace with actual user identification
        conn = get_db_connection()
        conn.execute('DELETE FROM cart WHERE item_id = ? AND user_id = ?', (item_id, current_user))
        conn.commit()
        conn.close()
    return redirect(url_for('view_cart'))

@app.route('/view_cart')
def view_cart():
    current_user = 1  # Replace with actual user identification
    conn = get_db_connection()
    cursor = conn.execute('SELECT ci.id, mi.name, mi.price, ci.quantity FROM Cart ci JOIN Menu mi ON ci.item_id = mi.id WHERE ci.user_id = ?', (current_user,))
    cart_items = cursor.fetchall()
    conn.close()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/checkout')
def checkout():
    current_user = 1  # Replace with actual user identification
    conn = get_db_connection()
    conn.execute('DELETE FROM Cart WHERE user_id = ?', (current_user,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
