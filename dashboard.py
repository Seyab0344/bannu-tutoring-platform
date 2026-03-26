import streamlit as st
from database import SessionLocal, engine
import models
from passlib.context import CryptContext
import smtplib
from email.mime.text import MIMEText
import random
import pandas as st_pandas # Added to make beautiful tables for the Admin

# 1. Initialize Database
models.Base.metadata.create_all(bind=engine)

# 2. Email Configuration
SENDER_EMAIL = "seyabkhan158@gmail.com"
# Make sure your 16-letter App Password is still here!
APP_PASSWORD = "your_sixteen_letter_code_here" 

def send_verification_email(receiver_email, otp_code):
    try:
        msg = MIMEText(f"Welcome to Bannu Tutoring!\n\nYour 6-digit verification code is: {otp_code}\n\nPlease enter this code on the website to complete your registration.")
        msg['Subject'] = 'Your Bannu Tutoring Security Code'
        msg['From'] = f"Bannu Tutoring <{SENDER_EMAIL}>"
        msg['To'] = receiver_email

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# 3. Setup Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

st.set_page_config(page_title="Bannu Tutoring", page_icon="📚", layout="centered")

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
    st.session_state["role"] = None
    st.session_state["user_phone"] = None
    st.session_state["user_name"] = None
    st.session_state["signup_step"] = 1 
    st.session_state["temp_reg_data"] = {} 
    st.session_state["real_otp"] = None 

db = SessionLocal()

