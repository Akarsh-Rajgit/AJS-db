from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from dotenv import load_dotenv
import os
from werkzeug.security import check_password_hash

app = Flask(__name__)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ichigo_bankai24",
    database="ajs"
)
cursor = conn.cursor()

load_dotenv() 
try:
    app.secret_key = os.environ["SECRET_KEY"]
except KeyError:
    raise RuntimeError("SECRET_KEY not set. Add it to your .env file or cloud config.")

STORED_HASH = "scrypt:32768:8:1$KrVTE7PR49O7AJR5$da2d20de61db40e9310f2dbc2f59c6acd021c73c809f33e969e9821a98f42032d94cdc4e8a194d9c0e36cad4e7a9d900563269bab80ccdc6d3ca3d1cf124c0bf"

def is_authenticated():
    return 'user' in session

@app.route('/')
def root():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'ajsen' and check_password_hash(STORED_HASH, password):
            session['user'] = username
            return redirect('/home')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/home')
def home():
    if not is_authenticated():
        return redirect('/login')
    return render_template('index.html')


@app.route('/quotation', methods=['GET', 'POST'])
def quotation():
    if request.method == 'POST':
        quotation_no = request.form['quotation_number']
        manager = request.form['manager']
        date = request.form['date']
        description = request.form['description']
        total_amount = request.form['total_amount']

        cursor.execute("""
            INSERT INTO quotation (quotation_no, manager, date, description, total_amount)
            VALUES (%s, %s, %s, %s, %s)
        """, (quotation_no, manager, date, description, total_amount))
        conn.commit()
        return redirect('/quotation')

    query = "SELECT * FROM quotation WHERE 1"
    params = []

    for field in ['quotation_number', 'manager', 'date']:
        value = request.args.get(field)
        if value:
            query += f" AND {field.replace('quotation_number', 'quotation_no')} LIKE %s"
            params.append(f"%{value}%")

    cursor.execute(query, params)
    results = cursor.fetchall()

    return render_template('quotation.html', quotation=results)

@app.route('/invoice', methods=['GET', 'POST'])
def invoice():
    if request.method == 'POST':
        invoice_no = request.form['invoice_number']
        quotation_no = request.form['quotation_number']
        date = request.form['date']
        description = request.form['description']
        total_amount = request.form['total_amount']
        payable_amount = request.form['payable_amount']

        cursor.execute("""
            INSERT INTO invoice (invoice_no, quotation_no, date, description, amount, payable_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (invoice_no, quotation_no, date, description, total_amount, payable_amount))
        conn.commit()
        return redirect('/invoice')

    query = "SELECT * FROM invoice WHERE 1"
    params = []

    for field in ['invoice_number', 'quotation_number', 'date']:
        value = request.args.get(field)
        if value:
            query += f" AND {field.replace('invoice_number', 'invoice_no').replace('quotation_number', 'quotation_no')} LIKE %s"
            params.append(f"%{value}%")

    cursor.execute(query, params)
    results = cursor.fetchall()

    return render_template('invoice.html', invoice=results)

@app.route('/logout')
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)
