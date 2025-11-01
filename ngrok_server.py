import os
import subprocess

NGROK_AUTH = os.environ.get("34lyt5Atxx1o6wzwjc9DbOluYn8_7NVpquS6mBJKoSYkCVCrj")
PORT = os.environ.get("PORT", "5000")

if not NGROK_AUTH:
    raise ValueError("Missing NGROK_AUTH_TOKEN in environment variables")

# Start ngrok tunnel
subprocess.Popen(["ngrok", "config", "add-authtoken", NGROK_AUTH])
subprocess.Popen(["ngrok", "http", PORT])

# Keep process alive
print("✅ Ngrok tunnel started...")
while True:
    pass
