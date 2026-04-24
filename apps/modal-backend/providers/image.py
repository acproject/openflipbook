"""Local image generation — supports ComfyUI or AUTOMATIC1111 WebUI.

Point LOCAL_IMAGE_API_URL to your image generation server:
- ComfyUI: http://localhost:8188 (uses /prompt API)
- AUTOMATIC1111: http://localhost:7860 (uses /sdapi/v1/txt2img)

Default: AUTOMATIC1111-compatible API.
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass

import httpx

LOCAL_IMAGE_API_URL = os.environ.get("LOCAL_IMAGE_API_URL", "http://localhost:8188")
DEFAULT_IMAGE_MODEL = os.environ.get("LOCAL_IMAGE_MODEL", "automatic1111")


@dataclass
class GeneratedImage:
    jpeg_bytes: bytes
    mime_type: str
    model: str
    provider_request_id: str | None


def _aspect_ratio_to_dimensions(aspect_ratio: str) -> tuple[int, int]:
    ratios = {
        "16:9": (1024, 576),
        "9:16": (576, 1024),
        "1:1": (768, 768),
        "4:3": (896, 672),
        "3:4": (672, 896),
    }
    return ratios.get(aspect_ratio, (1024, 576))


async def generate_image(prompt: str, aspect_ratio: str) -> GeneratedImage:
    width, height = _aspect_ratio_to_dimensions(aspect_ratio)
    
    api_type = os.environ.get("LOCAL_IMAGE_API_TYPE", "automatic1111")
    
    if api_type == "comfyui":
        return await _generate_comfyui(prompt, width, height)
    else:
        return await _generate_automatic1111(prompt, width, height)


async def _generate_automatic1111(prompt: str, width: int, height: int) -> GeneratedImage:
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{LOCAL_IMAGE_API_URL}/sdapi/v1/txt2img",
            json={
                "prompt": prompt,
                "negative_prompt": "text, watermark, blurry, low quality",
                "width": width,
                "height": height,
                "steps": int(os.environ.get("IMAGE_STEPS", "30")),
                "cfg_scale": float(os.environ.get("IMAGE_CFG", "7.0")),
            },
        )
        resp.raise_for_status()
        result = resp.json()
        
        if not result.get("images"):
            raise RuntimeError("Image generation returned no images")
        
        b64_image = result["images"][0]
        jpeg_bytes = base64.b64decode(b64_image)
        
        return GeneratedImage(
            jpeg_bytes=jpeg_bytes,
            mime_type="image/jpeg",
            model=DEFAULT_IMAGE_MODEL,
            provider_request_id=None,
        )


async def _generate_comfyui(prompt: str, width: int, height: int) -> GeneratedImage:
    import json
    import uuid
    import time
    import asyncio
    import requests
    
    model_name = os.environ.get("COMFYUI_MODEL", "05Xxmix9realisticV4005_v10.safetensors")
    
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": float(os.environ.get("IMAGE_CFG", "7.0")),
                "denoise": 1.0,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler",
                "scheduler": "normal",
                "seed": int(os.environ.get("IMAGE_SEED", "42")),
                "steps": int(os.environ.get("IMAGE_STEPS", "30")),
            },
        },
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": model_name}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": height, "width": width}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": prompt}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "text, watermark, blurry, low quality, deformed"}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "openflipbook", "images": ["8", 0]}},
    }
    
    client_id = str(uuid.uuid4())
    
    def post_prompt():
        return requests.post(
            f"{LOCAL_IMAGE_API_URL}/prompt",
            json={"prompt": workflow, "client_id": client_id},
            timeout=30,
        )
    
    resp = await asyncio.to_thread(post_prompt)
    resp.raise_for_status()
    prompt_data = resp.json()
    prompt_id = prompt_data.get("prompt_id")
    
    if not prompt_id:
        raise RuntimeError(f"ComfyUI did not return prompt_id: {prompt_data}")
    
    def get_history():
        return requests.get(f"{LOCAL_IMAGE_API_URL}/history/{prompt_id}", timeout=10)
    
    def get_view(filename, subfolder, type_):
        return requests.get(
            f"{LOCAL_IMAGE_API_URL}/view",
            params={"filename": filename, "subfolder": subfolder, "type": type_},
            timeout=30,
        )
    
    for _ in range(180):
        history_resp = await asyncio.to_thread(get_history)
        if history_resp.status_code == 200:
            history = history_resp.json()
            if prompt_id in history:
                node_output = history[prompt_id].get("outputs", {}).get("9", {})
                images = node_output.get("images", [])
                if images:
                    output = images[0]
                    img_resp = await asyncio.to_thread(
                        get_view,
                        output["filename"],
                        output.get("subfolder", ""),
                        output.get("type", "output"),
                    )
                    img_resp.raise_for_status()
                    return GeneratedImage(
                        jpeg_bytes=img_resp.content,
                        mime_type="image/jpeg",
                        model=model_name,
                        provider_request_id=prompt_id,
                    )
        await asyncio.sleep(1)
    
    raise RuntimeError("ComfyUI image generation timed out")


def encode_data_url(jpeg_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    b64 = base64.b64encode(jpeg_bytes).decode("ascii")
    return f"data:{mime_type};base64,{b64}"
