import requests

# We are looking at the dashboard for Tutor #1
tutor_id = 1
url = f"http://127.0.0.1:8000/tutors/{tutor_id}/bookings/"

print(f"Loading Dashboard for Tutor ID: {tutor_id}...")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("--- UPCOMING SESSIONS ---")
    sessions = data.get("upcoming_sessions", [])
    for s in sessions:
        print(f"Booking ID: {s['id']} | Student ID: {s['student_id']} | Time: {s['scheduled_time']} | Status: {s['status']}")
else:
    print(f"Could not load dashboard: {response.text}")