import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

auth_bp = Blueprint('auth', __name__)

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if not is_valid_password(password):
            flash('Password must be at least 8 characters long and contain uppercase, lowercase, and numeric characters.', 'danger')
            return render_template('register.html')

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            flash('An account with this email already exists.', 'danger')
            return render_template('register.html')

        pwd_hash = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (full_name, email, password_hash, auth_provider) VALUES (?, ?, ?, ?)',
            (full_name, email, pwd_hash, 'email')
        )
        db.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if user and user['password_hash'] and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session.permanent = True
            return redirect(url_for('dashboard.dashboard'))
        
        flash('Invalid email or password.', 'danger')

    return render_template('login.html')

# Endpoint to bridge Firebase OAuth authentication with SQLite and Flask Session
@auth_bp.route('/firebase-login', methods=['POST'])
def firebase_login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid payload.'}), 400

    email = data.get('email', '').strip().lower()
    full_name = data.get('full_name', '').strip() or 'OAuth User'
    provider = data.get('provider', 'google')

    if not email:
        return jsonify({'success': False, 'message': 'Email is required from OAuth identity.'}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            'INSERT INTO users (full_name, email, password_hash, auth_provider) VALUES (?, ?, ?, ?)',
            (full_name, email, None, provider)
        )
        db.commit()
        user_id = cursor.lastrowid
    else:
        user_id = user['id']
        full_name = user['full_name']

    session.clear()
    session['user_id'] = user_id
    session['user_name'] = full_name
    session.permanent = True

    return jsonify({'success': True, 'redirect_url': url_for('dashboard.dashboard')})

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))