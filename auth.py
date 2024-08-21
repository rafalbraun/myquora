from flask import Flask, render_template, request, redirect, url_for, make_response, session, flash
import sqlite3
import uuid
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

dbname = 'your_database.db'

# Queries for user management
QUERY_CREATE_USER = "INSERT INTO users (username, password, email, activation_token, is_active) VALUES (?, ?, ?, ?, 0)"
QUERY_SELECT_USER = "SELECT username, password, is_active FROM users WHERE username = ?"
QUERY_UPDATE_PASSWORD = "UPDATE users SET password = ? WHERE username = ?"
QUERY_SELECT_BY_TOKEN = "SELECT username FROM users WHERE activation_token = ?"
QUERY_ACTIVATE_USER = "UPDATE users SET is_active = 1 WHERE username = ?"
QUERY_UPDATE_ACTIVATION_TOKEN = "UPDATE users SET activation_token = ? WHERE email = ?"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        activation_token = str(uuid.uuid4())  # Generate a unique activation token
        hashed_password = hash_password(password)

        with sqlite3.connect(dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(QUERY_CREATE_USER, (username, hashed_password, email, activation_token))
            conn.commit()
            # Send an email with activation link (pseudo code)
            send_activation_email(email, activation_token)
            flash("Account created! Please check your email to activate your account.")
            return redirect(url_for('signin'))

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == 'GET':
        return render_template("signin.html")
    if request.method == 'POST':
        username = request.form.get('username')
        password = hash_password(request.form.get('password'))

        with sqlite3.connect(dbname) as conn:
            cursor = conn.cursor()
            row = cursor.execute(QUERY_SELECT_USER, (username,)).fetchone()
            if row is None:
                return 'No such user', 401
            else:
                if username == row[0] and password == row[1]:
                    if row[2] == 0:
                        return 'Account not activated', 403
                    # Create a response and set a cookie if login is successful
                    resp = make_response(redirect(url_for('posts')))
                    resp.set_cookie('auth', username, max_age=3600, httponly=True)  # Cookie valid for 1 hour
                    return resp
                else:
                    return 'Invalid credentials', 401

@app.route("/activate/<token>")
def activate_account(token):
    with sqlite3.connect(dbname) as conn:
        cursor = conn.cursor()
        row = cursor.execute(QUERY_SELECT_BY_TOKEN, (token,)).fetchone()
        if row is None:
            return 'Invalid activation link', 404
        cursor.execute(QUERY_ACTIVATE_USER, (row[0],))
        conn.commit()
        flash('Account activated! Please sign in.')
        return redirect(url_for('signin'))

@app.route("/password_reset_request", methods=["GET", "POST"])
def password_reset_request():
    if request.method == 'GET':
        return render_template("password_reset_request.html")
    if request.method == 'POST':
        email = request.form.get('email')
        reset_token = str(uuid.uuid4())  # Generate a unique reset token

        with sqlite3.connect(dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(QUERY_UPDATE_ACTIVATION_TOKEN, (reset_token, email))
            conn.commit()
            # Send an email with reset link (pseudo code)
            send_password_reset_email(email, reset_token)
            flash("Password reset link has been sent to your email.")
            return redirect(url_for('signin'))

@app.route("/password_reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    if request.method == 'GET':
        return render_template("password_reset.html")
    if request.method == 'POST':
        new_password = hash_password(request.form.get('password'))
        
        with sqlite3.connect(dbname) as conn:
            cursor = conn.cursor()
            row = cursor.execute(QUERY_SELECT_BY_TOKEN, (token,)).fetchone()
            if row is None:
                return 'Invalid reset link', 404
            cursor.execute(QUERY_UPDATE_PASSWORD, (new_password, row[0]))
            conn.commit()
            flash('Password reset successful! Please sign in.')
            return redirect(url_for('signin'))

# Dummy endpoint to display posts
@app.route("/posts")
def posts():
    return "Welcome to the posts page!"

# Pseudo functions to send emails
def send_activation_email(email, token):
    print(f"Sending activation email to {email} with token {token}")

def send_password_reset_email(email, token):
    print(f"Sending password reset email to {email} with token {token}")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
