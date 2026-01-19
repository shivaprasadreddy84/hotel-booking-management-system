from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------------- MySQL Database Connection ----------------
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",        # keep this if you are running MySQL locally
        user="root",             # ⚠️ replace if your MySQL username is different
        password="root",         # ⚠️ replace with your actual MySQL password
        database="hotel_db"
    )
    return conn

# ---------------- Routes ----------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            conn.close()
            return "⚠️ Username already exists. Try another one!"
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "❌ Invalid credentials. <a href='/login'>Try again</a>"
    return render_template('login.html')

# ---------------- Booking Route ----------------
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        room_type = request.form['room_type']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        amount = request.form['amount']  # ✅ collect total amount from form
        user = session.get('username', 'Guest')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bookings (user, room_type, check_in, check_out, amount) VALUES (%s, %s, %s, %s, %s)",
            (user, room_type, check_in, check_out, amount)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Get selected room type from URL (if any)
    selected_room = request.args.get('room_type', '')
    return render_template('booking.html', selected_room=selected_room)

# ---------------- Dashboard Route ----------------
@app.route('/dashboard')
def dashboard():
    username = session.get('username', 'Guest')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT room_type, check_in, check_out, amount FROM bookings WHERE user=%s", (username,))
    bookings = cur.fetchall()
    conn.close()

    return render_template('dashboard.html', username=username, bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True)
