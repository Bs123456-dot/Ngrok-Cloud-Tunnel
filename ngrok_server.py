import os
import subprocess

NGROK_AUTH = os.environ.get("NGROK_AUTH_TOKEN")
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
