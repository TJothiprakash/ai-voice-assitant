import json
import base64
import asyncio
import time

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosed

from ai.stt import start_transcription
from ai.llm import ask_llm, OPENING_MESSAGE
from ai.tts import text_to_speech

router = APIRouter()


@router.websocket("/media-stream")
async def media_stream(ws: WebSocket):

    await ws.accept()
    print("\n========== TWILIO WS CONNECTED ==========")

    dg = await start_transcription()
    print("Deepgram connection established\n")

    audio_buffer = bytearray()
    stream_sid = None

    is_speaking = False
    interrupt_ai = False

    # silence detection
    partial_transcript = ""
    last_speech_time = 0
    SILENCE_TIMEOUT = 0.7  # seconds


    async def send_audio_to_twilio(audio_bytes):
        nonlocal stream_sid, interrupt_ai

        if not stream_sid:
            print("⚠️ streamSid not available yet")
            return

        chunk_size = 160
        total = len(audio_bytes)

        await ws.send_json({
            "event": "clear",
            "streamSid": stream_sid
        })

        for i in range(0, total, chunk_size):

            if interrupt_ai:
                print("🛑 TTS interrupted (barge-in)")
                break

            chunk = audio_bytes[i:i + chunk_size]

            if len(chunk) < chunk_size:
                chunk = chunk.ljust(chunk_size, b"\0")

            payload = base64.b64encode(chunk).decode()

            message = {
                "event": "media",
                "streamSid": stream_sid,
                "media": {"payload": payload}
            }

            await ws.send_json(message)
            await asyncio.sleep(0.02)


    async def process_user_text(text):
        nonlocal is_speaking, interrupt_ai

        try:
            is_speaking = True
            interrupt_ai = False

            print("\n===== CALLER TRANSCRIPT =====")
            print(text)

            response = await ask_llm(text)

            print("\n===== AI RESPONSE =====")
            print(response)

            audio = await text_to_speech(response)
            await send_audio_to_twilio(audio)

        except Exception as e:
            print("LLM / TTS error:", e)

        finally:
            is_speaking = False


    async def silence_monitor():
        nonlocal partial_transcript, last_speech_time

        while True:
            await asyncio.sleep(0.1)

            if not partial_transcript:
                continue

            if time.time() - last_speech_time > SILENCE_TIMEOUT:

                text = partial_transcript.strip()
                partial_transcript = ""

                if text:
                    await process_user_text(text)


    async def receive_from_twilio():
        nonlocal stream_sid, is_speaking

        try:
            while True:
                message = await ws.receive_text()
                data = json.loads(message)
                event = data.get("event")

                if event == "start":
                    stream_sid = data["start"]["streamSid"]
                    print("Stream SID:", stream_sid)

                    # Play greeting message
                    try:
                        is_speaking = True
                        greeting_audio = await text_to_speech(OPENING_MESSAGE)
                        await send_audio_to_twilio(greeting_audio)
                    finally:
                        is_speaking = False

                elif event == "media":
                    payload = data["media"]["payload"]
                    audio = base64.b64decode(payload)

                    audio_buffer.extend(audio)

                    if len(audio_buffer) > 3200:
                        await dg.send(bytes(audio_buffer))
                        audio_buffer.clear()

                elif event == "stop":
                    break

        except WebSocketDisconnect:
            print("Twilio WebSocket disconnected")


    async def receive_from_deepgram():
        nonlocal partial_transcript, last_speech_time, is_speaking, interrupt_ai

        try:
            async for message in dg:

                data = json.loads(message)

                if data.get("type") != "Results":
                    continue

                transcript = data["channel"]["alternatives"][0]["transcript"]

                if not transcript.strip():
                    continue

                # ⚡ Barge-in
                if is_speaking:
                    print("⚡ BARGE-IN DETECTED")

                    interrupt_ai = True

                    await ws.send_json({
                        "event": "clear",
                        "streamSid": stream_sid
                    })

                    is_speaking = False
                    continue

                partial_transcript = transcript
                last_speech_time = time.time()

        except ConnectionClosed:
            print("Deepgram connection closed")


    await asyncio.gather(
        receive_from_twilio(),
        receive_from_deepgram(),
        silence_monitor()
    )

    print("\n========== SESSION ENDED ==========\n")