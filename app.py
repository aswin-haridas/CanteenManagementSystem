from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Secret key for session management
DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    current_user = session.get('user_id', 1)  # Get user_id from session or default to 1
    conn = get_db_connection()
    menu_cursor = conn.execute('SELECT * FROM Menu')
    menu_items = menu_cursor.fetchall()
    cart_cursor = conn.execute('SELECT ci.id, mi.name, mi.price, ci.quantity FROM Cart ci JOIN Menu mi ON ci.item_id = mi.id WHERE ci.user_id = ?', (current_user,))
    cart_items = cart_cursor.fetchall()
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    conn.close()
    return render_template('home.html', menu_items=menu_items, cart_items=cart_items, total_price=total_price)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add authentication logic here
        # For example, check if username and password match a user in the database
        # If authentication is successful, set the user_id in the session
        session['user_id'] = 1  # Set user_id to 1 for now, replace with actual user_id
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    if request.method == 'POST':
        current_user = session.get('user_id', 1)  # Get user_id from session or default to 1
        conn = get_db_connection()
        existing_item = conn.execute('SELECT * FROM Cart WHERE item_id = ? AND user_id = ?', (item_id, current_user)).fetchone()
        if existing_item:
            new_quantity = existing_item['quantity'] + 1
            conn.execute('UPDATE Cart SET quantity = ? WHERE id = ?', (new_quantity, existing_item['id']))
        else:
            conn.execute('INSERT INTO Cart (item_id, quantity, user_id) VALUES (?, ?, ?)', (item_id, 1, current_user))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if request.method == 'POST':
        current_user = session.get('user_id', 1)  # Get user_id from session or default to 1
        conn = get_db_connection()
        conn.execute('DELETE FROM Cart WHERE item_id = ? AND user_id = ?', (item_id, current_user))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

@app.route('/checkout')
def checkout():
    current_user = session.get('user_id', 1)  # Get user_id from session or default to 1
    conn = get_db_connection()
    conn.execute('DELETE FROM Cart WHERE user_id = ?', (current_user,))
    conn.commit()
    conn.close()
    return render_template('checkout.html')


if __name__ == '__main__':
    app.run(debug=True)
