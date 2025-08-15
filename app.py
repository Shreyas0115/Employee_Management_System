from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"   # Secret key for sessions

# Database connection
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",        # Change this to your MySQL username
        password="root",    # Change this to your MySQL password
        database="employee_db"
    )

# Home / Login Page
@app.route('/')
def home():
    return render_template("login.html")

# Login Authentication
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        session['username'] = user['username']
        session['role'] = user['role']
        return redirect(url_for('dashboard'))
    else:
        return "Invalid login! Please try again."

# Dashboard (Admin / Employee)
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if session['role'] == 'admin':
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template("employee_list.html", employees=employees)
    else:
        cursor.execute("SELECT * FROM employees WHERE email=%s", (session['username'],))
        employee = cursor.fetchone()
        cursor.close()
        db.close()
        return render_template("dashboard.html", employee=employee)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Add Employee (Admin only)
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            role = request.form['role']
            salary = request.form['salary']

            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO employees (name, email, role, salary) VALUES (%s, %s, %s, %s)",
                           (name, email, role, salary))
            db.commit()
            cursor.close()
            db.close()
            return redirect(url_for('dashboard'))

        return render_template("add_employee.html")
    return redirect(url_for('home'))

# Update Employee (Admin only)
@app.route('/update_employee/<int:id>', methods=['GET', 'POST'])
def update_employee(id):
    if 'role' in session and session['role'] == 'admin':
        db = get_db()
        cursor = db.cursor(dictionary=True)

        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            role = request.form['role']
            salary = request.form['salary']

            cursor.execute("UPDATE employees SET name=%s, email=%s, role=%s, salary=%s WHERE id=%s",
                           (name, email, role, salary, id))
            db.commit()
            cursor.close()
            db.close()
            return redirect(url_for('dashboard'))

        cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
        employee = cursor.fetchone()
        cursor.close()
        db.close()
        return render_template("update_employee.html", employee=employee)
    return redirect(url_for('home'))

# Delete Employee (Admin only)
@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    if 'role' in session and session['role'] == 'admin':
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))
    return redirect(url_for('home'))

# Run App
if __name__ == "__main__":
    app.run(debug=True)
