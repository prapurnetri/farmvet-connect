"""
FarmVet Connect - Admin Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from database import get_db

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('auth.login_admin'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    db = get_db()
    stats = {
        'total_users':   db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        'total_farms':   db.execute("SELECT COUNT(*) FROM farms").fetchone()[0],
        'total_animals': db.execute("SELECT COUNT(*) FROM animals").fetchone()[0],
        'total_reports': db.execute("SELECT COUNT(*) FROM health_reports").fetchone()[0],
        'pending':       db.execute("SELECT COUNT(*) FROM health_reports WHERE status='pending'").fetchone()[0],
        'answered':      db.execute("SELECT COUNT(*) FROM health_reports WHERE status='answered'").fetchone()[0],
        'closed':        db.execute("SELECT COUNT(*) FROM health_reports WHERE status='closed'").fetchone()[0],
        'alerts':        db.execute("SELECT COUNT(*) FROM herd_alerts WHERE resolved=0").fetchone()[0],
    }
    recent_reports = db.execute("""
        SELECT hr.*, a.name as animal_name, a.species,
               f.name as farm_name
        FROM health_reports hr
        JOIN animals a ON hr.animal_id = a.id
        JOIN farms f ON a.farm_id = f.id
        ORDER BY hr.created_at DESC LIMIT 5
    """).fetchall()
    db.close()
    return render_template('admin/dashboard.html',
                           stats=stats, recent_reports=recent_reports)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    db = get_db()
    all_users = db.execute("""
        SELECT u.*, f.name as farm_name
        FROM users u
        LEFT JOIN farms f ON u.farm_id = f.id
        ORDER BY u.role, u.name
    """).fetchall()
    db.close()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def user_add():
    db = get_db()
    farms = db.execute("SELECT id, name FROM farms ORDER BY name").fetchall()

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        role     = request.form.get('role', '').strip()
        farm_id  = request.form.get('farm_id', '').strip()

        if not all([name, email, password, role]):
            flash('All fields are required.', 'error')
            return render_template('admin/user_add.html', farms=farms)

        if role == 'manager' and not farm_id:
            flash('Farm managers must be assigned to a farm.', 'error')
            return render_template('admin/user_add.html', farms=farms)

        try:
            db.execute("""
                INSERT INTO users (name, email, password_hash, role, farm_id)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, generate_password_hash(password),
                  role, int(farm_id) if farm_id else None))
            db.commit()
            flash(f'{role.capitalize()} account created for {name}!', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            flash('Email already exists or error occurred.', 'error')

    db.close()
    return render_template('admin/user_add.html', farms=farms)


@admin_bp.route('/user/toggle/<int:user_id>')
@login_required
@admin_required
def user_toggle(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user and user['role'] != 'admin':
        new_status = 0 if user['is_enabled'] else 1
        db.execute("UPDATE users SET is_enabled = ? WHERE id = ?",
                   (new_status, user_id))
        db.commit()
        flash(f'User {"enabled" if new_status else "disabled"} successfully.', 'success')
    db.close()
    return redirect(url_for('admin.users'))


@admin_bp.route('/farms')
@login_required
@admin_required
def farms():
    db = get_db()
    all_farms = db.execute("""
        SELECT f.*,
               COUNT(DISTINCT a.id) as animal_count,
               COUNT(DISTINCT u.id) as user_count
        FROM farms f
        LEFT JOIN animals a ON a.farm_id = f.id
        LEFT JOIN users u ON u.farm_id = f.id
        GROUP BY f.id
        ORDER BY f.name
    """).fetchall()
    db.close()
    return render_template('admin/farms.html', farms=all_farms)


@admin_bp.route('/farm/add', methods=['GET', 'POST'])
@login_required
@admin_required
def farm_add():
    if request.method == 'POST':
        name       = request.form.get('name', '').strip()
        owner_name = request.form.get('owner_name', '').strip()
        location   = request.form.get('location', '').strip()
        region     = request.form.get('region', '').strip()
        phone      = request.form.get('phone', '').strip()
        email      = request.form.get('email', '').strip()

        if not name:
            flash('Farm name is required.', 'error')
            return render_template('admin/farm_add.html')

        db = get_db()
        db.execute("""
            INSERT INTO farms (name, owner_name, location, region, phone, email)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, owner_name or None, location or None,
              region or None, phone or None, email or None))
        db.commit()
        db.close()
        flash(f'Farm "{name}" added successfully!', 'success')
        return redirect(url_for('admin.farms'))

    return render_template('admin/farm_add.html')
