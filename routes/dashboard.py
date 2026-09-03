from flask import Blueprint, render_template, session
from routes import login_required
from database import get_db
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()

    # Aggregate Total Income
    cursor.execute('SELECT COALESCE(SUM(income_amount), 0) FROM income WHERE user_id = ?', (user_id,))
    total_income = cursor.fetchone()[0]

    # Aggregate Total Expenses
    cursor.execute('SELECT COALESCE(SUM(expense_amount), 0) FROM expenses WHERE user_id = ?', (user_id,))
    total_expenses = cursor.fetchone()[0]

    balance = total_income - total_expenses
    savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0

    # Recent 5 Transactions (Expenses)
    cursor.execute('''
        SELECT id, expense_name, expense_amount, expense_category, expense_date, payment_method 
        FROM expenses WHERE user_id = ? 
        ORDER BY expense_date DESC, id DESC LIMIT 5
    ''', (user_id,))

    recent_transactions = cursor.fetchall()

    # Category Breakdown for Chart
    cursor.execute('''
        SELECT expense_category, SUM(expense_amount) as total 
        FROM expenses WHERE user_id = ? 
        GROUP BY expense_category
    ''', (user_id,))
    cat_data = cursor.fetchall()
    categories = [row['expense_category'] for row in cat_data]
    category_totals = [row['total'] for row in cat_data]

    # Monthly Overview data (Current Year)
    current_year = str(datetime.now().year)
    cursor.execute('''
        SELECT strftime('%m', expense_date) as month, SUM(expense_amount) as total 
        FROM expenses WHERE user_id = ? AND strftime('%Y', expense_date) = ? 
        GROUP BY month ORDER BY month
    ''', (user_id, current_year))
    monthly_exp_raw = dict(cursor.fetchall())

    cursor.execute('''
        SELECT strftime('%m', income_date) as month, SUM(income_amount) as total 
        FROM income WHERE user_id = ? AND strftime('%Y', income_date) = ? 
        GROUP BY month ORDER BY month
    ''', (user_id, current_year))
    monthly_inc_raw = dict(cursor.fetchall())

    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    monthly_expenses = [monthly_exp_raw.get(m, 0) for m in months]
    monthly_income = [monthly_inc_raw.get(m, 0) for m in months]

    return render_template(
        'dashboard.html',
        user_name=session.get('user_name', 'User'),
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        savings_rate=round(savings_rate, 2),
        recent_transactions=recent_transactions,
        categories=categories,
        category_totals=category_totals,
        month_labels=month_labels,
        monthly_expenses=monthly_expenses,
        monthly_income=monthly_income
    )