import asyncio
import websockets
import json
import base64


async def simulate_call():

    uri = "ws://localhost:8000/media-stream"

    async with websockets.connect(uri) as ws:

        print("Connected to server")

        start_event = {
            "event": "start",
            "start": {"streamSid": "SIMULATED_STREAM"}
        }

        await ws.send(json.dumps(start_event))

        print("Sent start event")

        with open("test_audio.raw", "rb") as f:

            chunk_size = 320  # 20ms audio for 8kHz 16bit

            while True:

                audio_chunk = f.read(chunk_size)

                if not audio_chunk:
                    break

                payload = base64.b64encode(audio_chunk).decode()

                media_event = {
                    "event": "media",
                    "media": {"payload": payload}
                }

                await ws.send(json.dumps(media_event))

                await asyncio.sleep(0.02)

        await ws.send(json.dumps({"event": "stop"}))

        print("Simulation finished")


asyncio.run(simulate_call())