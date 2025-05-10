import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hmac
import hashlib
import json
from urllib.parse import parse_qsl

from data_manager import load_user, save_user

# 1. CORS: Use your actual deployed Vercel frontend domain here!
ALLOWED_ORIGINS = [
    "https://gems-miniapp-mmf25pgny-sarvesh-beheras-projects.vercel.app",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Make sure this is set in your hosting environment

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
    print(f"User request: {req}")
    user = check_telegram_init_data(req.hash, TOKEN)
    print(f"Validated Telegram user: {user['id']}")
    if user["id"] != req.telegram_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    uid = str(req.telegram_id)
    data = load_user(uid) or {}
    print(f"Loaded data for {uid}: {data}")
    return {
        "gems": data.get("gems", 100),
        "heartbeats": data.get("heartbeats", 7),
        "subscription_expires": data.get("subscription_expires", "2025-12-31")
    }

# Example endpoint to buy heartbeats (call from frontend after payment!)
class BuyRequest(BaseModel):
    telegram_id: int
    hash: str
    quantity: int

@app.post("/api/buy_heartbeats")
async def buy_heartbeats(req: BuyRequest):
    user = check_telegram_init_data(req.hash, TOKEN)
    if user["id"] != req.telegram_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    uid = str(req.telegram_id)
    data = load_user(uid) or {}
    data["heartbeats"] = data.get("heartbeats", 7) + req.quantity
    save_user(uid, data)
    print(f"User {uid} bought {req.quantity} heartbeats. New total: {data['heartbeats']}")
    return {"success": True, "heartbeats": data["heartbeats"]}

@app.post("/api/buy_gems")
async def buy_gems(req: BuyRequest):
    user = check_telegram_init_data(req.hash, TOKEN)
    if user["id"] != req.telegram_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    uid = str(req.telegram_id)
    data = load_user(uid) or {}
    data["gems"] = data.get("gems", 100) + req.quantity
    save_user(uid, data)
    print(f"User {uid} bought {req.quantity} gems. New total: {data['gems']}")
    return {"success": True, "gems": data["gems"]}

@app.post("/api/buy_subscription")
async def buy_subscription(req: BuyRequest):
    from datetime import datetime, timedelta
    user = check_telegram_init_data(req.hash, TOKEN)
    if user["id"] != req.telegram_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    uid = str(req.telegram_id)
    data = load_user(uid) or {}
    # Extend subscription by 30 days per quantity
    if data.get("subscription_expires"):
        try:
            current_expiry = datetime.strptime(data["subscription_expires"], "%Y-%m-%d")
            if current_expiry < datetime.now():
                current_expiry = datetime.now()
        except Exception:
            current_expiry = datetime.now()
    else:
        current_expiry = datetime.now()
    new_expiry = current_expiry + timedelta(days=30 * req.quantity)
    data["subscription_expires"] = new_expiry.strftime("%Y-%m-%d")
    save_user(uid, data)
    print(f"User {uid} extended subscription by {30 * req.quantity} days. New expiry: {data['subscription_expires']}")
    return {"success": True, "subscription_expires": data["subscription_expires"]}

@app.get("/")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))