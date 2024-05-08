from datetime import datetime, timedelta
import time
from flask import Flask, abort, render_template, request, redirect, session, url_for
import sqlite3
from helpers import generate_receipt_number as generate_receipt_number , canteen_db as canteen_db , student_db as student_db , increase_purchase_count as increase_purchase_count
app = Flask(__name__)
app.secret_key = "super_secret_key"
@app.context_processor
def common_icons():
    admin = "/static/assets/admin.png"
    customer = "/static/assets/customer.png"
    manager = "/static/assets/manager.png"
    editimage = "/static/assets/edit.png"
    return dict(admin=admin, manager=manager, customer=customer, editimage=editimage)
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["user-type"]
        conn = student_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ? AND role = ?",
            (username, password, role),
        ).fetchone()
        conn.close()
        if user:
            session["userid"] = user["id"]
            session["user_type"] = user["role"]
            session["user_name"] = user["username"]
            if user["role"] == "admin":
                return redirect(url_for("admin"))
            elif user["role"] == "manager":
                return redirect(url_for("manager"))
            session["logged_in"] = True
            return redirect(url_for("home", username=username))
        else:
            return render_template("error.html" , error = 'Invalid username or password')
    return render_template("login.html")
@app.route("/signup", methods=["GET", "POST"])
def signup():
    time.sleep(1)
    if request.method == "POST":
        username = request.form["university_reg_no"]
        password = request.form["password"]
        student_id = request.form.get("student_id")
        roll_no = request.form.get("roll_no")
        student_name = request.form.get("student_name")
        admission_number = request.form.get("admission_number")
        university_reg_no = request.form.get("university_reg_no")
        department = request.form.get("department")
        batch = request.form.get("batch")
        primary_email_id = request.form.get("primary_email_id")
        student_phone = request.form.get("student_phone")
        parent_phone = request.form.get("parent_phone")
        gender = request.form.get("gender")
        date_of_birth = request.form.get("date_of_birth")
        birth_place = request.form.get("birth_place")
        state = request.form.get("state")
        admission_date = request.form.get("admission_date")
        current_address = request.form.get("current_address")
        permanent_address = request.form.get("permanent_address")
        religion = request.form.get("religion")
        caste = request.form.get("caste")
        with student_db() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                return render_template("error.html", error="Username already exists. Please choose a different username.")
            else:
                conn.execute(
                    "INSERT INTO users (username, password, role, score) VALUES (?, ?, ?, ?)",
                    (university_reg_no, password, "customer", 100)
                )
                conn.execute(
                    "INSERT INTO students (Sl_No, Roll_No, Admission_No, University_Reg_No, Student_ID, Student_Name, Department, Batch, Primary_Email_ID, Gender, Date_of_Birth, Birth_Place, State, Admission_Date, Current_Address, Permenant_Address, Student_Phone, Parent_Phone, Religion, Caste, pfp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (None, roll_no, admission_number, university_reg_no, student_id, student_name, department, batch, primary_email_id, gender, date_of_birth, birth_place, state, admission_date, current_address, permanent_address, student_phone, parent_phone, religion, caste, None)
                )
                conn.commit()
                return redirect(url_for("login"))
    return render_template("signup.html")
@app.route("/finepayment", methods=["GET", "POST"])
def finepayment():
    return render_template("fine.html")

@app.route("/finepaymentprocessing", methods=["GET", "POST"])
def finepaymentprocessing():
    with student_db() as conn:
        conn.execute("UPDATE users SET score = 100 WHERE username = ?", (session["user_name"],))
        conn.commit()
    return render_template("processing.html")
@app.route("/home", methods=["GET", "POST"])
def home():
    with canteen_db() as conn:
        conn.row_factory = sqlite3.Row
        menu_cursor = conn.execute("SELECT * FROM Menu")
        cart_cursor = conn.execute("SELECT * FROM Cart WHERE status = 'ordered'")
    menu_items = menu_cursor.fetchall()
    cart_items = cart_cursor.fetchall()
    total_price = sum(item["price"] * item["quantity"] for item in cart_items)
    with student_db() as conn:
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE username = ?", (session["user_name"],)).fetchone()
        score = user["score"]
        conn.commit()
    if score == 50:
        return render_template("fine.html", user=session["user_name"])
    return render_template(
        "home.html",
        menu_items=menu_items,
        cart_items=cart_items,
        total_price=total_price,
    )
