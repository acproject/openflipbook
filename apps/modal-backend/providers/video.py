"""Video animation provider.

Supports:
- **ComfyUI (local):** Uses LTXV or Wan image-to-video nodes
- **fal.ai (cloud):** Fallback when FAL_KEY is set
"""

from __future__ import annotations

import base64
import os
import json
import uuid
import asyncio
import re
import requests
from dataclasses import dataclass

DEFAULT_ANIMATE_MODEL = "fal-ai/ltx-video/image-to-video"
PRO_ANIMATE_MODEL = "fal-ai/ltx-2/image-to-video"
LOCAL_IMAGE_API_URL = os.environ.get("LOCAL_IMAGE_API_URL", "http://localhost:8188")


@dataclass
class AnimatedClip:
    video_url: str
    content_type: str
    model: str
    duration_seconds: float


def _animate_model() -> str:
    override = os.environ.get("FAL_ANIMATE_MODEL", "").strip()
    if override:
        return override
    if os.environ.get("USE_LTX_PRO", "").lower() in ("1", "true", "yes"):
        return PRO_ANIMATE_MODEL
    return DEFAULT_ANIMATE_MODEL


async def animate_image(
    *,
    image_data_url: str,
    prompt: str,
    duration: int = 5,
) -> AnimatedClip:
    if LOCAL_IMAGE_API_URL and not os.environ.get("FAL_KEY"):
        return await _animate_comfyui(image_data_url, prompt, duration)
    
    if not os.environ.get("FAL_KEY"):
        raise RuntimeError("FAL_KEY is not set and no local image service available")

    model = _animate_model()
    import fal_client
    arguments: dict = {
        "image_url": image_data_url,
        "prompt": prompt,
    }
    if model == PRO_ANIMATE_MODEL:
        arguments["duration"] = duration
        arguments["resolution"] = os.environ.get("LTX_PRO_RESOLUTION", "1080p")

    result = await fal_client.subscribe_async(model, arguments=arguments, with_logs=False)

    video = result.get("video")
    if not isinstance(video, dict):
        raise RuntimeError("fal animate returned no video payload")
    url = video.get("url")
    if not isinstance(url, str) or not url:
        raise RuntimeError("fal animate returned video without url")
    content_type = str(video.get("content_type") or "video/mp4")
    duration_s = float(video.get("duration") or duration or 5)

    return AnimatedClip(
        video_url=url,
        content_type=content_type,
        model=model,
        duration_seconds=duration_s,
    )


async def _animate_comfyui(
    image_data_url: str,
    prompt: str,
    duration: int = 5,
) -> AnimatedClip:
    import base64
    import re
    
    mime, image_bytes = _parse_data_url(image_data_url)
    
    def upload_image():
        files = {"image": ("input.png", image_bytes, "image/png")}
        return requests.post(
            f"{LOCAL_IMAGE_API_URL}/upload/image",
            files=files,
            timeout=30,
        )
    
    resp = await asyncio.to_thread(upload_image)
    if resp.status_code != 200:
        raise RuntimeError(f"ComfyUI upload failed: {resp.status_code} {resp.text}")
    
    image_name = resp.json().get("name", "input.png")
    
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": os.environ.get("COMFYUI_VIDEO_MODEL", "ltx-video-2b-v0.9.safetensors"),
            },
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "umt5_xxl_fp16.safetensors",
                "type": "stable_diffusion",
            },
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["2", 0],
            },
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "blurry, low quality, deformed",
                "clip": ["2", 0],
            },
        },
        "5": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_name,
            },
        },
        "6": {
            "class_type": "LTXVImgToVideo",
            "inputs": {
                "positive": ["3", 0],
                "negative": ["4", 0],
                "vae": ["1", 2],
                "image": ["5", 0],
                "width": 768,
                "height": 432,
                "length": 49,
                "batch_size": 1,
                "strength": 1.0,
            },
        },
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["6", 2],
                "seed": 42,
                "steps": int(os.environ.get("VIDEO_STEPS", "30")),
                "cfg": float(os.environ.get("VIDEO_CFG", "3.0")),
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "vae": ["1", 2],
                "samples": ["7", 0],
            },
        },
        "9": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "images": ["8", 0],
                "filename_prefix": "openflipbook_video",
                "fps": 24,
                "lossless": False,
                "quality": 80,
                "method": "default",
            },
        },
    }
    
    client_id = str(uuid.uuid4())
    
    def post_prompt():
        return requests.post(
            f"{LOCAL_IMAGE_API_URL}/prompt",
            json={"prompt": workflow, "client_id": client_id},
            timeout=30,
        )
    
    resp = await asyncio.to_thread(post_prompt)
    if resp.status_code != 200:
        raise RuntimeError(f"ComfyUI prompt failed: {resp.status_code} {resp.text}")
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
            timeout=60,
        )
    
    for _ in range(300):
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
                    
                    video_bytes = img_resp.content
                    b64_video = base64.b64encode(video_bytes).decode("ascii")
                    data_url = f"data:image/webp;base64,{b64_video}"
                    
                    return AnimatedClip(
                        video_url=data_url,
                        content_type="video/webp",
                        model="comfyui-ltxv",
                        duration_seconds=2.0,
                    )
        await asyncio.sleep(1)
    
    raise RuntimeError("ComfyUI video generation timed out")


def _parse_data_url(data_url: str) -> tuple[str, bytes]:
    m = re.match(r"^data:([^;]+);base64,(.*)$", data_url, flags=re.I)
    if not m:
        raise ValueError("not a base64 data URL")
    return m.group(1), base64.b64decode(m.group(2))


def data_url_from_bytes(body: bytes, mime: str = "image/jpeg") -> str:
    b64 = base64.b64encode(body).decode("ascii")
    return f"data:{mime};base64,{b64}"
