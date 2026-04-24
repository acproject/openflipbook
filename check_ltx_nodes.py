import json

data = json.load(open("C:/Users/Admin/AppData/Local/Temp/comfyui_object_info.json"))
ltx_nodes = {k: v for k, v in data.items() if "LTX" in k}
print("LTX nodes:")
for k in ltx_nodes:
    print(f"  - {k}")
