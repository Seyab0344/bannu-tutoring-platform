from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, security
# We need to import SessionLocal so the get_db function works!
from database import engine, SessionLocal, get_db
# We import these specific functions so you can use them by name
from security import get_password_hash, verify_password, create_access_token, get_current_user

# This builds the database tables if they don't exist yet
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bannu Online Tutoring API")

# This is a helper function that opens a temporary connection to your database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Your welcome message
@app.get("/")
def read_root():
    return {"message": "Welcome to the Bannu Online Tutoring Backend!"}

# --- NEW FEATURE: SIGN UP ---
# Make sure get_password_hash is imported at the top of main.py!
# from security import get_password_hash

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Phone already registered")
    
    # Create the user with the ROLE included
    hashed_pw = security.get_password_hash(user.password)
    new_user = models.User(
        phone_number=user.phone_number,
        full_name=user.full_name,
        hashed_password=hashed_pw,
        role=user.role  # <--- MAKE SURE THIS IS HERE
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
# --- NEW FEATURE: GET ALL USERS ---
@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    # This tells the database: "Select * FROM users" (Get everything)
    users = db.query(models.User).all()
    return users
# --- NEW FEATURE: CREATE TUTOR PROFILE ---
@app.post("/tutors/")
def create_tutor_profile(profile: schemas.TutorProfileCreate, db: Session = Depends(get_db)):
    # 1. Create the profile linked to a User ID
    new_profile = models.TutorProfile(
        user_id=profile.user_id,
        subjects=profile.subjects,
        grade_levels=profile.grade_levels,
        hourly_rate=profile.hourly_rate
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return {"message": "Tutor profile created!", "profile": new_profile}
# --- NEW FEATURE: BOOK A SESSION ---
# --- You probably have this block twice! ---
@app.post("/book-lesson", response_model=schemas.BookingResponse)
def create_booking(
    booking_data: schemas.BookingCreate, 
    db: Session = Depends(get_db),
    current_user_phone: str = Depends(get_current_user)
):
    new_booking = models.Booking(
        student_phone=current_user_phone,
        subject=booking_data.subject,
        lesson_date=booking_data.lesson_date,
        lesson_time=booking_data.lesson_time
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking
# -------------------------------------------
# --- NEW FEATURE: TUTOR DASHBOARD ---
@app.get("/tutors/{tutor_id}/bookings/")
def get_tutor_dashboard(tutor_id: int, db: Session = Depends(get_db)):
    # This searches for all bookings where the tutor_id matches your ID
    my_sessions = db.query(models.Booking).filter(models.Booking.tutor_id == tutor_id).all()
    
    if not my_sessions:
        return {"message": "No bookings found for this tutor yet."}
    
    return {"tutor_id": tutor_id, "upcoming_sessions": my_sessions}

@app.post("/login")
def login(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Find user
    user = db.query(models.User).filter(models.User.phone_number == user_data.phone_number).first()
    
    # 2. Check password
    if not user or not security.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    # 3. Create token
    access_token = security.create_access_token(data={"sub": user.phone_number})

    # 4. THE HANDSHAKE (Must include 'role'!)
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role  # <--- If this is missing, dashboard.py crashes silently
    }
@app.get("/dashboard")
def student_dashboard(current_user_phone: str = Depends(get_current_user)):
    # If the code reaches here, it means the bouncer checked the key and it was valid!
    return {
        "message": "Welcome to your private dashboard!",
        "user_phone": current_user_phone,
        "secret_data": "Here are your upcoming math and physics tutoring lessons."
    }
# The "list" part tells the server to expect multiple bookings, not just one!
@app.get("/my-bookings", response_model=list[schemas.BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user_phone: str = Depends(get_current_user) # The Bouncer checks the key!
):
    # Search the database for all bookings that belong to this specific phone number
    user_bookings = db.query(models.Booking).filter(models.Booking.student_phone == current_user_phone).all()
    
    return user_bookings

# The "put" method is standard for UPDATING existing data
@app.put("/bookings/{booking_id}/status", response_model=schemas.BookingResponse)
def update_booking_status(
    booking_id: int,
    status_update: schemas.BookingUpdate,
    db: Session = Depends(get_db),
    current_user_phone: str = Depends(get_current_user) # Still checking the security key!
):
    # 1. Search the database for the specific booking by its ID
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    
    # 2. If it doesn't exist, throw an error
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # 3. Update the status, save it, and return the updated data
    booking.status = status_update.status
    db.commit()
    db.refresh(booking)
    
    return booking
# Tutors use this to see ALL bookings in the system
@app.get("/all-bookings", response_model=list[schemas.BookingResponse])
def get_all_bookings(
    db: Session = Depends(get_db),
    current_user_phone: str = Depends(get_current_user) # Still checking security!
):
    # This grabs absolutely everything in the bookings table
    all_bookings = db.query(models.Booking).all()
    return all_bookings
@app.put("/update-profile")
def update_profile(
    profile: schemas.ProfileUpdate, 
    db: Session = Depends(get_db), 
    current_user_phone: str = Depends(get_current_user)
):
    # Find you in the database
    user = db.query(models.User).filter(models.User.phone_number == current_user_phone).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update your M.Phil details
    user.specialization = profile.specialization
    user.bio = profile.bio
    user.experience = profile.experience
    
    db.commit()
    db.refresh(user)
    return {"message": "Tutor Profile updated successfully!"}
@app.get("/tutors", response_model=list[schemas.UserResponse])
def get_all_tutors(db: Session = Depends(get_db)):
    # This grabs everyone who registered as a tutor
    tutors = db.query(models.User).filter(models.User.role == "tutor").all()
    return tutors