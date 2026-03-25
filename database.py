from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. The Database File
SQLALCHEMY_DATABASE_URL = "sqlite:///./bannu_tutoring.db"

# 2. The Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Session Maker (CRITICAL: main.py is looking for this name)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 4. Dependency function (CRITICAL: main.py is looking for this name)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()