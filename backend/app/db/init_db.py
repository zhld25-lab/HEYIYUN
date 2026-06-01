from __future__ import annotations

"""Initialise database schema and seed reference data.

For local / Docker development we create tables directly from the SQLAlchemy
metadata. Alembic is configured for production-style migrations.
"""

from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine


def create_all() -> None:
    Base.metadata.create_all(bind=engine)


def init() -> None:
    create_all()
    db: Session = SessionLocal()
    try:
        from app.seed.seed_data import seed_all

        seed_all(db)
    finally:
        db.close()


if __name__ == "__main__":
    init()
    print("Database initialised and seeded.")
