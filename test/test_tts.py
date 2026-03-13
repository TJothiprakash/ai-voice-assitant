import sys
import os

# Add project root to Python path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import asyncio
from ai.tts import text_to_speech


async def main():

    text = "Hello JP. This is a test of the AI phone agent."

    audio = await text_to_speech(text)

    print("Generated:", len(audio), "bytes")

    with open("test.ulaw", "wb") as f:
        f.write(audio)


asyncio.run(main())