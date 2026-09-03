from flask import Blueprint, render_template, session
from routes import login_required
from database import get_db

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics():
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()

    # Category breakdown query
    cursor.execute('''
        SELECT expense_category, SUM(expense_amount) as total 
        FROM expenses 
        WHERE user_id = ? 
        GROUP BY expense_category 
        ORDER BY total DESC
    ''', (user_id,))
    cat_breakdown = cursor.fetchall() or []

    # Total expenses query
    cursor.execute('SELECT SUM(expense_amount) FROM expenses WHERE user_id = ?', (user_id,))
    total_spend_result = cursor.fetchone()
    total_spend = total_spend_result[0] if (total_spend_result and total_spend_result[0]) else 0.0

    # Daily average query
    cursor.execute('''
        SELECT AVG(daily_sum) FROM (
            SELECT SUM(expense_amount) as daily_sum 
            FROM expenses 
            WHERE user_id = ? 
            GROUP BY expense_date
        )
    ''', (user_id,))
    avg_daily_result = cursor.fetchone()
    avg_daily = avg_daily_result[0] if (avg_daily_result and avg_daily_result[0]) else 0.0

    # Daily spending trend (last 7 recorded days)
    cursor.execute('''
        SELECT expense_date, SUM(expense_amount) as total 
        FROM expenses 
        WHERE user_id = ? 
        GROUP BY expense_date 
        ORDER BY expense_date ASC 
        LIMIT 7
    ''', (user_id,))
    daily_trends = cursor.fetchall() or []

    # Generate insights safely
    insights = []
    if cat_breakdown:
        top_cat = cat_breakdown[0]
        insights.append(f"Your highest spending category is {top_cat['expense_category']} at ₹{top_cat['total']:,.2f}.")
    
    if avg_daily > 0:
        insights.append(f"Your average daily spending across recorded days is ₹{avg_daily:,.2f}.")
    else:
        insights.append("Start logging expenses regularly to track your daily average trends.")

    return render_template(
        'analytics.html', 
        cat_breakdown=cat_breakdown, 
        insights=insights,
        total_spend=total_spend,
        avg_daily=avg_daily,
        daily_trends=daily_trends
    )