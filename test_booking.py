import requests

# 1. LOGIN WITH THE NEW PERFECT ACCOUNT
login_url = "http://127.0.0.1:8000/login"
user_creds = {
    "phone_number": "03444444444",       
    "full_name": "Seyab Khan Master",           
    "password": "SecurePassword123!", 
    "role": "tutor"
}

print("Logging in to get security token...")
login_resp = requests.post(login_url, json=user_creds)

if login_resp.status_code != 200 or "access_token" not in login_resp.json():
    print("Login Failed! The server said:")
    print(login_resp.json())
else:
    token = login_resp.json()["access_token"]
    print("Login Success! Token received.")

    # 2. BOOK THE LESSON
    booking_url = "http://127.0.0.1:8000/book-lesson"
    headers = {"Authorization": f"Bearer {token}"} 

    lesson_details = {
        "subject": "General Relativity - M.Phil Level",
        "lesson_date": "2026-03-30",
        "lesson_time": "02:00 PM"
    }

    print("Attempting to book a lesson...")
    response = requests.post(booking_url, json=lesson_details, headers=headers)

    print("\n--- SERVER RESPONSE ---")
    print(response.json())