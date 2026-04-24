import requests
import json
import time

img_path = r"d:\workspace\python_projects\openflipbook\data\images\session_9779e7f1-edda-4c92-ba19-56f7a9f94be7\6331d82c-4e10-4f32-be43-980e59f0bf5c.jpg"

with open(img_path, "rb") as f:
    img_bytes = f.read()

print(f"Uploading image to ComfyUI...")
files = {"image": ("input.png", img_bytes, "image/png")}
resp = requests.post("http://127.0.0.1:8188/upload/image", files=files, timeout=30)
print(f"Upload status: {resp.status_code}")
image_name = resp.json().get("name", "input.png")
print(f"Image name: {image_name}")

prompt = "Camera slowly pans right, showing the Eiffel Tower in golden hour light"

# Use CLIPLoader to load umt5_xxl text encoder separately
# Use LoadImage to load the uploaded image as IMAGE tensor
workflow = {
    "1": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": "ltx-video-2b-v0.9.safetensors",
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
            "steps": 20,
            "cfg": 3.0,
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
            "filename_prefix": "test_video",
            "fps": 24,
            "lossless": False,
            "quality": 80,
            "method": "default",
        },
    },
}

print("\nSending prompt to ComfyUI...")
resp = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow}, timeout=30)
print(f"Prompt status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")

if resp.status_code == 200:
    prompt_data = resp.json()
    prompt_id = prompt_data.get("prompt_id")
    print(f"Prompt ID: {prompt_id}")
    
    if prompt_id:
        print("\nWaiting for generation (max 5 minutes)...")
        for i in range(150):
            time.sleep(2)
            history_resp = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=10)
            if history_resp.status_code == 200:
                history = history_resp.json()
                if prompt_id in history:
                    data = history[prompt_id]
                    status = data.get("status", {})
                    if status.get("status_str") == "success":
                        print(f"\nGeneration SUCCESS!")
                        outputs = data.get("outputs", {})
                        print(f"Outputs: {json.dumps(outputs, indent=2)[:1000]}")
                        
                        if "9" in outputs:
                            images = outputs["9"].get("images", [])
                            if images:
                                output = images[0]
                                print(f"\nVideo file: {output}")
                                view_resp = requests.get(
                                    "http://127.0.0.1:8188/view",
                                    params={"filename": output["filename"], "subfolder": output.get("subfolder", ""), "type": output.get("type", "output")},
                                    timeout=30,
                                )
                                if view_resp.status_code == 200:
                                    print(f"Video size: {len(view_resp.content)} bytes")
                                    with open("test_output.webp", "wb") as f:
                                        f.write(view_resp.content)
                                    print("Saved to test_output.webp")
                        break
                    elif status.get("status_str") == "error":
                        print(f"\nGeneration FAILED!")
                        print(f"Status: {json.dumps(status, indent=2)[:2000]}")
                        break
                    else:
                        print(f"  Still processing... ({i*2}s)")
                else:
                    print(f"  Still processing... ({i*2}s)")
            else:
                print(f"  History check failed: {history_resp.status_code}")
        else:
            print("Timed out waiting for generation")
