"""
FarmVet Connect - File Upload Service
Handles secure file uploads for health reports
"""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file, subfolder='reports'):
    """
    Save an uploaded file securely.
    Returns the saved filename or None if failed.
    """
    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename):
        return None

    # Generate unique filename to prevent overwrites
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    original_name = secure_filename(file.filename)

    # Create subfolder if it doesn't exist
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, unique_name)
    file.save(filepath)

    return {
        'filename': unique_name,
        'original_filename': original_name,
        'file_type': ext,
        'subfolder': subfolder
    }


def get_file_icon(file_type):
    """Return an emoji icon based on file type."""
    icons = {
        'pdf': '📄',
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
        'doc': '📝', 'docx': '📝',
    }
    return icons.get(file_type.lower(), '📎')


def is_image(file_type):
    return file_type.lower() in {'jpg', 'jpeg', 'png', 'gif'}
