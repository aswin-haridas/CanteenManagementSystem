from datetime import datetime
import random
import string
from flask import Flask, abort, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
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

def canteen_db():
    conn = sqlite3.connect('canteen.db')
    conn.row_factory = sqlite3.Row
    return conn

def student_db():
    conn = sqlite3.connect('student.db')
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = student_db()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user:
            session['userid'] = user['id']
            session['user_type'] = user['role']
            session['user_name'] = user['username']
            if user['role'] == 'admin':
                return redirect(url_for('usermgmt'))
            elif user['role'] =='manager':
                return redirect(url_for('manager'))
            session['logged_in'] = True
            return redirect(url_for('home', username=username)) 
        else:
            return render_template('error.html')
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        conn = student_db()
        conn.execute('INSERT INTO users VALUES (NULL,?,?,?)', (request.form['username'], request.form['password'],request.form['user-type']))
        conn.commit()
        conn.close()
    return redirect(url_for('login'))



@app.route('/home',methods=['GET', 'POST'])
def home():
    
    conn = sqlite3.connect('canteen.db')
    conn.row_factory = sqlite3.Row
    menu_cursor = conn.execute('SELECT * FROM Menu')
    menu_items = menu_cursor.fetchall()
    cart_cursor = conn.execute('SELECT * FROM Cart') 
    cart_items = cart_cursor.fetchall()
    total_price = 0
    for item in cart_items:
        total_price += item['price'] * item['quantity']
    conn.close()
    return render_template('home.html', menu_items=menu_items, cart_items=cart_items, total_price=total_price )

@app.route('/add_to_cart/<int:menu_id>', methods=['POST'])
def add_to_cart(menu_id):
    username= session.get("user_name")

    db = student_db()
    cursor = db.cursor()
    cursor.execute("SELECT score FROM users WHERE username = ?", (username,))
    score = cursor.fetchone()[0]
    db.commit()
    db.close()

    with canteen_db() as conn:
        menu_item = conn.execute(
            'SELECT name, price FROM Menu WHERE id = ?', (menu_id,)).fetchone()
        cart_item = conn.execute(
            'SELECT * FROM Cart WHERE id = ?', (menu_id,)).fetchone()
        if cart_item:
            new_quantity = cart_item['quantity'] + 1
            conn.execute(
                'UPDATE Cart SET quantity = ? WHERE id = ?',
                (new_quantity, cart_item['id']))
        else:
            conn.execute(
                'INSERT or IGNORE INTO Cart (id, name, price, quantity , ordered_by,customer_score ,status) VALUES (?, ?, ?, ?, ?, ?, "ordered")',
                (menu_id, menu_item['name'], menu_item['price'], 1, username, score))
            conn.commit()
            # conn.execute(
            #     'INSERT or IGNORE INTO Orders (id, name, price, quantity , ordered_by,customer_score ,status) VALUES (?, ?, ?, ?, ?, ?, "ordered")',
            #     (menu_id, menu_item['name'], menu_item['price'], 1, username, score))
            # conn.commit()
            
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<string:name>', methods=['POST'])  
def remove_from_cart(name):  
    conn = canteen_db()
    existing_item = conn.execute('SELECT * FROM Cart WHERE name = ?', (name,)).fetchone()  
    if existing_item:
        new_quantity = existing_item['quantity'] - 1  
        if new_quantity <= 0:
            conn.execute('DELETE FROM Cart WHERE name = ?', (name,))  
        else:
            conn.execute('UPDATE Cart SET quantity = ? WHERE name = ?', (new_quantity, name))  
        conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/checkout')
def checkout():
    conn = canteen_db()
    cart_items = conn.execute('SELECT * FROM Cart').fetchall()
    total_price = 0
    for item in cart_items:
        total_price += item['price'] * item['quantity']
    
    receipt_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    for item in cart_items:
        conn.execute(
            'INSERT INTO Orders (id, name, price, quantity, ordered_by, customer_score, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (item['id'], item['name'], item['price'], item['quantity'], item['ordered_by'], item['customer_score'], item['status']))
    conn.commit()
          
    conn.execute('DELETE FROM Cart')
    conn.commit()
    conn.close()
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, receipt_number=receipt_number)

