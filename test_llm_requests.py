import asyncio
import os
import requests
from dotenv import load_dotenv

load_dotenv("apps/modal-backend/.env")

base_url = os.environ.get("LLAMACPP_BASE_URL", "http://localhost:28081/v1")
model = os.environ.get("LLAMACPP_TEXT_MODEL", "Qwen2.5-VL-7B-Instruct-Q4_1.gguf")

print(f"Base URL: {base_url}")
print(f"Model: {model}")

payload = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You design a visual-explainer page. Return JSON with keys: page_title, prompt, facts."},
        {"role": "user", "content": "Query: how does a steam engine work"},
    ],
    "temperature": 0.7,
    "max_tokens": 900,
}

print(f"Sending request...")
try:
    response = requests.post(
        f"{base_url}/chat/completions",
        json=payload,
        timeout=300
    )
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.text[:500]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
