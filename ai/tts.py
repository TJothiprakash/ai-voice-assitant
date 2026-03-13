import os
import time
import subprocess
import tempfile
import shutil
import pyttsx3

# Save directory
SAVE_DIR = r"E:\os\voiceagent\ai-phone-agent\test\tts"
os.makedirs(SAVE_DIR, exist_ok=True)


async def text_to_speech(text: str) -> bytes:
    timestamp = int(time.time())

    # Step 1: Generate WAV using pyttsx3 (local, no network)
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)   # speed (default 200, slightly slower = clearer)
    engine.setProperty("volume", 1.0) # max volume

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name

    engine.save_to_file(text, wav_path)
    engine.runAndWait()
    print(f"[TTS] WAV saved to {wav_path}")

    # Step 2: Convert WAV → mulaw 8000Hz using ffmpeg
    ul_path = wav_path.replace(".wav", ".ul")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", wav_path,
        "-ar", "8000",
        "-ac", "1",
        "-acodec", "pcm_mulaw",
        "-f", "mulaw",
        ul_path
    ], check=True, capture_output=True)
    print(f"[TTS] Converted to mulaw: {ul_path}")

    # Step 3: Read the mulaw bytes
    with open(ul_path, "rb") as f:
        audio_bytes = f.read()

    # Step 4: Save debug copies
    debug_wav = os.path.join(SAVE_DIR, f"tts_{timestamp}.wav")
    debug_ul  = os.path.join(SAVE_DIR, f"tts_{timestamp}.ul")
    shutil.copy2(wav_path, debug_wav)
    with open(debug_ul, "wb") as f:
        f.write(audio_bytes)
    print(f"[TTS DEBUG] Saved WAV: {debug_wav}")
    print(f"[TTS DEBUG] Saved mulaw: {debug_ul} ({len(audio_bytes)} bytes)")

    # Step 5: Cleanup temp files
    os.remove(wav_path)
    os.remove(ul_path)

    return audio_bytes