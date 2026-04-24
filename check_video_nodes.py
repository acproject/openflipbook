import json

data = json.load(open("C:/Users/Admin/AppData/Local/Temp/comfyui_object_info.json"))

# Check SaveWEBM details
save_webm = data.get("SaveWEBM", {})
print("=== SaveWEBM ===")
print(json.dumps(save_webm.get("input", {}), indent=2))

# Check if there's any MP4 or H264 save node
for key in data:
    if "mp4" in key.lower() or "h264" in key.lower() or "ffmpeg" in key.lower():
        print(f"\n=== {key} ===")
        print(json.dumps(data[key].get("input", {}), indent=2))

# Also check VHS_VideoCombine which is common
for key in data:
    if "vhs" in key.lower() or "videocombine" in key.lower():
        print(f"\n=== {key} ===")
        inputs = data[key].get("input", {})
        if "required" in inputs:
            for k, v in inputs["required"].items():
                print(f"  {k}: {v}")
