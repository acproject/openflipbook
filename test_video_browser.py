import base64
import requests

img_path = r"d:\workspace\python_projects\openflipbook\data\images\session_9779e7f1-edda-4c92-ba19-56f7a9f94be7\6331d82c-4e10-4f32-be43-980e59f0bf5c.jpg"

with open(img_path, "rb") as f:
    img_bytes = f.read()

b64 = base64.b64encode(img_bytes).decode("ascii")
data_url = f"data:image/jpeg;base64,{b64}"

print("Requesting video from /animate API...")
resp = requests.post(
    "http://localhost:8787/animate",
    json={
        "image_data_url": data_url,
        "prompt": "Camera slowly pans right",
        "duration": 5,
    },
    timeout=300,
)

if resp.status_code == 200:
    data = resp.json()
    video_url = data.get('video_url', '')
    
    # Extract base64 part and save as webm file
    if video_url.startswith("data:video/webm;base64,"):
        b64_data = video_url.split(",")[1]
        video_bytes = base64.b64decode(b64_data)
        with open("test_output.webm", "wb") as f:
            f.write(video_bytes)
        print(f"Saved video to test_output.webm ({len(video_bytes)} bytes)")
        
        # Also create an HTML file to test in browser
        html = f"""<!DOCTYPE html>
<html>
<head><title>Video Test</title></head>
<body>
<h2>WebM Video Test</h2>
<video controls autoplay loop muted playsinline width="768" height="432">
    <source src="{video_url}" type="video/webm">
    Your browser does not support WebM video.
</video>
</body>
</html>"""
        with open("test_video.html", "w") as f:
            f.write(html)
        print("Saved test_video.html - open this in your browser to test playback")
    else:
        print(f"Unexpected video URL format: {video_url[:100]}")
else:
    print(f"Error: {resp.status_code} - {resp.text}")
