import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Fetch the secret database URL from Streamlit Cloud
# (If you run this locally, it will temporarily fall back to SQLite)
try:
    SQLALCHEMY_DATABASE_URL = st.secrets["DATABASE_URL"]
except FileNotFoundError:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./bannu_tutoring.db"

# 2. Set up the engine 
# (PostgreSQL handles connections slightly differently than SQLite)
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()