@app.route("/add_to_cart/<int:menu_id>", methods=["POST"])
def add_to_cart(menu_id):
    username = session.get("user_name")
    pickup_time = "03:00"
    db = student_db()
    cursor = db.cursor()
    cursor.execute("SELECT score FROM users WHERE username = ?", (username,))
    score = cursor.fetchone()[0]
    db.commit()
    db.close()
    with canteen_db() as conn:
        menu_item = conn.execute(
            "SELECT name, price FROM Menu WHERE id = ?", (menu_id,)
        ).fetchone()
        cart_item = conn.execute(
            "SELECT * FROM Cart WHERE id = ?", (menu_id,)
        ).fetchone()
        if cart_item:
            new_quantity = cart_item["quantity"] + 1
            conn.execute(
                "UPDATE Cart SET quantity = ? WHERE id = ?",
                (new_quantity, cart_item["id"]),
            )
        else:
            conn.execute(
                'INSERT or IGNORE INTO Cart (id, name, price, quantity, ordered_by, customer_score, status, pickup_time) VALUES (?, ?, ?, ?, ?, ?, "ordered", ?)',
                (
                    menu_id,
                    menu_item["name"],
                    menu_item["price"],
                    1,
                    username,
                    score,
                    pickup_time,
                ),
            )
            conn.commit()
    return redirect(url_for("home"))
@app.route("/remove_from_cart/<string:name>", methods=["POST"])
def remove_from_cart(name):
    with canteen_db() as conn:
        existing_item = conn.execute(
            "SELECT * FROM Cart WHERE name = ?", (name,)
        ).fetchone()
        if existing_item:
            new_quantity = existing_item["quantity"] - 1
            if new_quantity <= 0:
                conn.execute("DELETE FROM Cart WHERE name = ?", (name,))
            else:
                conn.execute(
                    "UPDATE Cart SET quantity = ? WHERE name = ?", (new_quantity, name)
                )
            conn.commit()
    return redirect(url_for("home"))

@app.route("/checkout")
def checkout():
    time.sleep(1)
    increase_purchase_count(session["user_name"])
    timenow = datetime.now() + timedelta(minutes=3)
    timenow = timenow.strftime("%H:%M:%S")
    print(timenow)
    with canteen_db() as conn:
        cart_items = conn.execute("SELECT * FROM Cart").fetchall()
        total = sum(item["price"] * item["quantity"] for item in cart_items)
        receipt_number = generate_receipt_number()
        for item in cart_items:
            conn.execute(
                "INSERT INTO Orders (name, price, ordered_by, quantity, customer_score,status, pickup_time, receipt_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    item["name"],
                    item["price"],
                    item["ordered_by"],
                    item["quantity"],
                    item["customer_score"],
                    'ordered',
                    timenow,
                    receipt_number,
                ),
            )
        conn.execute("DELETE FROM Cart")
        conn.commit()
    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total,
        receipt_number=receipt_number,
    )
    
@app.route("/processing", methods=["GET", "POST"])
def processing():
    return render_template("processing.html")
@app.route("/logout")
def logout():
    session.clear()
    time.sleep(1)
    return redirect(url_for("login"))
@app.route("/profile")
def profile():
    username = session.get("user_name")
    if not username:
        return abort(404)
    with student_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE University_Reg_No=?", (username,))
        user_info = cursor.fetchone()
        cursor.execute("SELECT score FROM users WHERE username=?", (username,))
        score = cursor.fetchone()[0]
        if not user_info:
            return abort(404)
    return render_template(
        "profile.html",
        student_id=user_info["Student_ID"],
        admission_no=user_info["Admission_No"],
        sl_no=user_info["Sl_No"],
        roll_no=user_info["Roll_No"],
        student_name=user_info["student_Name"],
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
        pfp=user_info["pfp"],
        user_score=score,
    )
@app.route("/orders")
def orders():
    user = session["user_name"]
    with student_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT score FROM users WHERE username=?", (user,))
        score = cursor.fetchone()[0]
    with canteen_db() as conn:
        orders = conn.execute("SELECT * FROM Orders WHERE ordered_by = ?", (user,)).fetchall()
    return render_template("orders.html", orders=orders, user=user) if score != 50 else render_template("fine.html", user=user)

@app.route("/cancel_order", methods=["POST"])
def cancel_order():
    order_id = request.form["order_id"]
    with canteen_db() as conn:
        order = conn.execute('SELECT * FROM Orders WHERE id = ?', (order_id,)).fetchone()
        pickup_time = datetime.strptime(order['pickup_time'], "%H:%M:%S")
        time_diff = pickup_time - datetime.now()
        if time_diff.total_seconds() < 60:
            with student_db() as student_conn:
                cursor = student_conn.cursor()
                cursor.execute("SELECT score FROM users WHERE username=?", (session["user_name"],))
                score = cursor.fetchone()[0]
                new_score = max(score - 10, 0)
                student_conn.execute("UPDATE users SET score = ? WHERE username = ?", (new_score, session["user_name"]))
                student_conn.commit()
        conn.execute("DELETE FROM Orders WHERE id = ?", (order_id,))
        conn.commit()
    return redirect("/orders")


@app.route("/manager")
def manager():
    with canteen_db() as conn:
        menu = conn.execute("SELECT * FROM Menu").fetchall()
        orders = conn.execute("SELECT * FROM Orders WHERE status = 'ordered'").fetchall()
        reports = conn.execute("SELECT * FROM Reports").fetchall()
    return render_template(
        "canteenmanager.html", menu=menu, orders=orders, reports=reports
    )
