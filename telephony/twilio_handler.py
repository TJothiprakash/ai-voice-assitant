from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()


@router.post("/incoming-call")
async def incoming_call():

    twiml = """
<Response>

    <Connect>
        <Stream url="wss://venerably-scrubbable-dylan.ngrok-free.dev/media-stream" />
    </Connect>

</Response>
"""

    return Response(content=twiml, media_type="text/xml")