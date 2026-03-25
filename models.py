from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base # Make sure this is the ONLY thing coming from database

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String) 
    role = Column(String) # 'student' or 'tutor'

    # --- NEW FIELDS FOR YOUR M.PHIL PROFILE ---
    specialization = Column(String, nullable=True) # e.g., "General Relativity"
    bio = Column(String, nullable=True)            # e.g., "M.Phil in Mathematics from QAU"
    experience = Column(String, nullable=True)     # e.g., "5 Years Teaching"

    # Keeps your relationship for advanced profile features later
    tutor_profile = relationship("TutorProfile", back_populates="user", uselist=False)


class TutorProfile(Base):
    __tablename__ = "tutor_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subjects = Column(String)
    grade_levels = Column(String)
    hourly_rate = Column(Float)
    user = relationship("User", back_populates="tutor_profile")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    student_phone = Column(String) # Who is booking
    subject = Column(String)       # e.g., "M.Phil Mathematics" or "9th Physics"
    lesson_date = Column(String)   # e.g., "2026-03-25"
    lesson_time = Column(String)   # e.g., "10:00 AM"
    status = Column(String, default="Pending") # Pending, Confirmed, or Completed