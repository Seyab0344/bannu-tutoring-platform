import requests

url = "http://127.0.0.1:8000/users/"
new_user = {
    "phone_number": "03111111111",   # NEW NUMBER for the student
    "full_name": "Student Seyab",
    "password": "StudentPassword123!",
    "role": "student"                # IMPORTANT: Set this to student
}

print("Registering new student...")
response = requests.post(url, json=new_user)
print(response.json())