import json

# Read the JSON file
with open("test.json", "r") as file:
    data = json.load(file)

# Print each field individually
print("Access Token:", data.get("access_token", "Not Found"))
print("Email:", data.get("email", "Not Found"))
print("Password:", data.get("password", "Not Found"))
print("Interface:", data.get("interface", "Not Found"))
