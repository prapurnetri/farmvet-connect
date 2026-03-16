"""
FarmVet Connect - Database Layer
Handles SQLite connection and all table creation
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from flask import current_app
from flask_login import UserMixin


# ─────────────────────────────────────────────
# User class (needed by Flask-Login)
# ─────────────────────────────────────────────

class User(UserMixin):
    """Represents a logged-in user."""
    def __init__(self, id, name, email, role, farm_id=None):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.farm_id = farm_id


# ─────────────────────────────────────────────
# Database connection helper
# ─────────────────────────────────────────────

def get_db():
    """Open a connection to the SQLite database."""
    db_path = current_app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_user_by_id(user_id):
    """Load a user by ID — used by Flask-Login."""
    with sqlite3.connect(current_app.config['DATABASE']) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, name, email, role, farm_id FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        if row:
            return User(row['id'], row['name'], row['email'],
                        row['role'], row['farm_id'])
    return None


# ─────────────────────────────────────────────
# Database initialisation — creates all tables
# ─────────────────────────────────────────────

def init_db():
    """Create all tables and seed a default admin user."""
    db_path = os.path.join(os.path.dirname(__file__), 'farmvet.db')
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    # ── Table 1: farms ──────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS farms (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            owner_name  TEXT,
            location    TEXT,
            region      TEXT,
            latitude    REAL,
            longitude   REAL,
            phone       TEXT,
            email       TEXT,
            is_enabled  INTEGER DEFAULT 1,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 2: users ──────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL CHECK(role IN ('admin','vet','manager')),
            farm_id       INTEGER REFERENCES farms(id),
            is_enabled    INTEGER DEFAULT 1,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 3: animals ────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS animals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_id     INTEGER NOT NULL REFERENCES farms(id),
            name        TEXT,
            tag_number  TEXT,
            species     TEXT NOT NULL,
            breed       TEXT,
            dob         DATE,
            sex         TEXT CHECK(sex IN ('Male','Female','Unknown')),
            weight_kg   REAL,
            notes       TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 4: health_reports ─────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS health_reports (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id         INTEGER NOT NULL REFERENCES animals(id),
            manager_id        INTEGER NOT NULL REFERENCES users(id),
            vet_id            INTEGER REFERENCES users(id),
            report_type       TEXT NOT NULL CHECK(report_type IN ('structured','freetext')),
            status            TEXT NOT NULL DEFAULT 'pending'
                                  CHECK(status IN ('pending','answered','closed')),
            symptom_category  TEXT,
            description       TEXT,
            farm_location     TEXT,
            severity_score    INTEGER CHECK(severity_score BETWEEN 1 AND 5),
            disease_code      TEXT,
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 5: questionnaire_answers ──────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS questionnaire_answers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id   INTEGER NOT NULL REFERENCES health_reports(id),
            question    TEXT NOT NULL,
            answer      TEXT NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 6: messages ───────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id   INTEGER NOT NULL REFERENCES health_reports(id),
            sender_id   INTEGER NOT NULL REFERENCES users(id),
            sender_role TEXT NOT NULL CHECK(sender_role IN ('manager','vet','admin')),
            message     TEXT NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 7: vitals ─────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS vitals (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id             INTEGER NOT NULL REFERENCES animals(id),
            report_id             INTEGER REFERENCES health_reports(id),
            temperature_celsius   REAL,
            weight_kg             REAL,
            heart_rate_bpm        INTEGER,
            respiratory_rate      INTEGER,
            body_condition_score  INTEGER CHECK(body_condition_score BETWEEN 1 AND 5),
            rumen_sounds          TEXT,
            mucous_membrane_color TEXT,
            lab_result_file       TEXT,
            ultrasound_file       TEXT,
            fecal_test_file       TEXT,
            created_at            DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 8: file_uploads ───────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS file_uploads (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id         INTEGER NOT NULL REFERENCES health_reports(id),
            filename          TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_type         TEXT,
            file_size_bytes   INTEGER,
            uploaded_by       INTEGER REFERENCES users(id),
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 9: video_consultations ────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS video_consultations (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id       INTEGER REFERENCES health_reports(id),
            animal_id       INTEGER NOT NULL REFERENCES animals(id),
            manager_id      INTEGER NOT NULL REFERENCES users(id),
            vet_id          INTEGER REFERENCES users(id),
            requested_date  DATE NOT NULL,
            requested_time  TEXT NOT NULL,
            duration_mins   INTEGER DEFAULT 30,
            status          TEXT DEFAULT 'requested'
                                CHECK(status IN ('requested','confirmed',
                                                  'rejected','rescheduled','completed')),
            manager_note    TEXT,
            vet_response    TEXT,
            proposed_date   DATE,
            proposed_time   TEXT,
            meeting_url     TEXT,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Table 10: herd_alerts (unique feature) ──────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS herd_alerts (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_id           INTEGER NOT NULL REFERENCES farms(id),
            symptom_category  TEXT NOT NULL,
            animal_count      INTEGER NOT NULL,
            first_report_date DATE,
            alert_level       TEXT CHECK(alert_level IN ('watch','warning','critical')),
            resolved          INTEGER DEFAULT 0,
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Seed default admin user ──────────────────────────────────────────────
    existing = c.execute(
        "SELECT id FROM users WHERE email = 'admin@farmvet.com'"
    ).fetchone()

    if not existing:
        c.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (
            'Admin User',
            'admin@farmvet.com',
            generate_password_hash('admin123'),
            'admin'
        ))
        print("✓ Default admin created: admin@farmvet.com / admin123")

    conn.commit()
    conn.close()
    print("✓ Database initialised — all 10 tables ready")
