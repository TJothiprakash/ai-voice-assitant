import os
import websockets

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

async def start_transcription():

    url = (
        "wss://api.deepgram.com/v1/listen"
        "?model=nova-2"
        "&encoding=mulaw"
        "&sample_rate=8000"
        "&channels=1"
        "&interim_results=true"
    )

    ws = await websockets.connect(
        url,
        additional_headers={
            "Authorization": f"Token {DEEPGRAM_API_KEY}"
        }
    )

    print("Deepgram connected")

    return ws