import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///canteen.db"
app.secret_key = "your_secret_key_here"

def create_conn():
    # Create a connection to the database
    conn = sqlite3.connect("canteen.db")
    return conn

@app.route('/')
def home():
    # Create the connection and pass it to the home function
    conn = create_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM menu")
    items = c.fetchall()
    conn.close()  # Close the connection after using it
    return render_template('home.html', items=items)

if __name__ == "__main__":
    app.run(debug=True)

    
@app.route('/cart')
def cart():
    # Add logic to display the cart page
    return render_template('cart.html')


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    # Get the user_id from the session
    user_id = session.get('user_id')
    
    # Get the item_id from the POST request data
    item_id = request.form.get('item_id')
    
    # Create a connection to the database
    conn = create_conn()
    c = conn.cursor()
    
    # Check if the item is already in the cart
    c.execute("SELECT * FROM cart WHERE user_id=? AND item_id=?", (user_id, item_id))
    item_in_cart = c.fetchone()
    
    if item_in_cart:
        # If the item is already in the cart, update the quantity
        c.execute("UPDATE cart SET quantity=quantity+1 WHERE user_id=? AND item_id=?", (user_id, item_id))
    else:
        # If the item is not in the cart, insert a new row
        c.execute("INSERT INTO cart (user_id, item_id, quantity) VALUES (?, ?, 1)", (user_id, item_id))
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    # Redirect back to the home page
    return redirect(url_for('home'))

