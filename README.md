# 🐄 FarmVet Connect

**Remote Livestock Health Management & Veterinary Consultation Platform**

FarmVet Connect is a full-stack web application that enables remote farms to submit animal health reports and receive veterinary consultation without requiring an on-site visit. Farm managers report sick animals through structured symptom questionnaires or free-text descriptions, and veterinarians review cases and send back treatment plans — all through a secure, role-based web portal.

---

## 🌐 Live Demo

> Run locally following the setup instructions below.

---

## ✨ Features

### Farm Manager
- Register and manage livestock (cattle, sheep, goats, horses, poultry)
- Submit structured health reports with 10 symptom categories
- Auto-calculated severity scoring (1–5) based on questionnaire answers
- Free-text report submission for open-ended cases
- Upload photos and lab result files (JPG, PNG, PDF)
- Record vital signs (temperature, heart rate, respiratory rate, body condition score)
- View full case event history and vet treatment plans

### Veterinarian
- Dashboard with pending, answered, and closed case filters
- Full case view — questionnaire answers, vitals, uploaded images/files
- Send structured treatment plans and update case status
- Email notification when a new case is submitted

### Admin
- Create and manage vet and farm manager accounts
- Register and manage farm profiles
- Live dashboard with platform statistics
- Enable/disable user accounts

### Platform
- Role-based access control (Admin, Veterinarian, Farm Manager)
- Herd alert system — flags when 3+ animals on the same farm report similar symptoms within 7 days
- Email notifications via Gmail SMTP
- Secure file uploads with type and size validation
- SQLite database with 10 normalised tables
- Responsive UI built with DM Sans + DM Serif Display typography

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Flask 3.0 |
| Database | SQLite (via Python sqlite3) |
| Auth | Flask-Login, Werkzeug password hashing |
| Frontend | HTML5, CSS3 (custom design system), Vanilla JS |
| Email | Gmail SMTP (smtplib) |
| File Uploads | Werkzeug, Pillow |
| Icons | Font Awesome 6 |
| Fonts | DM Sans, DM Serif Display (Google Fonts) |

---

## 📁 Project Structure
```
farmvet-connect/
├── app.py                  # Flask app factory
├── config.py               # Configuration
├── database.py             # SQLite setup, all 10 tables, User model
├── requirements.txt        # Python dependencies
│
├── routes/
│   ├── auth.py             # Login/logout for all 3 roles
│   ├── admin.py            # Admin dashboard, user & farm management
│   ├── manager.py          # Animal registration, health reports, vitals
│   └── vet.py              # Case dashboard, case view, treatment reply
│
├── services/
│   ├── questionnaire.py    # 10 symptom categories, severity scoring
│   ├── uploads.py          # Secure file upload handling
│   └── email_service.py    # Gmail SMTP notifications
│
├── templates/
│   ├── base.html           # Shared layout (header, sidebar)
│   ├── public/             # Login pages, landing page
│   ├── admin/              # Admin pages
│   ├── manager/            # Farm manager pages
│   └── vet/                # Veterinarian pages
│
└── static/
    ├── css/style.css       # Custom design system
    └── js/app.js           # Client-side JS
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation
```bash
# Clone the repository
git clone https://github.com/prapurnetri/farmvet-connect.git
cd farmvet-connect

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 app.py
```

Open your browser at `http://127.0.0.1:5000`

### Default Login
- Email: `admin@farmvet.com`
- Change the password on first login via the Admin panel.

---

## 📧 Email Notifications

The platform sends automated email alerts via Gmail SMTP — vets are notified 
when a new case is submitted, and farm managers are notified when a treatment 
plan is ready.

To configure your Gmail credentials before running:
```bash
export FARMVET_EMAIL="your@gmail.com"
export FARMVET_EMAIL_PASSWORD="your-app-password"
python3 app.py
```

Generate a Gmail App Password at myaccount.google.com → Security → App Passwords.

---

## 🗄️ Database Schema

10 tables: `users`, `farms`, `animals`, `health_reports`, `questionnaire_answers`, `messages`, `vitals`, `file_uploads`, `video_consultations`, `herd_alerts`

---

## 📸 Screenshots

> Add screenshots of the dashboard, health report form, and vet case view here.

---

## 🔮 Roadmap

- [ ] PostgreSQL support for production deployment
- [ ] Real-time notifications (WebSockets)
- [ ] Mobile-responsive improvements
- [ ] PDF report generation
- [ ] Video consultation integration

---

## 👤 Author

**Prapurnetri Vishnubhotla**  
[GitHub](https://github.com/prapurnetri)

---

## 📄 License

This project is for portfolio and demonstration purposes.
