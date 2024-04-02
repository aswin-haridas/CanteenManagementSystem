from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DATABASE = 'database.db'

@app.context_processor
def common_icons():
    icons = {
        'admin': "/static/assets/admin.png",
        'customer': "/static/assets/customer.png",
        'manager': "/static/assets/canteen-manager.png",
        'editimage': "/static/assets/edit.png"
    }
    return icons

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_type = request.form.get("user-type")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role, username FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = user['username']
            session['user_type'] = user['role']
            if user_type == 'admin':
                return render_template('usermgmt.html')
            else:
                return redirect(url_for('home'))
        else:
            return render_template('error.html')
    return render_template('login.html')
        

@app.route('/home')
def home():
    current_user = session.get('username')
    if current_user:
        conn = get_db_connection()
        menu_cursor = conn.execute('SELECT * FROM Menu')
        menu_items = menu_cursor.fetchall()
        cart_cursor = conn.execute('SELECT * FROM Cart WHERE ordered_by = ?', (current_user,))
        cart_items = cart_cursor.fetchall()
        total_price = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
        conn.close()
        return render_template('home.html', current_user=current_user, menu_items=menu_items, cart_items=cart_items, total_price=total_price)
    else:
        return redirect(url_for("login"))

@app.route('/user_management')
def user_management():
    if session.get('user_type') == 'admin':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users_data = cursor.fetchall()
        conn.close()
        return render_template('usermgmt.html', users_data=users_data)
    else:
        flash("You don't have permission to access this page.", 'error')
        return redirect(url_for("login"))

@app.route("/profile")
def profile():
    current_user = session.get("username")
    if current_user:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (current_user,))
        user_info = cursor.fetchone()

        if user_info:
            return render_template("profile.html", user_info=user_info)
        else:
            flash("User not found", 'error')
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    current_user = session.get('username')
    if current_user:
        conn = get_db_connection()
        item = conn.execute('SELECT name, price FROM Menu WHERE id = ?', (item_id,)).fetchone()
        existing_item = conn.execute('SELECT * FROM Cart WHERE item_id = ? AND ordered_by = ?', (item_id, current_user)).fetchone()
        if existing_item:
            new_quantity = str(existing_item['quantity'] + 1)
            conn.execute('UPDATE Cart SET quantity = ? WHERE item_id = ?', (new_quantity, existing_item['item_id']))
        else:
            conn.execute('INSERT INTO Cart (item_id, item_name, price, quantity, ordered_by) VALUES (?, ?, ?, ?, ?)', (item_id, item['name'], item['price'], 1, current_user))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    else:
        return redirect(url_for("login"))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    current_user = session.get('username')
    if current_user:
        conn = get_db_connection()
        conn.execute('DELETE FROM Cart WHERE item_id = ? AND ordered_by = ?', (item_id, current_user))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    else:
        return redirect(url_for("login"))

@app.route('/checkout')
def checkout():
    current_user = session.get('username')
    if current_user:
        conn = get_db_connection()
        conn.execute('DELETE FROM Cart WHERE ordered_by = ?', (current_user,))
        conn.commit()
        conn.close()
        return render_template('checkout.html')
    else:
        return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)
