import os
import subprocess
import time
import urllib.request
import zipfile
import shutil

# === 1️⃣ CONFIGURATION ===
NGROK_AUTH = os.environ.get("NGROK_AUTH_TOKEN")
PORT = os.environ.get("PORT", "5000")

if not NGROK_AUTH:
    raise ValueError("Missing NGROK_AUTH_TOKEN in environment variables")

NGROK_ZIP_URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip"
NGROK_PATH = "/opt/render/project/src/ngrok"

# === 2️⃣ DOWNLOAD NGROK IF NOT PRESENT ===
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

# === 3️⃣ AUTHENTICATE & START TUNNEL ===
print("🔑 Adding ngrok auth token...")
subprocess.run([NGROK_PATH, "config", "add-authtoken", NGROK_AUTH], check=True)

print("🚀 Starting ngrok tunnel on port", PORT)
proc = subprocess.Popen([NGROK_PATH, "http", PORT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# === 4️⃣ KEEP SERVER ALIVE ===
print("✅ Ngrok tunnel started. Waiting for public URL...")

# Try to read tunnel URL (optional)
time.sleep(5)
try:
    import requests
    resp = requests.get("http://localhost:4040/api/tunnels")
    if resp.ok:
        tunnels = resp.json()["tunnels"]
        if tunnels:
            print("🌐 Public URL:", tunnels[0]["public_url"])
except Exception as e:
    print("⚠️ Could not fetch public URL:", e)

while True:
    time.sleep(60)
