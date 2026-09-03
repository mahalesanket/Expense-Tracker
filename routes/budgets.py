from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes import login_required
from database import get_db
from datetime import datetime

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/budgets')
@login_required
def list_budgets():
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()

    current_month = datetime.now().strftime('%m')
    current_year = str(datetime.now().year)

    cursor.execute('''
        SELECT b.id, b.category, b.monthly_limit,
               COALESCE(SUM(e.expense_amount), 0) as spent
        FROM budgets b
        LEFT JOIN expenses e ON b.category = e.expense_category 
            AND e.user_id = b.user_id 
            AND strftime('%m', e.expense_date) = ? 
            AND strftime('%Y', e.expense_date) = ?
        WHERE b.user_id = ?
        GROUP BY b.id
    ''', (current_month, current_year, user_id))
    
    raw_budgets = cursor.fetchall()
    budgets = []
    
    for item in raw_budgets:
        limit = item['monthly_limit']
        spent = item['spent']
        percentage = round((spent / limit) * 100, 1) if limit > 0 else 0
        
        status = 'safe'
        if percentage >= 100:
            status = 'danger'
        elif percentage >= 75:
            status = 'warning'

        budgets.append({
            'id': item['id'],
            'category': item['category'],
            'limit': limit,
            'spent': spent,
            'percentage': min(percentage, 100),
            'raw_percentage': percentage,
            'status': status
        })

    return render_template('budgets.html', budgets=budgets)

@budgets_bp.route('/add-budget', methods=['POST'])
@login_required
def add_budget():
    user_id = session['user_id']
    category = request.form.get('category', '').strip()
    monthly_limit = request.form.get('monthly_limit', type=float)

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO budgets (user_id, category, monthly_limit) 
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, category) DO UPDATE SET monthly_limit=excluded.monthly_limit
    ''', (user_id, category, monthly_limit))
    db.commit()
    flash('Budget set successfully!', 'success')
    return redirect(url_for('budgets.list_budgets'))