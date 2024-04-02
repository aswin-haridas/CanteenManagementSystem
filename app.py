from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'supersecretkey'  
DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/home')
def home():
    current_user = session.get('user_id', 1)  
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

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role, username FROM users WHERE username=? AND password=?",
            (username, password),
        )
        result = cursor.fetchone()

        if result is not None:
            user_id, user_type, name = result
            session["user_id"] = user_id
            session["user_type"] = user_type
            session["username"] = username
            session["name"] = name

            if user_type_form == user_type:
                return redirect(url_for("home"))
        error_message = "Invalid username or password"
        return render_template("error.html", error=error_message)

    return render_template("login.html")

@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    user_type = session.get("user_type")

    if user_id is None:
        return "User ID not found"

    conn = get_db_connection()
    cursor = conn.cursor()

    if user_type == "customer":
        cursor.execute("SELECT id, name, dob, email, course, contact, address, pfp FROM studentlist WHERE id=?", (user_id,))
        user_info = cursor.fetchone()
        if user_info is None:
            conn.close()
            return "User not found"

        id, name, dob, email, course, contact, address, pfp = user_info
        conn.close()
        return render_template(
            "profile.html",
            id=id,
            user_type=user_type,
            name=name,
            dob=dob,
            email=email,
            pfp=pfp,
            course=course,
            contact=contact,
            address=address,
        )
    
    elif user_type == "manager":
        cursor.execute("SELECT id, name, dob, email, department, contact, address, pfp FROM facultylist WHERE id=?", (user_id,))
        user_info = cursor.fetchone()
        if user_info is None:
            conn.close()
            return "User not found"

        id, name, dob, email, department, contact, address, pfp = user_info
        conn.close()
        return render_template(
            "profile.html",
            id=id,
            user_type=user_type,
            name=name,
            dob=dob,
            email=email,
            pfp=pfp,
            course=department,
            contact=contact,
            address=address,
        )
    elif user_type == "admin":
        cursor.execute("SELECT id, name, dob, email, department, contact, address, pfp FROM facultylist WHERE id=?", (user_id,))
        user_info = cursor.fetchone()
        if user_info is None:
            conn.close()
            return "User not found"

        id, name, dob, email, department, contact, address, pfp = user_info
        conn.close()
        return render_template(
            "profile.html",
            id=id,
            user_type=user_type,
            name=name,
            dob=dob,
            email=email,
            pfp=pfp,
            course=department,
            contact=contact,
            address=address,
        )

    return "User not found"

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    if request.method == 'POST':
        current_user = session.get('user_id')  
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
    if request.method == 'POST':
        current_user = session.get('user_id')  
        conn = get_db_connection()
        conn.execute('DELETE FROM Cart WHERE item_id = ? AND ordered_by = ?', (item_id, current_user))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    else:
        return redirect(url_for("login"))

@app.route('/checkout')
def checkout():
    current_user = session.get('user_id')  
    conn = get_db_connection()
    conn.execute('DELETE FROM Cart WHERE user_id = ?', (current_user,))
    conn.commit()
    conn.close()
    return render_template('checkout.html')


if __name__ == '__main__':
    app.run(debug=True)
