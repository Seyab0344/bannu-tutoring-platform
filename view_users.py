import requests

url = "http://127.0.0.1:8000/users/"

print("Fetching all users from Bannu Online Tutoring...")
response = requests.get(url)

if response.status_code == 200:
    users = response.json()
    print(f"Found {len(users)} users in the database:")
    for user in users:
        print(f"ID: {user['id']} | Name: {user['full_name']} | Role: {user['role']}")
else:
    print("Failed to fetch users.")