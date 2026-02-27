import requests
import json

url = "http://127.0.0.1:8000/api/v1/analyze"
data = {"url": "https://www.google.com"}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
