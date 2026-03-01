"""Initialize database tables and create admin user."""
import sys
import time

from sqlalchemy import text

from app.database import engine, SessionLocal, Base
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


def init():
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == settings.admin_username).first()
        if not existing:
            admin = User(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
            )
            db.add(admin)
            db.commit()
            print(f"Admin user '{settings.admin_username}' created.")
        else:
            print(f"Admin user '{settings.admin_username}' already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    init()
