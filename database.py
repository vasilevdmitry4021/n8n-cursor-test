"""Database initialization utilities for the TORO API."""
from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance reused across modules
db = SQLAlchemy()


def init_db(app) -> None:
    """
    Configure SQLAlchemy for the provided Flask app and create all tables.

    Parameters
    ----------
    app: Flask
        The application instance to bind the database to.
    """
    # Ensure essential configuration defaults are in place
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///toro.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db.init_app(app)

    # Create database tables on first launch
    with app.app_context():
        db.create_all()
