from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.summary import get_summary, get_category_breakdown, get_monthly_totals, get_recent_activity

summary_bp = Blueprint('summary', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@summary_bp.route('/summary')
@login_required
def dashboard():
    role    = session.get('role')
    user_id = session.get('user_id')

    uid = None if role == 'admin' else user_id

    summary    = get_summary(uid)
    categories = get_category_breakdown(uid)
    monthly    = get_monthly_totals(uid)
    recent     = get_recent_activity(uid, limit=5)

    return render_template(
        'summary.html',
        summary=summary,
        categories=categories,
        monthly=monthly,
        recent=recent,
        role=role
    )