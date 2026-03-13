import json
import base64
import asyncio

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosed

from ai.stt import start_transcription
from ai.llm import ask_llm
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


    async def send_audio_to_twilio(audio_bytes):
        nonlocal stream_sid

        if not stream_sid:
            print("⚠️ streamSid not available yet")
            return

        chunk_size = 160
        total = len(audio_bytes)
        print(f"TTS audio generated: {total} bytes")

        # ✅ CLEAR TWILIO BUFFER BEFORE PLAYING AI AUDIO
        await ws.send_json({
            "event": "clear",
            "streamSid": stream_sid
        })

        for i in range(0, total, chunk_size):
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
            await asyncio.sleep(0.02)  # ✅ 20ms per chunk = real-time pace for 8kHz mulaw

        print(f"[TTS → Twilio] Sent {total} bytes")


    async def receive_from_twilio():
        nonlocal stream_sid

        print("Listening for Twilio audio stream...")

        try:
            while True:
                message = await ws.receive_text()
                data = json.loads(message)
                event = data.get("event")

                print(f"[Twilio EVENT] {event}")

                if event == "start":
                    stream_sid = data["start"]["streamSid"]
                    print("Twilio stream STARTED")
                    print("Stream SID:", stream_sid)

                elif event == "media":
                    payload = data["media"]["payload"]
                    audio = base64.b64decode(payload)

                    audio_buffer.extend(audio)
                    if len(audio_buffer) > 3200:
                        await dg.send(bytes(audio_buffer))
                        audio_buffer.clear()

                elif event == "stop":
                    print("Twilio stream STOPPED")
                    if len(audio_buffer) > 0:
                        await dg.send(bytes(audio_buffer))
                        audio_buffer.clear()
                    break

        except WebSocketDisconnect:
            print("Twilio WebSocket disconnected")

        except Exception as e:
            print("Twilio receiver error:", e)


    async def receive_from_deepgram():
        nonlocal is_speaking

        print("Listening for Deepgram transcripts...")

        try:
            async for message in dg:

                print("[Deepgram RAW]", message)

                data = json.loads(message)

                if data.get("type") != "Results":
                    continue

                if not data.get("speech_final"):
                    continue

                transcript = data["channel"]["alternatives"][0]["transcript"]

                if not transcript.strip():
                    continue

                if is_speaking:
                    print("[SKIPPED] AI is speaking, ignoring transcript:", transcript)
                    continue

                print("\n===== CALLER TRANSCRIPT =====")
                print(transcript)

                try:
                    is_speaking = True
                    audio_buffer.clear()

                    response = await ask_llm(transcript)

                    print("\n===== AI RESPONSE =====")
                    print(response)

                    audio = await text_to_speech(response)
                    await send_audio_to_twilio(audio)

                except Exception as e:
                    print("LLM / TTS error:", e)

                finally:
                    is_speaking = False
                    audio_buffer.clear()

        except ConnectionClosed:
            print("Deepgram connection closed")

        except Exception as e:
            print("Deepgram receiver error:", e)


    await asyncio.gather(
        receive_from_twilio(),
        receive_from_deepgram()
    )

    print("\n========== SESSION ENDED ==========\n")
