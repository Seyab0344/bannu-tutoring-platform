import streamlit as st
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# 1. Initialize Database
models.Base.metadata.create_all(bind=engine)

# 2. Setup Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

st.set_page_config(page_title="Bannu Tutoring", page_icon="📚")
st.title("📚 Bannu Online Tutoring Platform")

# Initialize session state (No more tokens, we just store the user details directly)
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
    st.session_state["role"] = None
    st.session_state["user_phone"] = None
    st.session_state["user_name"] = None

# Open database session for this page load
db = SessionLocal()

# -----------------------------------------
# SCREEN 1: THE LOGIN / REGISTER PAGE
# -----------------------------------------
if st.session_state["user_id"] is None:
    # Sidebar navigation for switching between Login and Sign Up
    choice = st.sidebar.selectbox("Action", ["Login", "Sign Up"])
    
    if choice == "Login":
        st.subheader("🔑 Secure Login")
        login_role = st.radio("I am a:", ["student", "tutor"], horizontal=True)
        
        with st.form("login_form"):
            phone = st.text_input("Phone Number")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                # Direct Database Query
                user = db.query(models.User).filter(
                    models.User.phone_number == phone, 
                    models.User.role == login_role
                ).first()
                
                if user and pwd_context.verify(password, user.hashed_password):
                    st.session_state["user_id"] = user.id
                    st.session_state["role"] = user.role
                    st.session_state["user_phone"] = user.phone_number
                    st.session_state["user_name"] = user.full_name
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please check your phone/password or role.")
    
    else:
        st.subheader("📝 Create New Account")
        reg_role = st.radio("Register as:", ["student", "tutor"], horizontal=True)
        with st.form("reg_form"):
            new_name = st.text_input("Full Name")
            new_phone = st.text_input("Phone Number")
            new_pw = st.text_input("Set Password", type="password")
            
            if st.form_submit_button("Register"):
                existing_user = db.query(models.User).filter(models.User.phone_number == new_phone).first()
                
                if existing_user:
                    st.error("Registration failed. That phone number is already taken.")
                else:
                    hashed_pw = pwd_context.hash(new_pw)
                    new_user = models.User(
                        full_name=new_name, 
                        phone_number=new_phone, 
                        hashed_password=hashed_pw, 
                        role=reg_role
                    )
                    db.add(new_user)
                    db.commit()
                    st.success("✅ Account created! Switch to 'Login' in the sidebar to enter.")

# -----------------------------------------
# SCREEN 2: THE DASHBOARDS (Logged In)
# -----------------------------------------
else:
    role_title = "Tutor" if st.session_state["role"] == "tutor" else "Student"
    st.success(f"🔒 Welcome back, {st.session_state['user_name']}! ({role_title} Dashboard)")
    
    if st.button("Log Out"):
        st.session_state["user_id"] = None
        st.session_state["role"] = None
        st.session_state["user_phone"] = None
        st.session_state["user_name"] = None
        st.rerun()

    current_user = db.query(models.User).filter(models.User.id == st.session_state["user_id"]).first()

    # ==========================================
    # TUTOR VIEW
    # ==========================================
    if st.session_state["role"] == "tutor":
        st.header("👨‍🏫 Tutor Dashboard")
        
        # --- EDIT PROFILE SECTION ---
        with st.expander("📝 Edit My Tutor Profile"):
            with st.form("profile_form"):
                st.info("Update your credentials so students can see your expertise.")
                spec = st.text_input("Specialization", value=getattr(current_user, 'specialization', "Mathematics"))
                bio = st.text_area("About Me", value=getattr(current_user, 'bio', ""))
                exp = st.text_input("Experience", value=getattr(current_user, 'experience', ""))
                
                if st.form_submit_button("Save Profile"):
                    current_user.specialization = spec
                    current_user.bio = bio
                    current_user.experience = exp
                    db.commit()
                    st.success("✅ Profile Saved Successfully!")
        
        # --- MANAGE REQUESTS SECTION ---
        st.subheader("📅 Manage All Student Requests")
        
        bookings = db.query(models.Booking).all()
        
        if len(bookings) == 0:
            st.info("No students have booked lessons yet.")
            
        for b in bookings:
            with st.container(border=True):
                st.markdown(f"### 📘 {b.subject} (Student: {b.student_phone})")
                st.write(f"**When:** {b.lesson_date} at {b.lesson_time}")
                
                if b.status == 'Pending':
                    st.warning(f"Status: {b.status}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Confirm", key=f"tutor_confirm_{b.id}"):
                            b.status = "Confirmed"
                            db.commit()
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", key=f"tutor_cancel_{b.id}"):
                            b.status = "Cancelled"
                            db.commit()
                            st.rerun()
                else:
                    st.info(f"Status: {b.status}")

    # ==========================================
    # STUDENT VIEW - BOOKING & PERSONAL SCHEDULE
    # ==========================================
    elif st.session_state["role"] == "student":
        tab1, tab2 = st.tabs(["📅 My Schedule", "➕ Book a Lesson"])

        with tab1:
            st.header("Your Upcoming Lessons")
            bookings = db.query(models.Booking).filter(models.Booking.student_phone == st.session_state["user_phone"]).all()
            
            if len(bookings) == 0:
                st.info("You have no lessons scheduled yet.")
            
            for b in bookings:
                with st.container(border=True):
                    st.markdown(f"### 📘 {b.subject}")
                    st.write(f"**When:** {b.lesson_date} at {b.lesson_time}")
                    
                    if b.status == 'Pending':
                        st.warning(f"Status: {b.status} (Waiting for Tutor)")
                    elif b.status == 'Confirmed':
                        st.success(f"Status: {b.status}")
                    else:
                        st.error(f"Status: {b.status}")

        with tab2:
            st.header("Book a New Lesson")
            
            # --- THE TUTOR SHOWCASE ---
            st.subheader("👨‍🏫 Available Tutors")
            tutors = db.query(models.User).filter(models.User.role == "tutor").all()
            
            if len(tutors) == 0:
                st.info("No tutors available at the moment.")
            else:
                for t in tutors:
                    with st.container(border=True):
                        st.markdown(f"### 🎓 {t.full_name}")
                        st.write(f"**Specialization:** {getattr(t, 'specialization', 'Not set')}")
                        st.write(f"**Experience:** {getattr(t, 'experience', 'Not set')}")
                        st.info(f"**Bio:** {getattr(t, 'bio', 'No bio provided.')}")
            
            st.divider()
            
            # --- BOOKING FORM ---
            with st.form("booking_form"):
                new_subject = st.text_input("Subject (e.g. Linear Algebra)")
                new_date = st.date_input("Lesson Date")
                new_time = st.time_input("Lesson Time")
                
                if st.form_submit_button("Submit Booking"):
                    new_booking = models.Booking(
                        subject=new_subject,
                        lesson_date=str(new_date),
                        lesson_time=str(new_time),
                        status="Pending",
                        student_phone=st.session_state["user_phone"]
                    )
                    db.add(new_booking)
                    db.commit()
                    st.success("Lesson Request Sent!")

# Close the database session at the end of the script
db.close()