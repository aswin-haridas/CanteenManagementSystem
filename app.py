from flask import Flask, abort, jsonify, render_template, request, redirect, session, url_for
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

#login.html----------------------------------------------------------------------------------------------------

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

#signup.html----------------------------------------------------------------------------------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        conn = student_db()
        conn.execute('INSERT INTO users VALUES (NULL,?,?,?)', (request.form['username'], request.form['password'],request.form['user-type']))
        conn.commit()
        conn.close()
    return redirect(url_for('login'))

#home.html----------------------------------------------------------------------------------------

@app.route('/home')
def home():

    #connected to canteen database instead
    conn = sqlite3.connect('canteen.db')
    conn.row_factory = sqlite3.Row

    #fetch menu and cart items
    menu_cursor = conn.execute('SELECT * FROM Menu')
    menu_items = menu_cursor.fetchall()
    cart_cursor = conn.execute('SELECT * FROM Cart') 
    cart_items = cart_cursor.fetchall()

    total_price = 0
    for item in cart_items:
        total_price += item['price'] * item['quantity']
    
    conn.close()
    return render_template('home.html', menu_items=menu_items, cart_items=cart_items, total_price=total_price)


@app.route('/add_to_cart/<int:menu_id>', methods=['POST'])
def add_to_cart(menu_id):
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
                'INSERT INTO Cart (id, name, price, quantity) VALUES (?, ?, ?, ?)',
                (menu_id, menu_item['name'], menu_item['price'], 1))
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
    conn.execute('DELETE FROM Cart')
    conn.commit()
    conn.close()
    return render_template('checkout.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#profile.html----------------------------------------------------------------------------------------
@app.route("/profile")
def profile():
    user_id = session.get("userid")
    if user_id is None:
        return abort(404)

    conn = student_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id=?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()

    if user_info is None:
        return abort(404)

    return render_template(
        "profile.html",
        user_id=user_info["id"],
        user_type=session["user_type"],
        name=user_info["name"],
        dob=user_info["dob"],
        email=user_info["email"],
        pfp=user_info["pfp"],
        course=user_info["department"],
        contact=user_info["contact"],
        address=user_info["address"],
    )


#usermgmt.html----------------------------------------------------------------------------------------

@app.route('/usermgmt')
def usermgmt():
    conn = student_db()
    users_cursor = conn.execute('SELECT * FROM users')
    users_data = users_cursor.fetchall()
    return render_template('usermgmt.html' , users_data=users_data)
    
@app.route('/manager')
def manager():
    conn = canteen_db()
    menu = conn.execute('SELECT * FROM Menu')
    menu = menu.fetchall()
    return render_template('cmanager.html' , menu=menu)

@app.route('/get_item_details', methods=['POST'])
def get_item_details():
    item_id = request.json['itemId']
    
    
    conn = canteen_db()
    items =conn.execute('SELECT * FROM menu WHERE id=?', (item_id,))
    item = items.fetchone()
    conn.close()
    
    item_details = {
        'id': item[0],
        'price': item[1], 
        'availability': item[2],
        'foodType': item[3]
    }
    
    return jsonify(item_details)


@app.route('/edit_item', methods=['POST'])
def edit_item():
    item_id = request.form['itemId']
    price = request.form['price']
    availability = request.form['availability']
    foodType = request.form['foodType']
    
    conn = canteen_db()
    conn.execute('UPDATE Menu SET price=?, availability=?, foodType=? WHERE id=?', (price, availability, foodType, item_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('manager'))

if __name__ == '__main__':
    app.run(debug=True)
