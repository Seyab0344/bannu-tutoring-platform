import streamlit as st
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# 1. Initialize Database
models.Base.metadata.create_all(bind=engine)

# 2. Setup Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

st.set_page_config(page_title="Bannu Tutoring", page_icon="📚", layout="centered")

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
    st.session_state["role"] = None
    st.session_state["user_phone"] = None
    st.session_state["user_name"] = None

# Open database session for this page load
db = SessionLocal()

# -----------------------------------------
# CUSTOM UI STYLING (The Upwork Look)
# -----------------------------------------
st.markdown("""
<style>
    /* Make the primary button Upwork Green */
    div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
        background-color: #14a800 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button[kind="primary"]:hover {
        background-color: #108a00 !important;
    }
    /* Style secondary buttons (Google/Apple/Sign Up) */
    div.stButton > button[kind="secondary"] {
        border-radius: 8px !important;
        border: 1px solid #d5e0d5 !important;
        font-weight: 500 !important;
    }
    /* The 'or' divider line */
    .or-divider {
        display: flex;
        align-items: center;
        text-align: center;
        color: #656565;
        font-size: 14px;
        margin: 20px 0px;
    }
    .or-divider::before, .or-divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #e4ebe4;
    }
    .or-divider::before { margin-right: 15px; }
    .or-divider::after { margin-left: 15px; }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------
# SCREEN 1: THE LOGIN / REGISTER PAGE
# -----------------------------------------
if st.session_state["user_id"] is None:
    
    choice = st.sidebar.selectbox("Action", ["Login", "Sign Up"])
    
    # Use columns to push the form to the center of the screen
    left_spacer, center_col, right_spacer = st.columns([1, 1.5, 1])
    
    with center_col:
        st.markdown("<h2 style='text-align: center; color: #001e00;'>📚 Bannu Tutoring</h2>", unsafe_allow_html=True)
        st.write("")
        
        if choice == "Login":
            st.markdown("<h4 style='text-align: center;'>Log in to your account</h4>", unsafe_allow_html=True)
            login_role = st.radio("I am a:", ["student", "tutor"], horizontal=True)
            
            with st.form("login_form", clear_on_submit=False):
                phone = st.text_input("Username", label_visibility="collapsed", placeholder="👤 Phone Number")
                password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="🔒 Password")
                
                submitted = st.form_submit_button("Continue", type="primary", use_container_width=True)
                
                if submitted:
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
            
            st.markdown("<div class='or-divider'>or</div>", unsafe_allow_html=True)
            st.button("🔵 Continue with Google", use_container_width=True)
            st.button("🍎 Continue with Apple", use_container_width=True)
            st.markdown("<p style='text-align: center; color: #656565; margin-top: 15px;'>Use the sidebar to Sign Up</p>", unsafe_allow_html=True)

        else:
            st.markdown("<h4 style='text-align: center;'>Create an Account</h4>", unsafe_allow_html=True)
            reg_role = st.radio("Register as:", ["student", "tutor"], horizontal=True)
            
            with st.form("reg_form"):
                new_name = st.text_input("Full Name", label_visibility="collapsed", placeholder="👤 Full Name")
                new_phone = st.text_input("Phone Number", label_visibility="collapsed", placeholder="📱 Phone Number")
                new_pw = st.text_input("Set Password", type="password", label_visibility="collapsed", placeholder="🔒 Set Password")
                
                if st.form_submit_button("Sign Up", type="primary", use_container_width=True):
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
    
    with st.sidebar:
        st.markdown("### 📞 Help & Payments")
        st.write("For payment issues or help:")
        st.success("EasyPaisa: 0336-9972158")
        st.warning("JazzCash: 0336-9972158")
        st.divider()
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
        
        st.subheader("📅 Manage All Student Requests")
        
        bookings = db.query(models.Booking).all()
        
        if len(bookings) == 0:
            st.info("No students have booked lessons yet.")
            
        for b in bookings:
            with st.container(border=True):
                st.markdown(f"### 📘 {b.subject} (Student: {b.student_phone})")
                st.write(f"**When:** {b.lesson_date} at {b.lesson_time}")
                st.info(f"💰 **EasyPaisa TID:** `{getattr(b, 'tid', 'No TID provided')}`")
                
                if b.status == 'Pending':
                    st.warning(f"Status: {b.status} (Awaiting Payment Verification)")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Verify & Confirm", key=f"tutor_confirm_{b.id}"):
                            b.status = "Confirmed"
                            db.commit()
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", key=f"tutor_cancel_{b.id}"):
                            b.status = "Cancelled"
                            db.commit()
                            st.rerun()
                else:
                    st.success(f"Status: {b.status}")

    # ==========================================
    # STUDENT VIEW
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
                        st.warning(f"Status: {b.status} (Waiting for Tutor to verify payment)")
                    elif b.status == 'Confirmed':
                        st.success(f"Status: {b.status}")
                    else:
                        st.error(f"Status: {b.status}")

        with tab2:
            st.header("Book a New Lesson")
            
            st.subheader("👨‍🏫 Find a Tutor")
            search_term = st.text_input("🔍 Search by subject, name, or specialization:", "")
            
            if search_term:
                search_pattern = f"%{search_term}%"
                tutors = db.query(models.User).filter(
                    models.User.role == "tutor",
                    (models.User.full_name.ilike(search_pattern)) | 
                    (models.User.specialization.ilike(search_pattern))
                ).all()
            else:
                tutors = db.query(models.User).filter(models.User.role == "tutor").all()
            
            if len(tutors) == 0:
                st.info("No tutors found matching your search.")
            else:
                for t in tutors:
                    with st.container(border=True):
                        st.markdown(f"### 🎓 {t.full_name}")
                        st.write(f"**Specialization:** {getattr(t, 'specialization', 'Not set')}")
                        st.write(f"**Experience:** {getattr(t, 'experience', 'Not set')}")
                        st.caption(f"**Bio:** {getattr(t, 'bio', 'No bio provided.')}")
            
            st.divider()
            
            # --- FIXED INDENTATION: BOOKING FORM ---
            st.subheader("📝 Request Lesson & Pay")
            with st.form("booking_form"):
                new_subject = st.text_input("Subject (e.g. M.Phil Mathematics)")
                new_date = st.date_input("Lesson Date")
                new_time = st.time_input("Lesson Time")
                
                st.markdown("---")
                st.markdown("### 💳 Payment Instructions")
                st.info("""
                **1. Send Fee:** Rs. 1000 per lesson  
                **2. EasyPaisa / JazzCash:** `0336-9972158`  
                **3. Account Name:** Seyab Khan  
                
                *Please send the payment first, then enter the Transaction ID below to complete your booking.*
                """)
                
                transaction_id = st.text_input("Enter Transaction ID (TID)")
                
                if st.form_submit_button("Submit Booking & Payment", type="primary"):
                    if not transaction_id or len(transaction_id) < 5:
                        st.error("❌ Please enter a valid Transaction ID to complete your booking.")
                    elif not new_subject:
                        st.error("❌ Please enter a subject.")
                    else:
                        try:
                            new_booking = models.Booking(
                                subject=new_subject,
                                lesson_date=str(new_date),
                                lesson_time=str(new_time),
                                status="Pending",
                                student_phone=st.session_state["user_phone"],
                                tid=transaction_id
                            )
                            db.add(new_booking)
                            db.commit()
                            st.success("✅ Booking Sent! I will confirm your lesson once the payment is verified.")
                        except Exception as e:
                            st.error("⚠️ Database Error. Please contact support.")
                            db.rollback()

# Close the database session at the end of the script
db.close()