import json

data = json.load(open("C:/Users/Admin/AppData/Local/Temp/comfyui_object_info.json"))

# Check LTXVImgToVideo requirements
ltx_img_to_video = data.get("LTXVImgToVideo", {})
print("LTXVImgToVideo inputs:")
print(json.dumps(ltx_img_to_video.get("input", {}), indent=2))

# Check CheckpointLoaderSimple outputs
checkpoint_loader = data.get("CheckpointLoaderSimple", {})
print("\nCheckpointLoaderSimple outputs:")
print(json.dumps(checkpoint_loader.get("output", []), indent=2))
