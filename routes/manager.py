"""
FarmVet Connect - Farm Manager Routes
"""

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, current_app)
from flask_login import login_required, current_user
from database import get_db
from services.questionnaire import get_questions, calculate_severity, CATEGORIES
from services.uploads import save_upload, get_file_icon, is_image
from services.email_service import notify_vet_new_case
import os

manager_bp = Blueprint('manager', __name__)


@manager_bp.route('/home')
@login_required
def home():
    if current_user.role != 'manager':
        flash('Access denied.', 'error')
        return redirect(url_for('auth.index'))
    db = get_db()
    animals = db.execute("""
        SELECT a.*,
               (SELECT status FROM health_reports
                WHERE animal_id = a.id
                ORDER BY created_at DESC LIMIT 1) as latest_status
        FROM animals a
        WHERE a.farm_id = ?
        ORDER BY a.name
    """, (current_user.farm_id,)).fetchall()
    db.close()
    return render_template('manager/home.html', animals=animals)


@manager_bp.route('/animal/add', methods=['GET', 'POST'])
@login_required
def animal_add():
    if current_user.role != 'manager':
        flash('Access denied.', 'error')
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        name       = request.form.get('name', '').strip()
        tag_number = request.form.get('tag_number', '').strip()
        species    = request.form.get('species', '').strip()
        breed      = request.form.get('breed', '').strip()
        dob        = request.form.get('dob', '').strip()
        sex        = request.form.get('sex', '').strip()
        weight_kg  = request.form.get('weight_kg', '').strip()
        notes      = request.form.get('notes', '').strip()

        if not species:
            flash('Species is required.', 'error')
            return render_template('manager/animal_add.html')

        db = get_db()
        db.execute("""
            INSERT INTO animals (farm_id, name, tag_number, species, breed,
                                 dob, sex, weight_kg, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (current_user.farm_id,
              name or None, tag_number or None, species,
              breed or None, dob or None, sex or None,
              float(weight_kg) if weight_kg else None,
              notes or None))
        db.commit()
        db.close()
        flash('Animal added successfully!', 'success')
        return redirect(url_for('manager.home'))

    return render_template('manager/animal_add.html')


@manager_bp.route('/report/structured/<int:animal_id>', methods=['GET', 'POST'])
@login_required
def report_structured(animal_id):
    if current_user.role != 'manager':
        flash('Access denied.', 'error')
        return redirect(url_for('auth.index'))

    db = get_db()
    animal = db.execute(
        "SELECT * FROM animals WHERE id = ? AND farm_id = ?",
        (animal_id, current_user.farm_id)
    ).fetchone()

    if not animal:
        flash('Animal not found.', 'error')
        return redirect(url_for('manager.home'))

    selected_category = request.form.get('symptom_category') or request.args.get('category')
    questions = get_questions(selected_category) if selected_category else []

    if request.method == 'POST' and request.form.get('submit') == 'final':
        farm_location    = request.form.get('farm_location', '').strip()
        symptom_category = request.form.get('symptom_category', '').strip()
        description      = request.form.get('description', '').strip()

        if not symptom_category:
            flash('Please select a symptom category.', 'error')
            return render_template('manager/report_structured.html',
                                   animal=animal, categories=CATEGORIES,
                                   selected_category=selected_category,
                                   questions=questions)

        answers = {}
        for q in questions:
            ans = request.form.get(f'q_{q["id"]}', '').strip()
            if ans:
                answers[q['text']] = ans

        severity = calculate_severity(answers)

        cursor = db.execute("""
            INSERT INTO health_reports
                (animal_id, manager_id, report_type, status,
                 symptom_category, description, farm_location, severity_score)
            VALUES (?, ?, 'structured', 'pending', ?, ?, ?, ?)
        """, (animal_id, current_user.id, symptom_category,
              description, farm_location, severity))
        report_id = cursor.lastrowid

        for question, answer in answers.items():
            db.execute("""
                INSERT INTO questionnaire_answers (report_id, question, answer)
                VALUES (?, ?, ?)
            """, (report_id, question, answer))

        # Handle file uploads
        files = request.files.getlist('files')
        for file in files:
            if file and file.filename:
                result = save_upload(file, subfolder='reports')
                if result:
                    db.execute("""
                        INSERT INTO file_uploads
                            (report_id, filename, original_filename,
                             file_type, file_size_bytes, uploaded_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (report_id, result['filename'],
                          result['original_filename'],
                          result['file_type'], 0, current_user.id))

        db.commit()

        # Email notification to all vets
        vets = db.execute("""
            SELECT name, email FROM users
            WHERE role = 'vet' AND is_enabled = 1
        """).fetchall()

        farm = db.execute(
            "SELECT name FROM farms WHERE id = ?",
            (current_user.farm_id,)
        ).fetchone()

        for vet in vets:
            notify_vet_new_case(
                vet_email=vet['email'],
                vet_name=vet['name'],
                animal_name=animal['name'] or animal['tag_number'] or 'Unknown',
                farm_name=farm['name'] if farm else 'Unknown Farm',
                category=symptom_category,
                severity=severity,
                report_id=report_id
            )

        db.close()
        flash('Health report submitted! A vet will review it shortly.', 'success')
        return redirect(url_for('manager.home'))

    db.close()
    return render_template('manager/report_structured.html',
                           animal=animal, categories=CATEGORIES,
                           selected_category=selected_category,
                           questions=questions)


@manager_bp.route('/report/freetext/<int:animal_id>', methods=['GET', 'POST'])
@login_required
def report_freetext(animal_id):
    if current_user.role != 'manager':
        flash('Access denied.', 'error')
        return redirect(url_for('auth.index'))

    db = get_db()
    animal = db.execute(
        "SELECT * FROM animals WHERE id = ? AND farm_id = ?",
        (animal_id, current_user.farm_id)
    ).fetchone()

    if not animal:
        flash('Animal not found.', 'error')
        return redirect(url_for('manager.home'))

    if request.method == 'POST':
        farm_location = request.form.get('farm_location', '').strip()
        description   = request.form.get('description', '').strip()

        if not description:
            flash('Please describe the symptoms.', 'error')
            return render_template('manager/report_freetext.html', animal=animal)

        cursor = db.execute("""
            INSERT INTO health_reports
                (animal_id, manager_id, report_type, status,
                 description, farm_location, severity_score)
            VALUES (?, ?, 'freetext', 'pending', ?, ?, 3)
        """, (animal_id, current_user.id, description, farm_location))
        report_id = cursor.lastrowid

        # Handle file uploads
        files = request.files.getlist('files')
        for file in files:
            if file and file.filename:
                result = save_upload(file, subfolder='reports')
                if result:
                    db.execute("""
                        INSERT INTO file_uploads
                            (report_id, filename, original_filename,
                             file_type, file_size_bytes, uploaded_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (report_id, result['filename'],
                          result['original_filename'],
                          result['file_type'], 0, current_user.id))

        db.commit()

        # Email notification to all vets
        vets = db.execute("""
            SELECT name, email FROM users
            WHERE role = 'vet' AND is_enabled = 1
        """).fetchall()

        farm = db.execute(
            "SELECT name FROM farms WHERE id = ?",
            (current_user.farm_id,)
        ).fetchone()

        for vet in vets:
            notify_vet_new_case(
                vet_email=vet['email'],
                vet_name=vet['name'],
                animal_name=animal['name'] or animal['tag_number'] or 'Unknown',
                farm_name=farm['name'] if farm else 'Unknown Farm',
                category='Free Text Report',
                severity=3,
                report_id=report_id
            )

        db.close()
        flash('Report submitted! A vet will review it shortly.', 'success')
        return redirect(url_for('manager.home'))

    db.close()
    return render_template('manager/report_freetext.html', animal=animal)


@manager_bp.route('/vitals/<int:animal_id>', methods=['GET', 'POST'])
@login_required
def vitals_add(animal_id):
    if current_user.role != 'manager':
        flash('Access denied.', 'error')
        return redirect(url_for('auth.index'))

    db = get_db()
    animal = db.execute(
        "SELECT * FROM animals WHERE id = ? AND farm_id = ?",
        (animal_id, current_user.farm_id)
    ).fetchone()

    if not animal:
        flash('Animal not found.', 'error')
        return redirect(url_for('manager.home'))

    reports = db.execute("""
        SELECT id, symptom_category, created_at FROM health_reports
        WHERE animal_id = ? AND status != 'closed'
        ORDER BY created_at DESC
    """, (animal_id,)).fetchall()

    if request.method == 'POST':
        def get_float(key):
            val = request.form.get(key, '').strip()
            return float(val) if val else None

        def get_int(key):
            val = request.form.get(key, '').strip()
            return int(val) if val else None

        report_id        = get_int('report_id')
        temperature      = get_float('temperature_celsius')
        weight_kg        = get_float('weight_kg')
        heart_rate       = get_int('heart_rate_bpm')
        respiratory_rate = get_int('respiratory_rate')
        bcs              = get_int('body_condition_score')
        rumen_sounds     = request.form.get('rumen_sounds', '').strip() or None
        mucous_membrane  = request.form.get('mucous_membrane_color', '').strip() or None

        db.execute("""
            INSERT INTO vitals (animal_id, report_id, temperature_celsius,
                weight_kg, heart_rate_bpm, respiratory_rate,
                body_condition_score, rumen_sounds, mucous_membrane_color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (animal_id, report_id, temperature, weight_kg,
              heart_rate, respiratory_rate, bcs, rumen_sounds, mucous_membrane))
        db.commit()
        db.close()
        flash('Vitals recorded successfully!', 'success')
        return redirect(url_for('manager.home'))

    db.close()
    return render_template('manager/vitals_add.html',
                           animal=animal, reports=reports)


@manager_bp.route('/history/<int:animal_id>')
@login_required
def event_history(animal_id):
    if current_user.role != 'manager':
        flash('Access denied.', 'error')
        return redirect(url_for('auth.index'))

    db = get_db()
    animal = db.execute(
        "SELECT * FROM animals WHERE id = ? AND farm_id = ?",
        (animal_id, current_user.farm_id)
    ).fetchone()

    if not animal:
        flash('Animal not found.', 'error')
        return redirect(url_for('manager.home'))

    reports = db.execute("""
        SELECT hr.*, u.name as vet_name
        FROM health_reports hr
        LEFT JOIN users u ON hr.vet_id = u.id
        WHERE hr.animal_id = ?
        ORDER BY hr.created_at DESC
    """, (animal_id,)).fetchall()

    timeline = []
    for r in reports:
        messages = db.execute("""
            SELECT m.*, u.name as sender_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.report_id = ?
            ORDER BY m.created_at ASC
        """, (r['id'],)).fetchall()

        answers = db.execute("""
            SELECT question, answer FROM questionnaire_answers
            WHERE report_id = ?
        """, (r['id'],)).fetchall()

        vitals = db.execute("""
            SELECT * FROM vitals
            WHERE report_id = ? OR animal_id = ?
            ORDER BY created_at DESC LIMIT 3
        """, (r['id'], animal_id)).fetchall()

        uploads = db.execute("""
            SELECT * FROM file_uploads
            WHERE report_id = ?
            ORDER BY created_at ASC
        """, (r['id'],)).fetchall()

        timeline.append({
            'report': r,
            'messages': messages,
            'answers': answers,
            'vitals': vitals,
            'uploads': uploads
        })

    db.close()
    return render_template('manager/event_history.html',
                           animal=animal, timeline=timeline,
                           get_file_icon=get_file_icon,
                           is_image=is_image)
