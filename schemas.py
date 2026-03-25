from pydantic import BaseModel
from typing import Optional

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    phone_number: str
    full_name: str
    role: str = "student"
    # Added these for your M.Phil Profile
    specialization: Optional[str] = None
    bio: Optional[str] = None
    experience: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# --- TUTOR PROFILE SCHEMAS (Advanced) ---
class TutorProfileCreate(BaseModel):
    user_id: int
    subjects: str        # e.g., "Calculus, Linear Algebra"
    grade_levels: str    # e.g., "MSc, BS, FSc"
    hourly_rate: float

# --- PROFILE UPDATE SCHEMA ---
# This is used when the Tutor clicks "Save Profile" on the dashboard
class ProfileUpdate(BaseModel):
    specialization: str
    bio: str
    experience: str

# --- BOOKING SCHEMAS ---
class BookingCreate(BaseModel):
    subject: str
    lesson_date: str
    lesson_time: str

class BookingResponse(BookingCreate):
    id: int
    student_phone: str
    status: str

    class Config:
        from_attributes = True

# --- STATUS UPDATE SCHEMA ---
class BookingUpdate(BaseModel):
    status: str