"""
FarmVet Connect - Authentication Routes
Handles login and logout for all 3 roles
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from database import get_db, User

auth_bp = Blueprint('auth', __name__)


# ── Helper: fetch user and verify password ───────────────────────────────────

def attempt_login(email, password, required_role):
    """Try to log in a user with a specific role."""
    db = get_db()
    row = db.execute(
        "SELECT id, name, email, password_hash, role, farm_id "
        "FROM users WHERE email = ? AND role = ? AND is_enabled = 1",
        (email.strip().lower(), required_role)
    ).fetchone()
    db.close()

    if row and check_password_hash(row['password_hash'], password):
        return User(row['id'], row['name'], row['email'],
                    row['role'], row['farm_id'])
    return None


# ── Landing page ─────────────────────────────────────────────────────────────

@auth_bp.route('/')
def index():
    return render_template('public/index.html')


# ── Admin login ──────────────────────────────────────────────────────────────

@auth_bp.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    error = None
    if request.method == 'POST':
        email    = request.form.get('email', '')
        password = request.form.get('password', '')
        user = attempt_login(email, password, 'admin')
        if user:
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        error = 'Invalid email or password, or not an admin account.'

    return render_template('public/login_admin.html', error=error)


# ── Farm Manager login ───────────────────────────────────────────────────────

@auth_bp.route('/login/manager', methods=['GET', 'POST'])
def login_manager():
    if current_user.is_authenticated:
        return redirect(url_for('manager.home'))

    error = None
    if request.method == 'POST':
        email    = request.form.get('email', '')
        password = request.form.get('password', '')
        user = attempt_login(email, password, 'manager')
        if user:
            login_user(user)
            return redirect(url_for('manager.home'))
        error = 'Invalid email or password, or not a farm manager account.'

    return render_template('public/login_manager.html', error=error)


# ── Veterinarian login ───────────────────────────────────────────────────────

@auth_bp.route('/login/vet', methods=['GET', 'POST'])
def login_vet():
    if current_user.is_authenticated:
        return redirect(url_for('vet.dashboard'))

    error = None
    if request.method == 'POST':
        email    = request.form.get('email', '')
        password = request.form.get('password', '')
        user = attempt_login(email, password, 'vet')
        if user:
            login_user(user)
            return redirect(url_for('vet.dashboard'))
        error = 'Invalid email or password, or not a veterinarian account.'

    return render_template('public/login_vet.html', error=error)


# ── Logout ───────────────────────────────────────────────────────────────────

@auth_bp.route('/logout')
@login_required
def logout():
    role = current_user.role
    logout_user()
    if role == 'admin':
        return redirect(url_for('auth.login_admin') + '?logged_out=1')
    elif role == 'manager':
        return redirect(url_for('auth.login_manager') + '?logged_out=1')
    else:
        return redirect(url_for('auth.login_vet') + '?logged_out=1')
