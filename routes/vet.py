"""
FarmVet Connect - Veterinarian Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database import get_db
from services.uploads import get_file_icon, is_image
from services.email_service import notify_manager_case_answered

vet_bp = Blueprint('vet', __name__)


@vet_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'vet':
        flash('Access denied.', 'error')
        return redirect(url_for('auth.index'))

    db = get_db()
    filter_status = request.args.get('status', 'pending')

    if filter_status == 'all':
        reports = db.execute("""
            SELECT hr.*, a.name as animal_name, a.species, a.tag_number,
                   f.name as farm_name, u.name as manager_name
            FROM health_reports hr
            JOIN animals a ON hr.animal_id = a.id
            JOIN farms f ON a.farm_id = f.id
            JOIN users u ON hr.manager_id = u.id
            ORDER BY hr.created_at DESC
        """).fetchall()
    else:
        reports = db.execute("""
            SELECT hr.*, a.name as animal_name, a.species, a.tag_number,
                   f.name as farm_name, u.name as manager_name
            FROM health_reports hr
            JOIN animals a ON hr.animal_id = a.id
            JOIN farms f ON a.farm_id = f.id
            JOIN users u ON hr.manager_id = u.id
            WHERE hr.status = ?
            ORDER BY hr.created_at DESC
        """, (filter_status,)).fetchall()

    db.close()
    return render_template('vet/dashboard.html', reports=reports,
                           filter_status=filter_status)


@vet_bp.route('/case/<int:report_id>', methods=['GET', 'POST'])
@login_required
def case_view(report_id):
    if current_user.role != 'vet':
        flash('Access denied.', 'error')
        return redirect(url_for('auth.index'))

    db = get_db()

    report = db.execute("""
        SELECT hr.*,
               a.name as animal_name, a.species, a.breed,
               a.tag_number, a.sex, a.dob, a.weight_kg,
               f.name as farm_name, f.location as farm_location,
               f.region as farm_region,
               u.name as manager_name, u.email as manager_email
        FROM health_reports hr
        JOIN animals a ON hr.animal_id = a.id
        JOIN farms f ON a.farm_id = f.id
        JOIN users u ON hr.manager_id = u.id
        WHERE hr.id = ?
    """, (report_id,)).fetchone()

    if not report:
        flash('Case not found.', 'error')
        return redirect(url_for('vet.dashboard'))

    answers = db.execute("""
        SELECT question, answer FROM questionnaire_answers
        WHERE report_id = ?
        ORDER BY id
    """, (report_id,)).fetchall()

    vitals = db.execute("""
        SELECT * FROM vitals
        WHERE animal_id = ?
        ORDER BY created_at DESC LIMIT 5
    """, (report['animal_id'],)).fetchall()

    messages = db.execute("""
        SELECT m.*, u.name as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.report_id = ?
        ORDER BY m.created_at ASC
    """, (report_id,)).fetchall()

    uploads = db.execute("""
        SELECT * FROM file_uploads
        WHERE report_id = ?
        ORDER BY created_at ASC
    """, (report_id,)).fetchall()

    if request.method == 'POST':
        treatment  = request.form.get('treatment', '').strip()
        new_status = request.form.get('status', 'answered')

        if not treatment:
            flash('Please write a treatment plan before submitting.', 'error')
            return render_template('vet/case_view.html',
                                   report=report, answers=answers,
                                   vitals=vitals, messages=messages,
                                   uploads=uploads,
                                   get_file_icon=get_file_icon,
                                   is_image=is_image)

        db.execute("""
            INSERT INTO messages (report_id, sender_id, sender_role, message)
            VALUES (?, ?, 'vet', ?)
        """, (report_id, current_user.id, treatment))

        db.execute("""
            UPDATE health_reports
            SET status = ?, vet_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_status, current_user.id, report_id))

        db.commit()

        # Send email to farm manager
        notify_manager_case_answered(
            manager_email=report['manager_email'],
            manager_name=report['manager_name'],
            animal_name=report['animal_name'] or report['tag_number'] or 'Unknown',
            vet_name=current_user.name,
            report_id=report_id
        )

        db.close()
        flash('Treatment plan sent successfully!', 'success')
        return redirect(url_for('vet.dashboard'))

    db.close()
    return render_template('vet/case_view.html',
                           report=report, answers=answers,
                           vitals=vitals, messages=messages,
                           uploads=uploads,
                           get_file_icon=get_file_icon,
                           is_image=is_image)
