import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "be0c1564a12b606aaa95b6065b63d06380564a39ea11ed809b43c85f4ed5f06f"
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