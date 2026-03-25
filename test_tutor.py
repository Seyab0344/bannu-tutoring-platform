import requests

url = "http://127.0.0.1:8000/tutors/"

# We are linking this to ID 1 (Seyab Khan)
tutor_data = {
    "user_id": 1,
    "subjects": "Calculus, General Relativity, Linear Algebra",
    "grade_levels": "BS, MSc",
    "hourly_rate": 1500.0
}

print("Registering as a Tutor...")
response = requests.post(url, json=tutor_data)

if response.status_code == 200:
    print("Success! Tutor profile is live:")
    print(response.json())
else:
    print(f"Error: {response.text}")