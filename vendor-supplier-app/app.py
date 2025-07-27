from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from utils.geolocation import get_location
from lang.translations import get_translation

app = Flask(__name__)
app.secret_key = 'vendor_supplier_secret'
DB = 'database/app.db'

def init_db():
    if not os.path.exists('database'):
        os.makedirs('database')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER,
        name TEXT,
        price REAL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER,
        supplier_id INTEGER,
        rating INTEGER,
        comment TEXT
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vendor-login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        return login('vendor')
    return render_template('vendor_login.html')

@app.route('/supplier-login', methods=['GET', 'POST'])
def supplier_login():
    if request.method == 'POST':
        return login('supplier')
    return render_template('supplier_login.html')

def login(role):
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", (username, password, role))
    user = c.fetchone()
    conn.close()
    if user:
        session['user_id'] = user[0]
        session['role'] = role
        return redirect(f'/{role}-dashboard')
    return "Login Failed. Check credentials."

@app.route('/vendor-dashboard')
def vendor_dashboard():
    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''SELECT materials.id, materials.name, materials.price, users.username, users.id
                 FROM materials JOIN users ON materials.supplier_id = users.id''')
    materials = c.fetchall()
    conn.close()
    return render_template('vendor_dashboard.html', materials=materials)

@app.route('/supplier-dashboard')
def supplier_dashboard():
    if 'role' not in session or session['role'] != 'supplier':
        return redirect('/')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT name, price FROM materials WHERE supplier_id=?", (session['user_id'],))
    materials = c.fetchall()
    conn.close()
    return render_template('supplier_dashboard.html', materials=materials)

@app.route('/add-review', methods=['POST'])
def add_review():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO reviews (vendor_id, supplier_id, rating, comment) VALUES (?, ?, ?, ?)",
              (session['user_id'], request.form['supplier_id'], request.form['rating'], request.form['comment']))
    conn.commit()
    conn.close()
    return redirect('/vendor-dashboard')

@app.route('/panel')
def panel():
    lang = request.args.get('lang', 'en')
    translation = get_translation(lang)
    location = get_location()
    return render_template('panel.html', translation=translation, location=location)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
