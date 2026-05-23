from flask import Flask, render_template, request, jsonify
import re
import random
import string
import hashlib
import sqlite3
import os

# Get the absolute path to the templates directory
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# =========================
# DATABASE SETUP
# =========================

conn = sqlite3.connect('passwords.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password_hash TEXT
)
''')

conn.commit()

# =========================
# COMMON PASSWORD CHECK
# =========================

def is_common_password(password):
    with open('common_passwords.txt', 'r') as file:
        common_passwords = file.read().splitlines()

    return password.lower() in common_passwords

# =========================
# PASSWORD HASHING
# =========================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# GENERATE STRONG PASSWORD
# =========================

def generate_strong_password():

    characters = (
        string.ascii_letters +
        string.digits +
        "!@#$%^&*()"
    )

    strong_password = ''.join(
        random.choice(characters) for _ in range(12)
    )

    return strong_password

# =========================
# PASSWORD STRENGTH CHECK
# =========================

def check_password_strength(password):

    score = 0
    suggestions = []

    # Length Check
    if len(password) >= 8:
        score += 1
    else:
        suggestions.append("Use at least 8 characters")

    # Uppercase Check
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        suggestions.append("Add an uppercase letter")

    # Lowercase Check
    if re.search(r'[a-z]', password):
        score += 1
    else:
        suggestions.append("Add a lowercase letter")

    # Number Check
    if re.search(r'[0-9]', password):
        score += 1
    else:
        suggestions.append("Add a number")

    # Special Character Check
    if re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        score += 1
    else:
        suggestions.append("Add a special character")

    # Common Password Check
    if is_common_password(password):
        suggestions.append("This password is very common")

    # Strength Levels
    if score <= 2:
        strength = "Weak"

    elif score <= 4:
        strength = "Medium"

    else:
        strength = "Strong"

    return strength, score, suggestions

# =========================
# HOME ROUTE
# =========================

@app.route('/')
def home():
    return render_template('index.html')

# =========================
# ANALYZE PASSWORD ROUTE
# =========================

@app.route('/analyze', methods=['POST'])
def analyze_password():

    data = request.get_json()

    password = data['password']

    strength, score, suggestions = check_password_strength(password)

    hashed_password = hash_password(password)

    # Check password reuse
    cursor.execute(
        'SELECT * FROM passwords WHERE password_hash=?',
        (hashed_password,)
    )

    reused = cursor.fetchone()

    if reused:
        reuse_message = "Password already used before!"

    else:
        cursor.execute(
            'INSERT INTO passwords (password_hash) VALUES (?)',
            (hashed_password,)
        )

        conn.commit()

        reuse_message = "Password is unique"

    strong_password = generate_strong_password()

    return jsonify({
        'strength': strength,
        'score': score,
        'suggestions': suggestions,
        'generated_password': strong_password,
        'reuse_message': reuse_message
    })

# =========================
# RUN APPLICATION
# =========================

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)