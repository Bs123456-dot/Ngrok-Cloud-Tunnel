import os
import subprocess
import threading
import time
import urllib.request
import zipfile
import shutil
from flask import Flask
import json

# === CONFIG ===
NGROK_AUTH = os.environ.get("NGROK_AUTH_TOKEN")
PORT = os.environ.get("PORT", "5000")

if not NGROK_AUTH:
    raise ValueError("Missing NGROK_AUTH_TOKEN in environment variables")

NGROK_ZIP_URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip"
NGROK_PATH = "/opt/render/project/src/ngrok"

# === DOWNLOAD NGROK ===
if not os.path.exists(NGROK_PATH):
    print("⬇️ Downloading ngrok binary...")
    zip_path = "ngrok.zip"
    urllib.request.urlretrieve(NGROK_ZIP_URL, zip_path)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(".")
    os.chmod("ngrok", 0o755)
    shutil.move("ngrok", NGROK_PATH)
    os.remove(zip_path)
    print("✅ Ngrok downloaded successfully.")

# === START NGROK ===
def start_ngrok():
    print("🔑 Adding ngrok auth token...")
    subprocess.run([NGROK_PATH, "config", "add-authtoken", NGROK_AUTH], check=True)
    print("🚀 Starting ngrok tunnel on port", PORT)
    ngrok_process = subprocess.Popen([NGROK_PATH, "http", PORT], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Wait and try repeatedly to get the public URL
    import requests
    tunnel_url = None
    for i in range(15):  # try for ~30 seconds
        time.sleep(2)
        try:
            resp = requests.get("http://localhost:4040/api/tunnels")
            data = resp.json()
            if data.get("tunnels"):
                tunnel_url = data["tunnels"][0]["public_url"]
                break
        except Exception:
            continue

    if tunnel_url:
        print(f"🌐 NGROK TUNNEL URL: {tunnel_url}")
        # store it globally so Flask can serve it
        global current_tunnel_url
        current_tunnel_url = tunnel_url
    else:
        print("⚠️ Could not detect tunnel URL from localhost:4040")

# === FLASK SERVER ===
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Ngrok + Flask tunnel running on Render (Free Plan)."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(PORT))
