"""Database helpers for the TORO Maintenance Orders API."""

from __future__ import annotations

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance shared across modules.
db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """Configure SQLAlchemy on the provided app and create tables.

    By default the database is stored in ``toro.db`` at the project root.
    The location can be overridden via the TORO_DATABASE_URL environment
    variable, e.g. ``sqlite:////tmp/toro.db``.
    """

    database_url = os.getenv("TORO_DATABASE_URL", "sqlite:///toro.db")
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", database_url)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    # Ensure idle connections are verified before each use.
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {"pool_pre_ping": True})

    db.init_app(app)

    with app.app_context():
        db.create_all()


__all__: list[str] = ["db", "init_db"]
