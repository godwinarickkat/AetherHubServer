from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
MSG91_VERIFY_URL = "https://control.msg91.com/api/v5/otp/token/verify"
MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY")

app = FastAPI()

class OTPAuthentication(BaseModel):
    otp_token: str  # This is the access_token from frontend

@app.post("/login")
async def login_func(data: OTPAuthentication):
    if not data.otp_token.strip():
        raise HTTPException(status_code=400, detail="OTP token is required")

    headers = {
        "Content-Type": "application/json",
        "authkey": MSG91_AUTH_KEY,
        "access_token": data.otp_token
    }

    async with httpx.AsyncClient() as client:
        # ✅ Make GET request (not POST)
        response = await client.get(MSG91_VERIFY_URL, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to verify OTP. MSG91 service error.")

    try:
        res_json = response.json()
        print("MSG91 JSON Response:", res_json)
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid response from MSG91")

    # Handle successful or already-verified token
    if res_json.get("type") == "success":
        return {
            "success": True,
            "message": res_json.get("message", "OTP verified successfully")
        }

    msg = res_json.get("message", "OTP verification failed")

    if msg == "access-token already verified":
        return {
            "success": True,
            "message": "OTP already verified earlier"
        }

    raise HTTPException(
        status_code=400,
        detail=msg
    )
