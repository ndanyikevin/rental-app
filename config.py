import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "development-key-change-before-production"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///rental_management.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Kenyan Shilling is the application's default currency.
    DEFAULT_CURRENCY = "KES"

    # Session security settings.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False