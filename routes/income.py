from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes import login_required
from database import get_db

income_bp = Blueprint('income', __name__)

@income_bp.route('/income')
@login_required
def list_income():
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM income WHERE user_id = ? ORDER BY income_date DESC', (user_id,))
    incomes = cursor.fetchall()
    return render_template('income.html', incomes=incomes)

@income_bp.route('/add-income', methods=['POST'])
@login_required
def add_income():
    user_id = session['user_id']
    income_name = request.form.get('income_name', '').strip()
    income_amount = request.form.get('income_amount', type=float)
    income_category = request.form.get('income_category', '').strip()
    income_date = request.form.get('income_date', '').strip()
    payment_method = request.form.get('payment_method', '').strip()
    description = request.form.get('description', '').strip()

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO income (user_id, income_name, income_amount, income_category, income_date, payment_method, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, income_name, income_amount, income_category, income_date, payment_method, description))
    db.commit()
    flash('Income added successfully!', 'success')
    return redirect(url_for('income.list_income'))