@app.route('/served_order', methods=['POST'])
def served_order():
    order_id = request.form['order_id']
    with canteen_db() as conn:
        order = conn.execute('SELECT * FROM Orders WHERE id = ?', (order_id,)).fetchone()
        conn.execute("""
            INSERT INTO Reports (name, price, ordered_by, quantity, customer_score, status, pickup_time, receipt_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (order['name'], order['price'], order['ordered_by'], order['quantity'], order['customer_score'], 'served', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), generate_receipt_number()))
        conn.execute('DELETE FROM Orders WHERE id = ?', (order_id,))
        conn.commit()
    return redirect('/manager')

@app.route("/edit_item", methods=["POST"])
def edit_item():
    item_id = request.form["item_id"]
    item_name = request.form["item_name"]
    item_price = request.form["item_price"]
    item_image = request.form["item_image"]
    item_availability = request.form["item_availability"]
    item_food_type = request.form["item_food_type"]
    item_demerits = request.form["item_demerit"]
    item_quantity = request.form["item_quantity"]
    conn = sqlite3.connect("canteen.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE menu 
        SET name=?, price=?, image_url=?, availability=?, foodtype=?, demerit=?,quantity=?
        WHERE id=?
    """,
        (item_name, item_price, f"static/{item_image}", item_availability, item_food_type,item_demerits,item_quantity, item_id),
    )
    conn.commit()
    conn.close()
    return redirect("/manager")

@app.route("/delete_item", methods=["POST"])
def delete_item():
    item_id = request.form.get("item_id")
    with canteen_db() as conn:
        conn.execute("DELETE FROM Menu WHERE id = ?", (item_id,))
        conn.commit()
    return redirect("/manager")

@app.route("/admin")
def admin():
    conn = student_db()
    users_cursor = conn.execute("SELECT * FROM users WHERE role != 'admin'")
    users_data = users_cursor.fetchall()
    return render_template("admin.html", users_data=users_data)

@app.route("/edit_user", methods=["POST"])
def edit_user():
    user_id = request.form.get("user_id")
    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role")
    score = request.form.get("score")
    with student_db() as conn:
        conn.execute(
            "UPDATE users SET username = ?, password = ?, role = ? ,score = ? WHERE id = ?",
            (username, password, role, score, user_id),
        )
        conn.commit()
    return redirect("/admin")

@app.route("/delete_user", methods=["POST"])
def delete_user():
    user_id = request.form.get("user_id")
    with student_db() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return redirect("/admin")

@app.route("/edit_profile")
def edit_profile():
    render_template("editprofile.html")
    
@app.route('/set_order_expired', methods=['POST'])
def set_order_expired():
    order_id = request.args.get('order_id')
    with canteen_db() as conn:
        conn.execute('UPDATE Orders SET status = ? WHERE id = ?', ('expired', order_id))
        conn.commit()
    return redirect('/orders')

@app.route("/add_item", methods=["POST"])
def add_item():
    item_name = request.form.get("item_name")
    item_price = request.form.get("item_price")
    item_image = request.form.get("item_image")
    item_quantity = request.form.get("item_quantity")
    item_availability = request.form.get("item_availability")
    item_food_type = request.form.get("item_food_type")
    with canteen_db() as conn:
        conn.execute(
            "INSERT INTO Menu (name, price, image_url, availability, foodtype, quantity) VALUES (?, ?, ?, ?, ?, ?)",
            (item_name, item_price, f"static/{item_image}",item_quantity, item_availability, item_food_type),
        )
        conn.commit()
    return redirect("/manager")

@app.route('/download_report')
def download_report():
    with canteen_db() as conn:
        reports = conn.execute('SELECT * FROM Reports').fetchall()
    return render_template('report.html', reports=reports)

@app.route('/reduce_score', methods=['POST'])
def reduce_score():
    ordered_by = request.args.get('ordered_by')
    ordered_id = request.args.get('order_id')
    #get demerit from menu using order id
    with canteen_db() as conn:
        demerit = conn.execute('SELECT demerit FROM Menu WHERE id = ?', (ordered_id,)).fetchone()
        if demerit:
            demerit = demerit[0]
    with student_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE username = ?', (ordered_by,)).fetchone()
        if user:
            purchase_count = conn.execute('SELECT purchasecount FROM users WHERE username = ?', (ordered_by,)).fetchone()[0]
            if purchase_count == 1:
                new_score = 90 - demerit
            elif purchase_count == 2:
                new_score = 80 - demerit
            elif purchase_count == 3:
                new_score = 70 - demerit
            elif purchase_count == 4:
                new_score = 60 - demerit
            elif purchase_count == 5:
                new_score = 50 - demerit
            if new_score < 50:
                redirect(url_for('finepayment'))
            conn.execute('UPDATE users SET score = ? WHERE username = ?', (new_score, ordered_by))
            conn.commit()  
    return redirect(url_for('orders'))


if __name__ == "__main__":
    app.run(debug=True)
