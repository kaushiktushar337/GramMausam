from app.db import Base, engine
from app.models import db_models  # noqa: F401


if __name__ == "__main__":
    if engine is None:
        raise SystemExit("DATABASE_URL is not configured in .env")

    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
