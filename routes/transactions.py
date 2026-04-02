from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.transaction import (
    create_transaction, get_all_transactions,
    get_transaction_by_id, update_transaction, delete_transaction
)

transactions_bp = Blueprint('transactions', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Admin access required.", "error")
            return redirect(url_for('transactions.list_transactions'))
        return f(*args, **kwargs)
    return decorated


@transactions_bp.route('/')
@login_required
def list_transactions():
    role = session.get('role')
    user_id = session.get('user_id')

    # Analyst and admin can filter; viewer sees own records
    type_filter     = request.args.get('type') if role in ('analyst', 'admin') else None
    category_filter = request.args.get('category') if role in ('analyst', 'admin') else None
    date_from       = request.args.get('date_from') if role in ('analyst', 'admin') else None
    date_to         = request.args.get('date_to') if role in ('analyst', 'admin') else None

    # Admin sees all; others see only own
    filter_user_id = None if role == 'admin' else user_id

    transactions = get_all_transactions(
        user_id=filter_user_id,
        type_=type_filter,
        category=category_filter,
        date_from=date_from,
        date_to=date_to
    )
    return render_template('transactions/list.html', transactions=transactions, role=role)


@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_transaction():
    if request.method == 'POST':
        amount   = request.form.get('amount')
        type_    = request.form.get('type')
        category = request.form.get('category')
        date     = request.form.get('date')
        notes    = request.form.get('notes', '')
        user_id  = session['user_id']

        txn_id, errors = create_transaction(user_id, amount, type_, category, date, notes)
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            flash("Transaction added.", "success")
            return redirect(url_for('transactions.list_transactions'))
    return render_template('transactions/form.html', action='Add', transaction=None)


@transactions_bp.route('/edit/<int:txn_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_transaction(txn_id):
    txn = get_transaction_by_id(txn_id)
    if not txn:
        flash("Transaction not found.", "error")
        return redirect(url_for('transactions.list_transactions'))

    if request.method == 'POST':
        success, errors = update_transaction(
            txn_id,
            amount=request.form.get('amount'),
            type_=request.form.get('type'),
            category=request.form.get('category'),
            date=request.form.get('date'),
            notes=request.form.get('notes', '')
        )
        if not success:
            for e in errors:
                flash(e, "error")
        else:
            flash("Transaction updated.", "success")
            return redirect(url_for('transactions.list_transactions'))
    return render_template('transactions/form.html', action='Edit', transaction=txn)


@transactions_bp.route('/delete/<int:txn_id>', methods=['POST'])
@login_required
@admin_required
def delete_transaction_route(txn_id):
    success, error = delete_transaction(txn_id)
    if success:
        flash("Transaction deleted.", "success")
    else:
        flash(f"Error: {error}", "error")
    return redirect(url_for('transactions.list_transactions'))