import os
import subprocess
import threading
import time
import urllib.request
import zipfile
import shutil
from flask import Flask

# === 1️⃣ CONFIG ===
NGROK_AUTH = os.environ.get("NGROK_AUTH_TOKEN")
PORT = os.environ.get("PORT", "5000")

if not NGROK_AUTH:
    raise ValueError("Missing NGROK_AUTH_TOKEN in environment variables")

NGROK_ZIP_URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip"
NGROK_PATH = "/opt/render/project/src/ngrok"

# === 2️⃣ DOWNLOAD NGROK IF NEEDED ===
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

# === 3️⃣ START NGROK IN BACKGROUND ===
def start_ngrok():
    print("🔑 Adding ngrok auth token...")
    subprocess.run([NGROK_PATH, "config", "add-authtoken", NGROK_AUTH], check=True)
    print("🚀 Starting ngrok tunnel on port", PORT)
    subprocess.Popen([NGROK_PATH, "http", PORT])
    time.sleep(5)
    print("✅ Ngrok tunnel should now be live!")

threading.Thread(target=start_ngrok, daemon=True).start()

# === 4️⃣ MINIMAL FLASK APP TO KEEP PORT OPEN ===
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Ngrok tunnel service is active on Render Free Plan!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(PORT))
