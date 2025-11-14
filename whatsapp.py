import os
import json
from fastapi import HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from twilio.rest import Client

### El siguiente código no se utiliza actualmente, pero se deja como referencia ###

# Cargar variables de entorno
load_dotenv()

# Twilio config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
TARGET_WHATSAPP_NUMBER = os.getenv("TARGET_WHATSAPP_NUMBER")
TWILIO_CONTENT_TEMPLATE_SID = os.getenv("TWILIO_CONTENT_TEMPLATE_SID")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class WhatsAppRequest(BaseModel):
    user_name: str

@app.post("/send_whatsapp")
async def send_whatsapp(request: WhatsAppRequest):
    """
    Envía un mensaje de plantilla de WhatsApp usando Twilio.
    La función actualmente no se utiliza, pero se deja el código como referencia.
    """
    try:
        message = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=TARGET_WHATSAPP_NUMBER,
            content_sid=TWILIO_CONTENT_TEMPLATE_SID,
            content_variables=json.dumps({"1": request.user_name}),
        )
        logger.info("Template WhatsApp message sent (SID: %s)", message.sid)
        return {"status": "success", "sid": message.sid}
    except Exception as exc:
        logger.error("Failed to send template WhatsApp message: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to send WhatsApp message")