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
    print("Received OTP token:", data.otp_token)

    if not MSG91_AUTH_KEY:
        raise HTTPException(status_code=500, detail="MSG91_AUTH_KEY is not set")

    if not data.otp_token.strip():
        raise HTTPException(status_code=400, detail="OTP token is required")

    headers = {
        "Content-Type": "application/json",
        "authkey": MSG91_AUTH_KEY,
        "access_token": data.otp_token
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(MSG91_VERIFY_URL, headers=headers)
            print("MSG91 status code:", response.status_code)
            print("MSG91 response body:", response.text)
    except Exception as e:
        print("Exception when calling MSG91:", str(e))
        raise HTTPException(status_code=500, detail="Failed to connect to MSG91")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="MSG91 service error")

    try:
        res_json = response.json()
    except Exception:
        raise HTTPException(status_code=500, detail="MSG91 returned invalid JSON")

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

    raise HTTPException(status_code=400, detail=msg)
