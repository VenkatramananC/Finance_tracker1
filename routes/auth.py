from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import authenticate_user, create_user, get_all_users

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f"Welcome, {user['username']}! Role: {user['role']}", "success")
            return redirect(url_for('transactions.list_transactions'))
        else:
            flash("Invalid username or password.", "error")
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'viewer').strip()
        user_id, error = create_user(username, password, role)
        if error:
            flash(f"Error: {error}", "error")
        else:
            flash("Account created. Please login.", "success")
            return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth_bp.route('/users')
def list_users():
    if session.get('role') != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('transactions.list_transactions'))
    users = get_all_users()
    return render_template('users.html', users=users)