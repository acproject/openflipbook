import base64
import requests
import json

img_path = r"d:\workspace\python_projects\openflipbook\data\images\session_9779e7f1-edda-4c92-ba19-56f7a9f94be7\6331d82c-4e10-4f32-be43-980e59f0bf5c.jpg"

with open(img_path, "rb") as f:
    img_bytes = f.read()

b64 = base64.b64encode(img_bytes).decode("ascii")
data_url = f"data:image/jpeg;base64,{b64}"

print(f"Image size: {len(img_bytes)} bytes")

# Test the animate API with short timeout to see the error quickly
print("\nTesting /animate API...")
try:
    resp = requests.post(
        "http://localhost:8787/animate",
        json={
            "image_data_url": data_url,
            "prompt": "Camera slowly pans right",
            "duration": 5,
        },
        timeout=60,
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
except requests.exceptions.Timeout:
    print("Request timed out after 60 seconds")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
