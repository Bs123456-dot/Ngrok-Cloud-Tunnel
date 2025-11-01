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
    ngrok_process = subprocess.Popen([NGROK_PATH, "http", PORT], stdout=subprocess.PIPE)

    # Wait for tunnel info to appear in the API
    time.sleep(8)
    try:
        import requests
        resp = requests.get("http://localhost:4040/api/tunnels")
        data = resp.json()
        public_url = data["tunnels"][0]["public_url"]
        print("🌐 NGROK TUNNEL URL:", public_url)
    except Exception as e:
        print("⚠️ Could not fetch tunnel URL:", e)

threading.Thread(target=start_ngrok, daemon=True).start()

# === FLASK SERVER ===
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Ngrok + Flask tunnel running on Render (Free Plan)."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(PORT))