@app.route('/processing')
def processing():
    return render_template('processing.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    username = session.get("user_name")
    if not username:
        return abort(404)

    conn = student_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE University_Reg_No=?", (username,))
    user_info = cursor.fetchone()
    conn.close()

    if not user_info:
        return abort(404)

    return render_template(
        "profile.html",
        student_id=user_info["Student_ID"],
        admission_no=user_info["Admission_No"],
        sl_no=user_info["Sl_No"],
        roll_no=user_info["Roll_No"],
        admission_number=user_info["Admission_No"],
        university_reg_no=user_info["University_Reg_No"],
        department=user_info["Department"],
        batch=user_info["Batch"],
        primary_email_id=user_info["Primary_Email_ID"],
        gender=user_info["Gender"],
        date_of_birth=user_info["Date_of_Birth"],
        birth_place=user_info["Birth_Place"],
        state=user_info["State"],
        admission_date=user_info["Admission_Date"],
        current_address=user_info["Current_Address"],
        permanent_address=user_info["Permenant_Address"],
        student_phone=user_info["Student_Phone"],
        parent_phone=user_info["Parent_Phone"],
        religion=user_info["Religion"],
        caste=user_info["Caste"],
        pfp=user_info["pfp"]
    )


@app.route('/orders')
def orders():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user = session['user_name']

    with canteen_db() as conn:
        orders = conn.execute('SELECT * FROM orders WHERE ordered_by = ?', (user,)).fetchall()

    return render_template('orders.html', orders=orders)
    
@app.route('/delete_order', methods=['POST'])
def delete_order():
    order_id = request.form.get('order_id')
    with canteen_db() as conn:
        conn.execute('DELETE FROM Orders WHERE id = ?', (order_id,))
        conn.commit()
    return redirect('/orders')

@app.route('/usermgmt')
def usermgmt():
    conn = student_db()
    users_cursor = conn.execute('SELECT * FROM users')
    users_data = users_cursor.fetchall()
    return render_template('usermgmt.html' , users_data=users_data)
    
@app.route('/edit_user', methods=['POST'])
def edit_user():
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    score = request.form.get('score')
    with student_db() as conn:
        conn.execute('UPDATE users SET username = ?, password = ?, role = ? ,score = ? WHERE id = ?', (username, password, role, score, user_id))
        conn.commit()
    return redirect('/usermgmt')


@app.route('/manager')
def manager():
    with canteen_db() as conn:
        menu = conn.execute('SELECT * FROM Menu').fetchall()
        orders = conn.execute('SELECT * FROM Orders').fetchall()
        reports = conn.execute('SELECT * FROM Reports').fetchall()
    return render_template('cmanager.html', menu=menu, orders=orders , reports=reports)

@app.route('/accept_order', methods=['POST'])
def accept_order():
    order_id = request.form.get('order_id')
    with canteen_db() as conn:
        conn.execute('UPDATE Orders SET status = ? WHERE id = ?', ('accepted', order_id))
        conn.commit()
    return redirect('/manager')

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    order_id = request.form.get('order_id')
    with canteen_db() as conn:
        conn.execute('UPDATE Orders SET status = ? WHERE id = ?', ('cancelled', order_id))
        conn.commit()
        conn.execute('DELETE FROM Orders WHERE id = ?', (order_id,))
        conn.commit()
    return redirect('/manager')

@app.route('/served_order', methods=['POST'])
def served_order():
    order_id = request.form['order_id']
    with canteen_db() as conn:
        order = conn.execute('SELECT * FROM Orders WHERE id = ?', (order_id,)).fetchone()
        conn.execute("""
            INSERT INTO Reports (item_name, item_price, ordered_by, item_quantity, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """, (order['name'], order['price'], order['ordered_by'], order['quantity'],
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.execute('UPDATE Orders SET status = ? WHERE id = ?', ('served', order_id))
        conn.commit()
        conn.execute('DELETE FROM Orders WHERE id = ?', (order_id,))
        conn.commit()
    return redirect('/manager')


@app.route('/edit_item', methods=['POST'])
def edit_item():

    item_id = request.form['item_id']
    item_name = request.form['item_name']
    item_price = request.form['item_price']
    item_image = request.form['item_image']
    item_availability = request.form['item_availability']
    item_food_type = request.form['item_food_type']

    
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()

  
    cursor.execute("""
        UPDATE menu 
        SET name=?, price=?, image_url=?, availability=?, foodtype=?
        WHERE id=?
    """, (item_name, item_price, item_image, item_availability, item_food_type, item_id))

    conn.commit()
    conn.close()
    return redirect('/manager')

@app.route('/delete_item', methods=['POST'])
def delete_item():
    item_id = request.form.get('item_id')
    with canteen_db() as conn:
        conn.execute('DELETE FROM Menu WHERE id = ?', (item_id,))
        conn.commit()
    return redirect('/manager')


if __name__ == '__main__':
    app.run(debug=True)
