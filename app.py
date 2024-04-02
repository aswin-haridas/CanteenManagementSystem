from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'canteen.db'
app.secret_key = 'super_secret_key'


@app.context_processor
def common_icons():
    admin = "/static/assets/admin.png"
    customer = "/static/assets/customer.png"
    manager = "/static/assets/manager.png"
    editimage="/static/assets/edit.png"

    return dict(
        admin=admin,
        manager=manager,
        customer=customer,
        editimage=editimage
    )


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user:
            session['userid'] = user['id']
            session['user_type'] = user['role']
            session['user_name'] = user['username']
            
            if user['role'] == 'admin':
                return redirect(url_for('usermgmt'))
            session['logged_in'] = True
            return redirect(url_for('home', username=username))  # Sending the username to home.html
        else:
            return render_template('error.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        conn.execute('INSERT INTO users(username, password) VALUES (?,?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/home')
def home():
    conn = get_db_connection()
    menu_cursor = conn.execute('SELECT * FROM Menu')  
    menu_items = menu_cursor.fetchall()
    cart_cursor = conn.execute('SELECT * FROM Cart')
    cart_items = cart_cursor.fetchall()
    total_price = sum(item['price'] for item in cart_items)
    conn.close()
    return render_template('home.html', menu_items=menu_items, cart_items=cart_items, total_price=total_price)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    conn = get_db_connection()  
    item = conn.execute('SELECT name, price FROM Menu WHERE id = ?', (item_id,)).fetchone()
    existing_item = conn.execute('SELECT * FROM Cart WHERE item_id = ?', (item_id,)).fetchone()
    if existing_item:
        new_quantity = existing_item['quantity'] + 1  
        conn.execute('UPDATE Cart SET quantity = ? WHERE item_id = ?', (new_quantity, existing_item['item_id']))
    else:
        conn.execute('INSERT INTO Cart (item_id, item_name, price, quantity) VALUES (?, ?, ?, ?)', (item_id, item['name'], item['price'], 1))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<string:item_name>', methods=['POST'])  
def remove_from_cart(item_name):  
    conn = get_db_connection()
    existing_item = conn.execute('SELECT * FROM Cart WHERE item_name = ?', (item_name,)).fetchone()  
    if existing_item:
        new_quantity = existing_item['quantity'] - 1  
        if new_quantity <= 0:
            conn.execute('DELETE FROM Cart WHERE item_name = ?', (item_name,))  
        else:
            conn.execute('UPDATE Cart SET quantity = ? WHERE item_name = ?', (new_quantity, item_name))  
        conn.commit()
    conn.close()
    return redirect(url_for('home'))


@app.route("/profile")
def profile():
    user_id = session.get("userid")
    user_type = session.get("user_type")

    if user_id is None:
        return "User ID not found"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, dob, email, department, contact, address, pfp FROM customers WHERE id=?", (user_id,))
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





@app.route('/checkout')
def checkout():
    conn = get_db_connection()
    conn.execute('DELETE FROM Cart')
    conn.commit()
    conn.close()
    return render_template('checkout.html')

@app.route('/usermgmt')
def usermgmt():
    conn = get_db_connection()
    users_cursor = conn.execute('SELECT * FROM users')
    users_data = users_cursor.fetchall()
    return render_template('usermgmt.html' , users_data=users_data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)
