import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv("apps/modal-backend/.env")

async def test_llm_verbose():
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
    
    print(f"Payload: {payload}")
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0)) as client:
        try:
            # 构建请求但不发送，查看详细信息
            request = client.build_request("POST", f"{base_url}/chat/completions", json=payload)
            print(f"Request URL: {request.url}")
            print(f"Request headers: {dict(request.headers)}")
            print(f"Request body: {request.content.decode()[:500]}")
            
            print("\nSending request...")
            response = await client.send(request)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Body: {response.text[:500]}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test_llm_verbose())
