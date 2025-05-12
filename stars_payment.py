from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users = {}

@app.post("/api/user")
async def user_endpoint(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "unknown_user")
    user = users.get(user_id, {"gems": 0, "heartbeats": 0, "subscription_expiry": None})
    return {
        "status": "success",
        "user_id": user_id,
        "gems": user["gems"],
        "heartbeats": user["heartbeats"],
        "subscription_expiry": user["subscription_expiry"],
    }

@app.post("/api/buy_heartbeats")
async def buy_heartbeats(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "unknown_user")
    amount = data.get("amount", 1)
    user = users.setdefault(user_id, {"gems": 0, "heartbeats": 0, "subscription_expiry": None})
    user["heartbeats"] += amount
    return {"status": "success", "message": "Heartbeats bought", "heartbeats": user["heartbeats"]}

@app.post("/api/use_heartbeat")
async def use_heartbeat(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "unknown_user")
    user = users.setdefault(user_id, {"gems": 0, "heartbeats": 0, "subscription_expiry": None})
    if user["heartbeats"] > 0:
        user["heartbeats"] -= 1
        return {"status": "success", "message": "Heartbeat used", "heartbeats": user["heartbeats"]}
    else:
        return {"status": "error", "message": "No heartbeats left", "heartbeats": 0}

@app.post("/api/buy_gems")
async def buy_gems(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "unknown_user")
    amount = data.get("amount", 1)
    user = users.setdefault(user_id, {"gems": 0, "heartbeats": 0, "subscription_expiry": None})
    user["gems"] += amount
    return {"status": "success", "message": "Gems bought", "gems": user["gems"]}

@app.post("/api/buy_subscription")
async def buy_subscription(request: Request):
    from datetime import datetime, timedelta
    data = await request.json()
    user_id = data.get("user_id", "unknown_user")
    days = data.get("days", 30)
    user = users.setdefault(user_id, {"gems": 0, "heartbeats": 0, "subscription_expiry": None})
    expiry = datetime.utcnow() + timedelta(days=days)
    user["subscription_expiry"] = expiry.isoformat() + "Z"
    return {"status": "success", "message": "Subscription bought", "subscription_expiry": user["subscription_expiry"]}

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}