from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes import login_required
from database import get_db
import math

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses')
@login_required
def list_expenses():
    user_id = session['user_id']
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    cursor = db.cursor()

    sql_base = "FROM expenses WHERE user_id = ?"
    params = [user_id]

    if search_query:
        sql_base += " AND (expense_name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    if category_filter:
        sql_base += " AND expense_category = ?"
        params.append(category_filter)

    # Count Total Records
    cursor.execute(f"SELECT COUNT(*) {sql_base}", params)
    total_records = cursor.fetchone()[0]
    total_pages = math.ceil(total_records / per_page)

    # Fetch Paginated Records
    sql_query = f"SELECT * {sql_base} ORDER BY expense_date DESC, id DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    cursor.execute(sql_query, params)
    expenses = cursor.fetchall()

    return render_template(
        'expenses.html',
        expenses=expenses,
        page=page,
        total_pages=total_pages,
        search_query=search_query,
        category_filter=category_filter
    )

@expenses_bp.route('/add-expense', methods=['POST'])
@login_required
def add_expense():
    user_id = session['user_id']
    expense_name = request.form.get('expense_name', '').strip()
    expense_amount = request.form.get('expense_amount', type=float)
    expense_category = request.form.get('expense_category', '').strip()
    expense_date = request.form.get('expense_date', '').strip()
    payment_method = request.form.get('payment_method', '').strip()
    description = request.form.get('description', '').strip()

    if not expense_name or not expense_amount or not expense_category or not expense_date:
        flash('Required fields are missing.', 'danger')
        return redirect(url_for('expenses.list_expenses'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO expenses (user_id, expense_name, expense_amount, expense_category, expense_date, payment_method, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, expense_name, expense_amount, expense_category, expense_date, payment_method, description))
    db.commit()
    flash('Expense recorded successfully!', 'success')
    return redirect(url_for('expenses.list_expenses'))

@expenses_bp.route('/edit-expense/<int:expense_id>', methods=['POST'])
@login_required
def edit_expense(expense_id):
    user_id = session['user_id']
    expense_name = request.form.get('expense_name', '').strip()
    expense_amount = request.form.get('expense_amount', type=float)
    expense_category = request.form.get('expense_category', '').strip()
    expense_date = request.form.get('expense_date', '').strip()
    payment_method = request.form.get('payment_method', '').strip()
    description = request.form.get('description', '').strip()

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        UPDATE expenses 
        SET expense_name=?, expense_amount=?, expense_category=?, expense_date=?, payment_method=?, description=?
        WHERE id=? AND user_id=?
    ''', (expense_name, expense_amount, expense_category, expense_date, payment_method, description, expense_id, user_id))
    db.commit()
    flash('Expense updated successfully!', 'success')
    return redirect(url_for('expenses.list_expenses'))

@expenses_bp.route('/delete-expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM expenses WHERE id=? AND user_id=?', (expense_id, user_id))
    db.commit()
    flash('Expense deleted.', 'info')
    return redirect(url_for('expenses.list_expenses'))