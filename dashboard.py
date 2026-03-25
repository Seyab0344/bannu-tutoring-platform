import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Bannu Tutoring", page_icon="📚")
st.title("📚 Bannu Online Tutoring Platform")

# Initialize session state for security tokens and user roles
if "token" not in st.session_state:
    st.session_state["token"] = None
    st.session_state["role"] = None

# -----------------------------------------
# SCREEN 1: THE LOGIN / REGISTER PAGE
# -----------------------------------------
if st.session_state["token"] is None:
    # Sidebar navigation for switching between Login and Sign Up
    choice = st.sidebar.selectbox("Action", ["Login", "Sign Up"])
    
    if choice == "Login":
        st.subheader("🔑 Secure Login")
        login_role = st.radio("I am a:", ["student", "tutor"], horizontal=True)
        
        with st.form("login_form"):
            phone = st.text_input("Phone Number")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                creds = {
                    "phone_number": phone, 
                    "full_name": "User", 
                    "password": password, 
                    "role": login_role
                }
                # Fix: Using 'response' consistently so the handshake works
                response = requests.post(f"{BASE_URL}/login", json=creds)
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["role"] = data["role"]
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please check your phone/password.")
    
    else:
        st.subheader("📝 Create New Account")
        reg_role = st.radio("Register as:", ["student", "tutor"], horizontal=True)
        with st.form("reg_form"):
            new_name = st.text_input("Full Name")
            new_phone = st.text_input("Phone Number")
            new_pw = st.text_input("Set Password", type="password")
            
            if st.form_submit_button("Register"):
                reg_data = {
                    "phone_number": new_phone, 
                    "full_name": new_name, 
                    "password": new_pw, 
                    "role": reg_role
                }
                response = requests.post(f"{BASE_URL}/users/", json=reg_data)
                if response.status_code == 200:
                    st.success("✅ Account created! Switch to 'Login' in the sidebar to enter.")
                else:
                    st.error(f"Registration failed. That phone number might already be taken.")

# -----------------------------------------
# SCREEN 2: THE DASHBOARDS (Logged In)
# -----------------------------------------
else:
    role_title = "Tutor" if st.session_state["role"] == "tutor" else "Student"
    st.success(f"🔒 Welcome to the {role_title} Dashboard!")
    
    if st.button("Log Out"):
        st.session_state["token"] = None
        st.session_state["role"] = None
        st.rerun()

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    # ==========================================
    # TUTOR VIEW
    # ==========================================
    if st.session_state["role"] == "tutor":
        st.header("👨‍🏫 Tutor Dashboard")
        
        # --- NEW: EDIT PROFILE SECTION ---
        with st.expander("📝 Edit My Tutor Profile"):
            with st.form("profile_form"):
                st.info("Update your credentials so students can see your expertise.")
                # I've pre-filled some defaults for you!
                spec = st.text_input("Specialization", value="Mathematics (General Relativity)")
                bio = st.text_area("About Me", value="M.Phil in Mathematics from Quaid-I-Azam University, Islamabad.")
                exp = st.text_input("Experience", value="e.g., 5 years teaching A-Levels")
                
                if st.form_submit_button("Save Profile"):
                    p_data = {
                        "specialization": spec,
                        "bio": bio,
                        "experience": exp
                    }
                    p_resp = requests.put(f"{BASE_URL}/update-profile", json=p_data, headers=headers)
                    if p_resp.status_code == 200:
                        st.success("✅ Profile Saved Successfully!")
                    else:
                        st.error("❌ Failed to save profile.")
        
        # --- EXISTING: MANAGE REQUESTS SECTION ---
        st.subheader("📅 Manage All Student Requests")
        
        schedule_resp = requests.get(f"{BASE_URL}/all-bookings", headers=headers)
        if schedule_resp.status_code == 200:
            bookings = schedule_resp.json()
            if len(bookings) == 0:
                st.info("No students have booked lessons yet.")
            
            for b in bookings:
                with st.container(border=True):
                    st.markdown(f"### 📘 {b['subject']} (Student: {b['student_phone']})")
                    st.write(f"**When:** {b['lesson_date']} at {b['lesson_time']}")
                    
                    if b['status'] == 'Pending':
                        st.warning(f"Status: {b['status']}")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Confirm", key=f"tutor_confirm_{b['id']}"):
                                requests.put(f"{BASE_URL}/bookings/{b['id']}/status", json={"status": "Confirmed"}, headers=headers)
                                st.rerun()
                        with col2:
                            if st.button("❌ Cancel", key=f"tutor_cancel_{b['id']}"):
                                requests.put(f"{BASE_URL}/bookings/{b['id']}/status", json={"status": "Cancelled"}, headers=headers)
                                st.rerun()
                    else:
                        st.info(f"Status: {b['status']}")

    # ==========================================
    # STUDENT VIEW - BOOKING & PERSONAL SCHEDULE
    # ==========================================
    elif st.session_state["role"] == "student":
        tab1, tab2 = st.tabs(["📅 My Schedule", "➕ Book a Lesson"])

        with tab1:
            st.header("Your Upcoming Lessons")
            schedule_resp = requests.get(f"{BASE_URL}/my-bookings", headers=headers)
            if schedule_resp.status_code == 200:
                bookings = schedule_resp.json()
                if len(bookings) == 0:
                    st.info("You have no lessons scheduled yet.")
                
                for b in bookings:
                    with st.container(border=True):
                        st.markdown(f"### 📘 {b['subject']}")
                        st.write(f"**When:** {b['lesson_date']} at {b['lesson_time']}")
                        
                        if b['status'] == 'Pending':
                            st.warning(f"Status: {b['status']} (Waiting for Tutor)")
                        elif b['status'] == 'Confirmed':
                            st.success(f"Status: {b['status']}")
                        else:
                            st.error(f"Status: {b['status']}")

        with tab2:
            st.header("Book a New Lesson")
            
            # --- NEW: THE TUTOR SHOWCASE ---
            st.subheader("👨‍🏫 Available Tutors")
            tutors_resp = requests.get(f"{BASE_URL}/tutors", headers=headers)
            
            if tutors_resp.status_code == 200:
                tutors = tutors_resp.json()
                if len(tutors) == 0:
                    st.info("No tutors available at the moment.")
                else:
                    for t in tutors:
                        with st.container(border=True):
                            st.markdown(f"### 🎓 {t['full_name']}")
                            # We use .get() here just in case a tutor hasn't filled out their profile yet
                            st.write(f"**Specialization:** {t.get('specialization') or 'Not set'}")
                            st.write(f"**Experience:** {t.get('experience') or 'Not set'}")
                            st.info(f"**Bio:** {t.get('bio') or 'No bio provided.'}")
            
            st.divider() # Adds a nice visual line
            
            # --- EXISTING BOOKING FORM ---
            with st.form("booking_form"):
                new_subject = st.text_input("Subject (e.g. Linear Algebra)")
                new_date = st.date_input("Lesson Date")
                new_time = st.time_input("Lesson Time")
                if st.form_submit_button("Submit Booking"):
                    booking_data = {
                        "subject": new_subject, 
                        "lesson_date": str(new_date), 
                        "lesson_time": str(new_time)
                    }
                    book_resp = requests.post(f"{BASE_URL}/book-lesson", json=booking_data, headers=headers)
                    if book_resp.status_code == 200:
                        st.success("Lesson Request Sent!")
                    else:
                        st.error("Failed to book lesson.")