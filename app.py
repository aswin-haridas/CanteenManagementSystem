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
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    menu_items = cursor.fetchall()
    conn.close()
    return render_template('home.html', menu_items=menu_items)


@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    if request.method == 'POST':
        item_id = request.form.get('item_id')  # Use request.form.get() to handle missing keys gracefully
        if item_id is not None:  # Check if item_id is present
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cart (item_id) VALUES (?)", (item_id,))
            conn.commit()
            conn.close()
    return redirect(url_for('home'))


@app.route('/view_cart')
def view_cart():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cart JOIN menu ON cart.item_id = menu.id")
    cart_items = cursor.fetchall()
    conn.close()
    return render_template('cart.html', cart_items=cart_items)


if __name__ == '__main__':
    app.run(debug=True)
