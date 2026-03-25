import requests

# Make sure this says /login at the end!
url = "http://127.0.0.1:8000/login"

login_credentials = {
    "phone_number": "03119998888", 
    "full_name": "Tariq Khan",
    "password": "BannuTutoring2026!",
    "role": "student"
}

print("Attempting to login...")
response = requests.post(url, json=login_credentials)

if response.status_code == 200:
    print("Login Success!")
    print(response.json())
else:
    print(f"Login Failed: {response.text}")