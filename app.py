"""
FarmVet Connect - Remote Livestock Health Management Platform
Main Flask application entry point
"""

from flask import Flask
from flask_login import LoginManager
from config import Config
from database import init_db, get_user_by_id

# Import route blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.manager import manager_bp
from routes.vet import vet_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database (creates all tables if they don't exist)
    init_db()

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_admin'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(int(user_id))

    # Register blueprints (groups of routes)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(vet_bp, url_prefix='/vet')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
