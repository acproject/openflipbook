# Local Setup Guide - Endless Canvas

Complete local setup without Docker, OpenRouter, or fal.ai.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  llama.cpp      │         │  Python Backend  │         │  Image Gen API  │
│  (LLM/VLM)      │◄────────│  FastAPI         │────────►│  (SD/ComfyUI)   │
│  :8080          │         │  :8787           │         │  :7860/:8188    │
└─────────────────┘         └────────┬─────────┘         └─────────────────┘
                                     │
                                     ▼
                          ┌──────────────────┐
                          │  Next.js Web     │
                          │  :3000           │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │  Local Storage   │
                          │  JSON + Files    │
                          └──────────────────┘
```

## Prerequisites

### 1. Install Python 3.12+

Download from: https://www.python.org/downloads/

```bash
python --version
```

### 2. Install Node.js 20+

Download from: https://nodejs.org/

```bash
node --version
npm --version
```

### 3. Install pnpm

```bash
npm install -g pnpm
```

### 4. Setup llama.cpp

#### Download llama.cpp

1. Download pre-built binaries from: https://github.com/ggerganov/llama.cpp/releases
2. Or build from source:
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   cmake -B build
   cmake --build build --config Release
   ```

#### Download Models

**Text Model (Qwen2.5-7B-Instruct):**
- Download from HuggingFace: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF
- Recommended: `qwen2.5-7b-instruct-q4_k_m.gguf` (~4.5GB)

**Vision Model (Qwen2.5-VL-7B):**
- Download from: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct-GGUF
- You need both the model file and the mmproj (multimodal projector) file

#### Run llama.cpp Server

**Text model:**
```bash
server.exe -m qwen2.5-7b-instruct-q4_k_m.gguf --host 0.0.0.0 --port 8080 -c 4096
```

**Vision model (for click-to-explore):**
```bash
server.exe -m qwen2.5-vl-7b-instruct-q4_k_m.gguf --host 0.0.0.0 --port 8081 -c 4096 --mmproj qwen2.5-vl-7b-mmproj.gguf
```

### 5. Setup Image Generation

Choose ONE of the following:

#### Option A: AUTOMATIC1111 (Recommended for simplicity)

1. Install from: https://github.com/AUTOMATIC1111/stable-diffusion-webui
2. Download a model (e.g., FLUX.1-dev, SDXL, or any SD model)
3. Start with API enabled:
   ```bash
   webui-user.bat --api
   ```
4. Default URL: http://localhost:7860

#### Option B: ComfyUI

1. Install from: https://github.com/comfyanonymous/ComfyUI
2. Download a model and place it in `ComfyUI/models/checkpoints/`
3. Start ComfyUI:
   ```bash
   python main.py
   ```
4. Default URL: http://localhost:8188

## Setup Steps

### Step 1: Run Setup Script

```bash
.\scripts\setup-local.bat
```

This will:
- Create Python virtual environment
- Install Python dependencies
- Install Node.js dependencies
- Create configuration files

### Step 2: Configure Backend

Edit `apps\modal-backend\.env`:

```env
# llama.cpp server URL
LLAMACPP_BASE_URL=http://localhost:8080/v1

# Model names (optional, defaults shown)
LLAMACPP_TEXT_MODEL=qwen2.5-7b
LLAMACPP_VLM_MODEL=qwen2.5-vl-7b

# Image generation API
LOCAL_IMAGE_API_URL=http://localhost:7860
LOCAL_IMAGE_API_TYPE=automatic1111

# Image generation parameters
IMAGE_STEPS=30
IMAGE_CFG=7.0
```

### Step 3: Configure Web App

Edit `apps\web\.env.local`:

```env
MODAL_API_URL=http://localhost:8787
NEXT_PUBLIC_LTX_WS_URL=
```

### Step 4: Start Services

Open 3 terminal windows:

**Terminal 1 - llama.cpp server:**
```bash
# Navigate to your llama.cpp directory
server.exe -m your-model.gguf --host 0.0.0.0 --port 8080 -c 4096
```

**Terminal 2 - Image generation server:**
```bash
# AUTOMATIC1111
webui-user.bat --api

# OR ComfyUI
python main.py
```

**Terminal 3 - Python backend:**
```bash
.\scripts\start-backend.bat
```

**Terminal 4 - Web app:**
```bash
.\scripts\start-web.bat
```

### Step 5: Open the App

Navigate to: http://localhost:3000/play

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 16GB | 32GB |
| GPU VRAM | 8GB | 12GB+ |
| Storage | 20GB | 50GB+ |

### Model Size Guide

| Model | Quantization | VRAM | Quality |
|-------|--------------|------|---------|
| Qwen2.5-7B | Q4_K_M | ~5GB | Good |
| Qwen2.5-7B | Q8_0 | ~8GB | Better |
| Qwen2.5-72B | Q4_K_M | ~40GB | Best |
| Qwen2.5-VL-7B | Q4_K_M | ~6GB | Good |

## Troubleshooting

### Backend can't connect to llama.cpp

```bash
curl http://localhost:8080/v1/models
```

Should return a list of models. If not, check llama.cpp is running.

### Backend can't connect to image generation

```bash
# AUTOMATIC1111
curl http://localhost:7860/sdapi/v1/options

# ComfyUI
curl http://localhost:8188/system_stats
```

### Check backend health

```bash
curl http://localhost:8787/health
```

Should return: `{"ok": true, "service": "openflipbook-generate"}`

### Images not generating

- Check image generation server logs
- Verify model is loaded
- Check VRAM availability
- Try generating a test image via API

### LLM responses are slow

- Use smaller quantization (Q4 instead of Q8)
- Reduce context length (`-c 2048` instead of 4096)
- Consider using a smaller model (1.5B or 3B instead of 7B)

## Data Storage

All data is stored locally in the `data/` directory:

```
data/
├── nodes.json          # Page metadata
└── images/             # Generated images
    └── session_*/
        └── *.jpg
```

To reset all data:
```bash
rmdir /s /q data
```

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| LLAMACPP_BASE_URL | llama.cpp server URL | http://localhost:8080/v1 |
| LLAMACPP_TEXT_MODEL | Text model name | qwen2.5-7b |
| LLAMACPP_VLM_MODEL | Vision model name | qwen2.5-vl-7b |
| LOCAL_IMAGE_API_URL | Image generation API URL | http://localhost:7860 |
| LOCAL_IMAGE_API_TYPE | API type: automatic1111 or comfyui | automatic1111 |
| IMAGE_STEPS | Generation steps | 30 |
| IMAGE_CFG | CFG scale | 7.0 |
| PORT | Backend port | 8787 |

### Web App (.env.local)

| Variable | Description | Default |
|----------|-------------|---------|
| MODAL_API_URL | Backend URL | http://localhost:8787 |
| NEXT_PUBLIC_LTX_WS_URL | LTX streaming URL | (empty) |

## Next Steps

- Explore pages by clicking on images
- Check `/status` page for environment health
- View generated images in `data/images/`
- View page metadata in `data/nodes.json`
