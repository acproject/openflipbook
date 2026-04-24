import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv("apps/modal-backend/.env")

async def test_llm_long_timeout():
    base_url = os.environ.get("LLAMACPP_BASE_URL", "http://localhost:28081/v1")
    model = os.environ.get("LLAMACPP_TEXT_MODEL", "Qwen2.5-VL-7B-Instruct-Q4_1.gguf")
    
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    
    # 5分钟超时
    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0)) as client:
        try:
            print("Sending request...")
            response = await client.post(
                f"{base_url}/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You design a visual-explainer page. Return JSON with keys: page_title, prompt, facts."},
                        {"role": "user", "content": "Query: how does a steam engine work"},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 900,
                },
            )
            print(f"Status: {response.status_code}")
            print(f"Body: {response.text[:500]}")
        except httpx.ReadTimeout as e:
            print(f"ReadTimeout: {e}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

asyncio.run(test_llm_long_timeout())
