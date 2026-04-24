"""Test script to verify the full pipeline: LLM + Image Generation"""

import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv(".env")

async def test_llm():
    print("Testing LLM connection to llama.cpp...")
    from providers import llm
    
    try:
        plan = await llm.plan_page("how does a steam engine work", web_search=False)
        print(f"  Page Title: {plan.page_title}")
        print(f"  Prompt: {plan.prompt[:100]}...")
        print(f"  Facts: {plan.facts}")
        print("  LLM test PASSED!")
        return plan
    except Exception as e:
        print(f"  LLM test FAILED: {e}")
        return None

async def test_image_generation(prompt: str):
    print("\nTesting image generation with ComfyUI...")
    from providers import image as image_provider
    
    try:
        result = await image_provider.generate_image(prompt, aspect_ratio="16:9")
        print(f"  Model: {result.model}")
        print(f"  Image size: {len(result.jpeg_bytes)} bytes")
        print(f"  MIME type: {result.mime_type}")
        print("  Image generation test PASSED!")
        return result
    except Exception as e:
        print(f"  Image generation test FAILED: {e}")
        return None

async def main():
    print("=" * 60)
    print("Endless Canvas - Local Pipeline Test")
    print("=" * 60)
    print(f"LLAMACPP_BASE_URL: {os.environ.get('LLAMACPP_BASE_URL')}")
    print(f"LOCAL_IMAGE_API_URL: {os.environ.get('LOCAL_IMAGE_API_URL')}")
    print(f"LOCAL_IMAGE_API_TYPE: {os.environ.get('LOCAL_IMAGE_API_TYPE')}")
    print("=" * 60)
    print()
    
    plan = await test_llm()
    
    if plan:
        result = await test_image_generation(plan.prompt)
        
        if result:
            print("\n" + "=" * 60)
            print("All tests PASSED! The pipeline is working correctly.")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("LLM works, but image generation failed.")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("LLM test failed. Please check llama.cpp connection.")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
