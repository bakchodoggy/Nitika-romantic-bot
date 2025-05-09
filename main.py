import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hmac
import hashlib
import json
from urllib.parse import parse_qsl

from data_manager import load_user

ALLOWED_ORIGINS = [
    "https://your-vercel-app.vercel.app",  # <-- CHANGE THIS to your actual Vercel app URL
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

class UserRequest(BaseModel):
    telegram_id: int
    hash: str  # Telegram Mini App's initData

def check_telegram_init_data(init_data: str, bot_token: str) -> dict:
    try:
        data = dict(parse_qsl(init_data, strict_parsing=True))
        hash_check = data.pop("hash", None)
        if not hash_check:
            raise ValueError("Missing hash")
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
        secret = hashlib.sha256(bot_token.encode()).digest()
        h = hmac.new(secret, data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
        if not hmac.compare_digest(h, hash_check):
            raise ValueError("Hash check failed")
        user = json.loads(data["user"])
        return user
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Telegram validation error: {str(e)}")

@app.post("/api/user")
async def get_user_data(req: UserRequest):
    user = check_telegram_init_data(req.hash, TOKEN)
    if user["id"] != req.telegram_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    uid = str(req.telegram_id)
    data = load_user(uid) or {}
    return {
        "gems": data.get("gems", 100),
        "heartbeats": data.get("heartbeats", 7),
        "subscription_expires": data.get("subscription_expires", "2025-12-31")
    }

@app.get("/")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))