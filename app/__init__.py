
import os

from flask import Flask, app


from app.cli import create_admin, reset_admin_password
from config import DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate, login_manager, bcrypt, csrf



@login_manager.user_loader
def load_user(user_id):
    from app.models import User

    try:
        user_id, session_version = user_id.split(":", 1)

        user = db.session.get(User, int(user_id))

        if user is None or not user.is_active:
            return None

        if user.session_version != int(session_version):
            return None

        return user

    except (ValueError, TypeError, AttributeError):
        return None



def create_app(config_class=None):
    app = Flask(
        __name__,
        instance_relative_config=True
    )

    if config_class is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

        config_class = (
            ProductionConfig
            if config_name == "production"
            else DevelopmentConfig
        )

    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.session_protection = "strong"
    bcrypt.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login" # type: ignore
    login_manager.login_message_category = "info"

    # Import models for SQLAlchemy discovery.       
    from app import models

    # Register blueprints.
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.staff import staff_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(staff_bp)

    from app.cli import create_admin, reset_admin_password
    app.cli.add_command(create_admin)
    app.cli.add_command(reset_admin_password)   

    return app
