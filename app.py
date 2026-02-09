from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("hotel.db")
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Bills table (bill header)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            total INTEGER
        )
    """)

    # Bill items table (multiple items)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER,
            item TEXT,
            quantity INTEGER,
            price INTEGER,
            subtotal INTEGER,
            FOREIGN KEY (bill_id) REFERENCES bills(id)
        )
    """)

    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bill', methods=['POST'])
def bill():
    customer_name = request.form['customer_name']
    items = request.form.getlist('item[]')
    quantities = request.form.getlist('quantity[]')
    prices = request.form.getlist('price[]')

    conn = get_db_connection()
    cursor = conn.cursor()

    grand_total = 0
    for i in range(len(items)):
        grand_total += int(quantities[i]) * int(prices[i])

    # Insert into bills table
    cursor.execute(
        "INSERT INTO bills (customer_name, total) VALUES (?, ?)",
        (customer_name, grand_total)
    )
    bill_id = cursor.lastrowid

    # Insert multiple items
    for i in range(len(items)):
        subtotal = int(quantities[i]) * int(prices[i])
        cursor.execute(
            "INSERT INTO bill_items (bill_id, item, quantity, price, subtotal) VALUES (?, ?, ?, ?, ?)",
            (bill_id, items[i], quantities[i], prices[i], subtotal)
        )

    conn.commit()
    conn.close()

    return render_template("bill.html", total=grand_total)

@app.route('/history')
def history():
    conn = get_db_connection()

    bills_data = conn.execute("SELECT * FROM bills").fetchall()
    bills = []

    for bill in bills_data:
        items = conn.execute(
            "SELECT item, quantity, price, subtotal FROM bill_items WHERE bill_id = ?",
            (bill["id"],)
        ).fetchall()

        bills.append({
            "id": bill["id"],
            "customer_name": bill["customer_name"],
            "total": bill["total"],
            "items": items
        })

    conn.close()
    return render_template("history.html", bills=bills)



if __name__ == "__main__":
    init_db()
    app.run(debug=True)

