from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from data_manager import load_user, save_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gems-miniapp-mmf25pgny-sarvesh-beheras-projects.vercel.app",
        # "http://localhost:3000",  # Uncomment for local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for debugging/deployment check
@app.get("/")
def root():
    return {"status": "ok"}

# Actual user info endpoint
@app.post("/api/user")
async def get_user(request: Request):
    data = await request.json()
    uid = data.get("uid")
    if not uid:
        return JSONResponse(status_code=400, content={"error": "Missing uid"})
    user = load_user(uid)
    return {
        "gems": user.get("gems", 0),
        "heartbeats": user.get("heartbeats", 0),
        "subscription_expiry": user.get("subscription_expiry", None)
    }

# Placeholder endpoint for buying gems
@app.post("/api/buy_gems")
async def buy_gems(request: Request):
    data = await request.json()
    uid = data.get("uid")
    qty = int(data.get("quantity", 0))
    if not uid or qty <= 0:
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid UID or quantity"})
    user = load_user(uid)
    user["gems"] = user.get("gems", 0) + qty
    save_user(uid, user)
    return {"success": True, "gems": user["gems"]}

# Placeholder endpoint for buying heartbeats
@app.post("/api/buy_heartbeats")
async def buy_heartbeats(request: Request):
    data = await request.json()
    uid = data.get("uid")
    qty = int(data.get("quantity", 0))
    if not uid or qty <= 0:
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid UID or quantity"})
    user = load_user(uid)
    user["heartbeats"] = user.get("heartbeats", 0) + qty
    save_user(uid, user)
    return {"success": True, "heartbeats": user["heartbeats"]}

# Placeholder endpoint for buying/extending subscription (by 30 days per quantity)
from datetime import datetime, timedelta

@app.post("/api/buy_subscription")
async def buy_subscription(request: Request):
    data = await request.json()
    uid = data.get("uid")
    qty = int(data.get("quantity", 0))
    if not uid or qty <= 0:
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid UID or quantity"})
    user = load_user(uid)
    # Calculate new expiry (extend from now or from current expiry)
    now = datetime.utcnow()
    current_expiry = user.get("subscription_expiry")
    if current_expiry:
        try:
            expiry = datetime.fromisoformat(current_expiry.replace("Z", "+00:00"))
            if expiry < now:
                expiry = now
        except Exception:
            expiry = now
    else:
        expiry = now
    new_expiry = expiry + timedelta(days=30 * qty)
    user["subscription_expiry"] = new_expiry.strftime("%Y-%m-%dT%H:%M:%SZ")
    save_user(uid, user)
    return {"success": True, "subscription_expiry": user["subscription_expiry"]}

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )