"""
FarmVet Connect - Configuration
"""

import os
import secrets

class Config:
    SECRET_KEY    = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    DATABASE      = os.path.join(os.path.dirname(__file__), 'farmvet.db')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx'}
