import requests
import json

prompt_id = "34d42c94-c2a9-4780-87c3-4fdbeb973d1a"

history_resp = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=10)
history = history_resp.json()

if prompt_id in history:
    data = history[prompt_id]
    print("Status:", json.dumps(data.get("status"), indent=2))
    print("\nOutputs:", json.dumps(data.get("outputs"), indent=2))
    print("\nFull history:", json.dumps(data, indent=2)[:2000])
