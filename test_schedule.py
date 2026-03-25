import requests

# 1. LOGIN WITH ALL REQUIRED FIELDS
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

    # 2. CHECK THE SCHEDULE
    schedule_url = "http://127.0.0.1:8000/my-bookings"
    headers = {"Authorization": f"Bearer {token}"} 

    print("Fetching your schedule...")
    response = requests.get(schedule_url, headers=headers)

    if response.status_code == 200:
        print("\n--- YOUR UPCOMING LESSONS ---")
        for booking in response.json():
            print(f"Lesson: {booking['subject']}")
            print(f"When: {booking['lesson_date']} at {booking['lesson_time']}")
            print(f"Status: {booking['status']}")
            print("-" * 30)
    else:
        print(f"Failed to fetch schedule: {response.status_code}")
        print(response.text)