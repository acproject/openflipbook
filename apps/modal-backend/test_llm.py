import asyncio
import httpx

async def test_llamacpp():
    print("Testing llama.cpp chat completion...")
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "http://127.0.0.1:28081/v1/chat/completions",
            json={
                "model": "Qwen2.5-VL-7B-Instruct-Q4_1.gguf",
                "messages": [{"role": "user", "content": "Say hello in one sentence"}],
                "max_tokens": 50
            }
        )
        print(f"Status: {resp.status_code}")
        result = resp.json()
        print(f"Response: {result.get('choices', [{}])[0].get('message', {})}")

asyncio.run(test_llamacpp())
