"""Wait for database and create initial admin user."""
import sys
import time

from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from app.database import engine, SessionLocal
from app.models import User
from app.auth import hash_password
from app.config import settings


def wait_for_db(retries: int = 30, delay: float = 2.0):
    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is ready.")
            return
        except Exception:
            print(f"Waiting for database... ({i + 1}/{retries})")
            time.sleep(delay)
    print("Could not connect to database.")
    sys.exit(1)


def create_admin():
    """Create initial admin user if not exists. Requires tables to exist (run alembic first)."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == settings.admin_username).first()
        if not existing:
            admin = User(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print(f"Admin user '{settings.admin_username}' created.")
        else:
            print(f"Admin user '{settings.admin_username}' already exists.")
    except ProgrammingError:
        print("Tables not yet created, skipping admin user creation.")
        db.rollback()
    finally:
        db.close()


def init():
    wait_for_db()
    create_admin()


if __name__ == "__main__":
    init()
