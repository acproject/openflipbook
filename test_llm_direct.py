import asyncio
import os
from dotenv import load_dotenv

load_dotenv("apps/modal-backend/.env")

async def test_llm():
    from openai import AsyncOpenAI
    
    base_url = os.environ.get("LLAMACPP_BASE_URL", "http://localhost:28081/v1")
    model = os.environ.get("LLAMACPP_TEXT_MODEL", "qwen2.5-7b")
    
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    
    client = AsyncOpenAI(
        api_key="not-needed",
        base_url=base_url,
    )
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Say hello in one sentence."},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=100,
        )
        print(f"Success: {response.choices[0].message.content}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

asyncio.run(test_llm())
