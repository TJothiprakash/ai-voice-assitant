import pyttsx3
import subprocess
import tempfile
import os

# Step 1: Generate WAV
engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

wav_path = "test_pyttsx3.wav"
engine.save_to_file("Hello! I am your payment support assistant. How can I help you today?", wav_path)
engine.runAndWait()
print(f"WAV saved: {wav_path}")

# Step 2: Convert to mulaw
ul_path = "test_pyttsx3.ul"
subprocess.run([
    "ffmpeg", "-y",
    "-i", wav_path,
    "-ar", "8000",
    "-ac", "1",
    "-f", "mulaw",
    ul_path
], check=True)
print(f"Mulaw saved: {ul_path}")

# Step 3: Convert back to WAV to verify
verify_path = "test_pyttsx3_verify.wav"
subprocess.run([
    "ffmpeg", "-y",
    "-f", "mulaw",
    "-ar", "8000",
    "-ac", "1",
    "-i", ul_path,
    verify_path
], check=True)
print(f"Verify WAV saved: {verify_path} — open this and listen!")