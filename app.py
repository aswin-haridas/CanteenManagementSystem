from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

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

@app.route('/home')
def home():
    current_user = session.get('user_item_id', 1)  
    conn = get_db_connection()
    menu_cursor = conn.execute('SELECT * FROM Menu')
    menu_items = menu_cursor.fetchall()
    cart_cursor = conn.execute('SELECT * FROM Cart')
    cart_items = cart_cursor.fetchall()
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    conn.close()
    return render_template('home.html', menu_items=menu_items, cart_items=cart_items, total_price=total_price)


@app.route('/user_management')
def user_management():
    name=session.get("name")
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')
    users_data = cursor.fetchall()
    connection.close()
    return render_template('usermgmt.html', users_data=users_data,name=name)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_type_form = request.form.get("user-type")
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT item_id, role, username FROM users WHERE username=? AND password=?",
            (username, password),
        )
        result = cursor.fetchone()

        if result is not None:
            user_item_id, user_type, name = result
            session["user_item_id"] = user_item_id
            session["user_type"] = user_type
            session["username"] = username
            session["name"] = name

            if user_type_form == user_type:
                if user_type == 'admin':
                    return redirect(url_for("user_management"))
                else:
                    return redirect(url_for("home"))
        error_message = "Invalid username or password"
        return render_template("error.html", error=error_message)

    return render_template("login.html")

@app.route("/profile")
def profile():
    user_item_id = session.get("user_item_id")
    user_type = session.get("user_type")

    if user_item_id is None:
        return "User item_id not found"

    conn = get_db_connection()
    cursor = conn.cursor()

    if user_type == "customer":
        cursor.execute("SELECT item_id, name, dob, email, course, contact, address, pfp FROM user WHERE item_id=?", (user_item_id,))
        user_info = cursor.fetchone()
        if user_info is None:
            conn.close()
            return "User not found"

        item_id, name, dob, email, course, contact, address, pfp = user_info
        conn.close()
        return render_template(
            "profile.html",
            item_id=item_id,
            user_type=user_type,
            name=name,
            dob=dob,
            email=email,
            pfp=pfp,
            course=course,
            contact=contact,
            address=address,
        )
    return "User not found"

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    if request.method == 'POST':
        current_user = session.get('user_item_id')  
        conn = get_db_connection()
        existing_item = conn.execute('SELECT * FROM Cart WHERE item_id = ? AND user_item_id = ?', (item_id, current_user)).fetchone()
        if existing_item:
            new_quantity = existing_item['quantity'] + 1
            conn.execute('UPDATE Cart SET quantity = ? WHERE item_id = ?', (new_quantity, existing_item['item_id']))
        else:
            conn.execute('INSERT INTO Cart (item_id, quantity, user_item_id) VALUES (?, ?, ?)', (item_id, 1, current_user))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if request.method == 'POST':
        current_user = session.get('user_item_id')  
        conn = get_db_connection()
        conn.execute('DELETE FROM Cart WHERE item_id = ? AND user_item_id = ?', (item_id, current_user))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

@app.route('/checkout')
def checkout():
    current_user = session.get('user_item_id')  
    conn = get_db_connection()
    conn.execute('DELETE FROM Cart WHERE user_item_id = ?', (current_user,))
    conn.commit()
    conn.close()
    return render_template('checkout.html')


if __name__ == '__main__':
    app.run(debug=True)
