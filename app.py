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
    menu_cursor = conn.execute('SELECT * FROM Menu')  # Ensure table name is correct
    menu_items = menu_cursor.fetchall()
    cart_cursor = conn.execute('SELECT * FROM Cart')
    cart_items = cart_cursor.fetchall()
    total_price = 100
    conn.close()
    return render_template('home.html', menu_items=menu_items, cart_items=cart_items, total_price=total_price)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    conn = get_db_connection()  # Use get_db_connection function to connect to the database
    item = conn.execute('SELECT name, price FROM Menu WHERE id = ?', (item_id,)).fetchone()
    existing_item = conn.execute('SELECT * FROM Cart WHERE item_id = ?', (item_id,)).fetchone()
    if existing_item:
        new_quantity = existing_item['quantity'] + 1  # Increment quantity directly
        conn.execute('UPDATE Cart SET quantity = ? WHERE item_id = ?', (new_quantity, existing_item['item_id']))
    else:
        conn.execute('INSERT INTO Cart (item_id, item_name, price, quantity) VALUES (?, ?, ?, ?)', (item_id, item['name'], item['price'], 1))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<string:item_name>', methods=['POST'])  # Changed item_id to item_name
def remove_from_cart(item_name):  # Changed item_id to item_name
    conn = get_db_connection()
    existing_item = conn.execute('SELECT * FROM Cart WHERE item_name = ?', (item_name,)).fetchone()  # Changed item_id to item_name
    if existing_item:
        new_quantity = existing_item['quantity'] - 1  # Decrement quantity directly
        if new_quantity <= 0:
            conn.execute('DELETE FROM Cart WHERE item_name = ?', (item_name,))  # Changed item_id to item_name
        else:
            conn.execute('UPDATE Cart SET quantity = ? WHERE item_name = ?', (new_quantity, item_name))  # Changed item_id to item_name
        conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/checkout')
def checkout():
    conn = get_db_connection()
    conn.execute('DELETE FROM Cart')
    conn.commit()
    conn.close()
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(debug=True)
