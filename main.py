import random
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = FastAPI()

# --- Config ---
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
verification_codes = {}

# --- Models ---
class EmailRequest(BaseModel):
    email: str

class VerificationRequest(BaseModel):
    email: str
    code: str

# --- Helper ---
def generate_code():
    return str(random.randint(100000, 999999))

# --- 1. Send Code ---
@app.post("/send_code/")
async def send_code(data: EmailRequest):
    email = data.email
    code = generate_code()
    verification_codes[email] = code

    message = Mail(
        from_email=("no-reply@techapppartners.com", "Do I Sound Crazy"),
        to_emails=email,
        subject="DISC Verification Code",
        html_content=f"<p>Your verification code is: <strong>{code}</strong></p>"
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        if response.status_code not in range(200, 300):
            raise HTTPException(status_code=500, detail="Failed to send email")
        return {"message": "Verification code sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 2. Verify Code ---
@app.post("/verify_code/")
async def verify_code(data: VerificationRequest):
    stored_code = verification_codes.get(data.email)

    if stored_code is None:
        return {"verified": False, "message": "No code sent to this email"}
    if stored_code == data.code:
        del verification_codes[data.email]
        return {"verified": True, "message": "Email verified successfully"}
    return {"verified": False, "message": "Invalid code"}