# -----------------------------------------
# CUSTOM UI STYLING 
# -----------------------------------------
st.markdown("""
<style>
    div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
        background-color: #14a800 !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: bold !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button[kind="primary"]:hover { background-color: #108a00 !important; }
    div.stButton > button[kind="secondary"] { border-radius: 8px !important; border: 1px solid #d5e0d5 !important; font-weight: 500 !important; }
    .or-divider { display: flex; align-items: center; text-align: center; color: #656565; font-size: 14px; margin: 20px 0px; }
    .or-divider::before, .or-divider::after { content: ''; flex: 1; border-bottom: 1px solid #e4ebe4; }
    .or-divider::before { margin-right: 15px; } .or-divider::after { margin-left: 15px; }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------
# SCREEN 1: THE LOGIN / REGISTER PAGE
# -----------------------------------------
if st.session_state["user_id"] is None:
    
    choice = st.sidebar.selectbox("Action", ["Login", "Sign Up"])
    left_spacer, center_col, right_spacer = st.columns([1, 1.5, 1])
    
    with center_col:
        st.markdown("<h2 style='text-align: center; color: #001e00;'>📚 Bannu Tutoring</h2>", unsafe_allow_html=True)
        st.write("")
        
        # --- LOGIN FLOW ---
        if choice == "Login":
            st.markdown("<h4 style='text-align: center;'>Log in to your account</h4>", unsafe_allow_html=True)
            login_role = st.radio("I am a:", ["student", "tutor"], horizontal=True)
            
            with st.form("login_form", clear_on_submit=False):
                email_input = st.text_input("Email", label_visibility="collapsed", placeholder="📧 Email Address")
                password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="🔒 Password")
                submitted = st.form_submit_button("Continue", type="primary", use_container_width=True)
                
                if submitted:
                    user = db.query(models.User).filter(
                        models.User.phone_number == email_input.lower(),
                        models.User.role == login_role
                    ).first()
                    
                    if user and pwd_context.verify(password, user.hashed_password):
                        st.session_state["user_id"] = user.id
                        st.session_state["role"] = user.role
                        st.session_state["user_phone"] = user.phone_number
                        st.session_state["user_name"] = user.full_name
                        st.session_state["signup_step"] = 1
                        st.session_state["temp_reg_data"] = {}
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please check your email/password or role.")
            
            st.markdown("<div class='or-divider'>or</div>", unsafe_allow_html=True)
            st.button("🔵 Continue with Google", use_container_width=True)
            st.button("🍎 Continue with Apple", use_container_width=True)

        # --- REGISTRATION FLOW ---
        else:
            st.markdown("<h4 style='text-align: center;'>Create an Account</h4>", unsafe_allow_html=True)
            
            if st.session_state["signup_step"] == 1:
                reg_role = st.radio("Register as:", ["student", "tutor"], horizontal=True)
                
                with st.form("reg_form"):
                    new_name = st.text_input("Full Name", label_visibility="collapsed", placeholder="👤 Full Name")
                    new_email = st.text_input("Email", label_visibility="collapsed", placeholder="📧 Email Address")
                    new_pw = st.text_input("Set Password", type="password", label_visibility="collapsed", placeholder="🔒 Set Password")
                    
                    if st.form_submit_button("Send Verification Code", type="primary", use_container_width=True):
                        new_email = new_email.lower().strip()
                        existing_user = db.query(models.User).filter(models.User.phone_number == new_email).first()
                        
                        if existing_user:
                            st.error("Registration failed. That email is already registered.")
                        elif "@" not in new_email or "." not in new_email:
                            st.error("Please enter a valid email address.")
                        elif not new_name or len(new_pw) < 4:
                            st.error("Please fill in all fields (password must be 4+ chars).")
                        else:
                            generated_otp = str(random.randint(100000, 999999))
                            
                            with st.spinner("Sending email..."):
                                success = send_verification_email(new_email, generated_otp)
                            
                            if success:
                                st.session_state["real_otp"] = generated_otp
                                st.session_state["temp_reg_data"] = {
                                    "name": new_name,
                                    "phone": new_email,
                                    "pw": new_pw,
                                    "role": reg_role
                                }
                                st.session_state["signup_step"] = 2
                                st.rerun()
                            else:
                                st.error("Failed to send email. Check your App Password configuration.")

            elif st.session_state["signup_step"] == 2:
                st.info(f"📧 We have sent a code to **{st.session_state['temp_reg_data']['phone']}**")
                
                with st.form("otp_form"):
                    entered_otp = st.text_input("Enter 6-Digit Security Code", max_chars=6)
                    
                    if st.form_submit_button("Verify & Create Account", type="primary", use_container_width=True):
                        if entered_otp == st.session_state["real_otp"]:
                            hashed_pw = pwd_context.hash(st.session_state["temp_reg_data"]["pw"])
                            new_user = models.User(
                                full_name=st.session_state["temp_reg_data"]["name"], 
                                phone_number=st.session_state["temp_reg_data"]["phone"], 
                                hashed_password=hashed_pw, 
                                role=st.session_state["temp_reg_data"]["role"]
                            )
                            db.add(new_user)
                            db.commit()
                            
                            st.session_state["signup_step"] = 1
                            st.session_state["temp_reg_data"] = {}
                            st.session_state["real_otp"] = None
                            st.success("✅ Account created! Switch to 'Login' in the sidebar to enter.")
                        else:
                            st.error("❌ Incorrect code. Please try again.")
                
                if st.button("← Back to edit details"):
                    st.session_state["signup_step"] = 1
                    st.rerun()

# -----------------------------------------
# SCREEN 2: THE DASHBOARDS (Logged In)
# -----------------------------------------
else:
    # Check if the logged-in user is the Admin
    is_admin = (st.session_state["user_phone"] == "seyabkhan158@gmail.com")
    
    if is_admin:
        role_title = "Platform Admin"
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
            st.session_state.clear()
            st.session_state["user_id"] = None
            st.rerun()

    current_user = db.query(models.User).filter(models.User.id == st.session_state["user_id"]).first()

    # ==========================================
    # 👑 ADMIN VIEW (Only visible to you)
    # ==========================================
    if is_admin:
        st.header("👑 Platform Master Control")
        st.info("You are viewing the secret Admin Dashboard.")
        
        tab_users, tab_bookings = st.tabs(["👥 All Users", "💸 All Bookings & Payments"])
        
        with tab_users:
            all_users = db.query(models.User).all()
            if all_users:
                # Convert database data into a nice table
                user_data = [{"ID": u.id, "Name": u.full_name, "Email": u.phone_number, "Role": u.role} for u in all_users]
                st.dataframe(user_data, use_container_width=True)
            else:
                st.write("No users registered yet.")
                
        with tab_bookings:
            all_bookings = db.query(models.Booking).all()
            if all_bookings:
                booking_data = [{"ID": b.id, "Student Email": b.student_phone, "Subject": b.subject, "Date": b.lesson_date, "Time": b.lesson_time, "Status": b.status, "TID": b.tid} for b in all_bookings]
                st.dataframe(booking_data, use_container_width=True)
            else:
                st.write("No bookings made yet.")

    # ==========================================
    # TUTOR VIEW (If you are not the admin)
    # ==========================================
    elif st.session_state["role"] == "tutor":
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
                st.markdown(f"### 📘 {b.subject} (Student Email: {b.student_phone})")
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

db.close()