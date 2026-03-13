from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from telephony.twilio_handler import router as twilio_router
from telephony.media_stream import router as media_router



app = FastAPI()

app.include_router(twilio_router)
app.include_router(media_router)


@app.get("/")
def home():
    return {"status": "AI phone agent running"}