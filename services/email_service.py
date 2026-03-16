"""
FarmVet Connect - Email Notification Service
Sends notifications via Gmail SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


# ── Config — set these in your environment or directly here ──
GMAIL_USER     = os.environ.get('FARMVET_EMAIL', '')
GMAIL_PASSWORD = os.environ.get('FARMVET_EMAIL_PASSWORD', '')
APP_NAME       = 'FarmVet Connect'


def send_email(to_email, subject, html_body):
    """
    Send an email via Gmail SMTP.
    Returns True if sent, False if failed.
    """
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print(f"[EMAIL SKIPPED] No credentials set. Would send to: {to_email}")
        print(f"[EMAIL SUBJECT] {subject}")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[{APP_NAME}] {subject}"
        msg['From']    = f"{APP_NAME} <{GMAIL_USER}>"
        msg['To']      = to_email

        part = MIMEText(html_body, 'html')
        msg.attach(part)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        print(f"[EMAIL SENT] To: {to_email} | Subject: {subject}")
        return True

    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


def notify_vet_new_case(vet_email, vet_name, animal_name,
                         farm_name, category, severity, report_id):
    """Notify vet when a new health report is submitted."""
    subject = f"New Case: {animal_name} — {category}"
    html = f"""
    <div style="font-family: 'DM Sans', Arial, sans-serif; max-width:600px;
                margin:0 auto; background:#f9fafb; padding:24px;">

        <div style="background:#1a4332; padding:24px; border-radius:12px 12px 0 0;">
            <h1 style="color:white; margin:0; font-size:20px;">
                🐄 FarmVet Connect
            </h1>
            <p style="color:rgba(255,255,255,0.7); margin:4px 0 0; font-size:13px;">
                Veterinary Notification
            </p>
        </div>

        <div style="background:white; padding:28px; border-radius:0 0 12px 12px;
                    border:1px solid #e5e7eb; border-top:none;">
            <p style="color:#374151; font-size:15px;">Hi {vet_name},</p>
            <p style="color:#374151; font-size:15px;">
                A new health report has been submitted and requires your review.
            </p>

            <div style="background:#f0faf4; border-left:4px solid #40916c;
                        padding:16px 20px; border-radius:0 8px 8px 0; margin:20px 0;">
                <table style="width:100%; font-size:14px; color:#374151;">
                    <tr>
                        <td style="padding:4px 0; font-weight:600; width:140px;">Animal</td>
                        <td style="padding:4px 0;">{animal_name}</td>
                    </tr>
                    <tr>
                        <td style="padding:4px 0; font-weight:600;">Farm</td>
                        <td style="padding:4px 0;">{farm_name}</td>
                    </tr>
                    <tr>
                        <td style="padding:4px 0; font-weight:600;">Category</td>
                        <td style="padding:4px 0;">{category}</td>
                    </tr>
                    <tr>
                        <td style="padding:4px 0; font-weight:600;">Severity</td>
                        <td style="padding:4px 0;">{'⭐' * severity} ({severity}/5)</td>
                    </tr>
                </table>
            </div>

            <p style="color:#374151; font-size:14px;">
                Please log in to FarmVet Connect to review the full case details
                and submit your treatment plan.
            </p>

            <div style="text-align:center; margin:28px 0;">
                <a href="http://127.0.0.1:5000/vet/case/{report_id}"
                   style="background:#2d6a4f; color:white; padding:12px 28px;
                          border-radius:6px; text-decoration:none; font-weight:600;
                          font-size:14px;">
                    View Case #{report_id}
                </a>
            </div>

            <p style="color:#9ca3af; font-size:12px; text-align:center; margin-top:24px;">
                FarmVet Connect — Remote Livestock Health Management
            </p>
        </div>
    </div>
    """
    return send_email(vet_email, subject, html)


def notify_manager_case_answered(manager_email, manager_name,
                                  animal_name, vet_name, report_id):
    """Notify farm manager when vet sends a treatment plan."""
    subject = f"Treatment Plan Ready: {animal_name}"
    html = f"""
    <div style="font-family: 'DM Sans', Arial, sans-serif; max-width:600px;
                margin:0 auto; background:#f9fafb; padding:24px;">

        <div style="background:#1a4332; padding:24px; border-radius:12px 12px 0 0;">
            <h1 style="color:white; margin:0; font-size:20px;">
                🐄 FarmVet Connect
            </h1>
            <p style="color:rgba(255,255,255,0.7); margin:4px 0 0; font-size:13px;">
                Treatment Plan Notification
            </p>
        </div>

        <div style="background:white; padding:28px; border-radius:0 0 12px 12px;
                    border:1px solid #e5e7eb; border-top:none;">
            <p style="color:#374151; font-size:15px;">Hi {manager_name},</p>
            <p style="color:#374151; font-size:15px;">
                Good news — <strong>Dr. {vet_name}</strong> has reviewed your
                health report for <strong>{animal_name}</strong> and sent a
                treatment plan.
            </p>

            <div style="background:#f0faf4; border-left:4px solid #40916c;
                        padding:16px 20px; border-radius:0 8px 8px 0; margin:20px 0;">
                <p style="margin:0; font-size:14px; color:#374151;">
                    ✅ Your case has been answered. Please log in to view the
                    full diagnosis and treatment instructions.
                </p>
            </div>

            <div style="text-align:center; margin:28px 0;">
                <a href="http://127.0.0.1:5000/manager/history/1"
                   style="background:#2d6a4f; color:white; padding:12px 28px;
                          border-radius:6px; text-decoration:none; font-weight:600;
                          font-size:14px;">
                    View Treatment Plan
                </a>
            </div>

            <p style="color:#9ca3af; font-size:12px; text-align:center; margin-top:24px;">
                FarmVet Connect — Remote Livestock Health Management
            </p>
        </div>
    </div>
    """
    return send_email(manager_email, subject, html)
