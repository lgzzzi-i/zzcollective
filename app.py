from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from urllib.parse import quote

VENMO_USERNAME = "Lila-Gizzie"  

def build_venmo_link(order_id, amount):
       note = quote(f"Order #{order_id}")
       return (
           f"https://venmo.com/?txn=pay&audience=private"
           f"&recipients={VENMO_USERNAME}&amount={amount:.2f}&note={note}"
       )

app = Flask(__name__)
@app.route('/')
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/products")
def products():
    return render_template("products.html")

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        name = request.form.get("name")
        contact = request.form.get("contact")
        items = request.form.get("items")
        venmo_account = request.form.get("venmo_account")

        conn = sqlite3.connect("orders.db")
        cur = conn.execute(
            "INSERT INTO orders (name, contact, items, venmo_account) VALUES (?, ?, ?, ?)",
            (name, contact, items, venmo_account),
        )
        order_id = cur.lastrowid
        conn.commit()
        conn.close()

        return redirect(url_for("confirmation", order_id=order_id))

    return render_template("order.html")

def init_db():
    conn = sqlite3.connect("orders.db")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            items TEXT NOT NULL,
            venmo_account TEXT NOT NULL,
            status TEXT DEFAULT 'pending_payment'
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/confirmation/<int:order_id>")
def confirmation(order_id):
       conn = sqlite3.connect("orders.db")
       row = conn.execute(
           "SELECT name, items, venmo_account FROM orders WHERE id = ?", (order_id,)
       ).fetchone()
       conn.close()

       name, items, venmo_account = row
       return render_template(
            "confirmation.html",
            order_id=order_id, name=name, items=items, venmo_account=venmo_account,
        )

if __name__== "__main__":
    init_db()
    app.run(debug=True)

