from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI()

MSG91_VERIFY_URL = "https://control.msg91.com/api/v5/widget/verifyAccessToken"
MSG91_AUTH_KEY = "443004A7FjUniD2nJ6837cc5dP1"  # Ideally keep this in a .env file

class OTPAuthentication(BaseModel):
    otp_token: str


@app.post("/login")
async def login_func(data: OTPAuthentication):
    if not data.otp_token.strip():
        raise HTTPException(status_code=400, detail="OTP token is required")

    payload = {
        "authkey": MSG91_AUTH_KEY,
        "access-token": data.otp_token
    }

    headers = {
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(MSG91_VERIFY_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to verify OTP. MSG91 service error.")

    try:
        res_json = response.json()
        print("MSG91 JSON Response:", res_json)
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid response from MSG91")

    msg_type = res_json.get("type")
    message = res_json.get("message", "OTP verification failed")

    if msg_type == "success" or message == "access-token already verified":
        return {
            "success": True,
            "message": "OTP verified successfully"
        }

    raise HTTPException(
        status_code=400,
        detail=message
    )
