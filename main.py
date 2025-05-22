from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from data_manager import load_user, save_user
from datetime import datetime, timedelta

# --- ADDED FOR PAYMENT GATEWAYS ---
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gems-miniapp.vercel.app"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/api/user")
async def get_user(request: Request):
    data = await request.json()
    uid = data.get("uid")
    if not uid:
        return JSONResponse(status_code=400, content={"error": "Missing uid"})
    user = load_user(uid)
    return {
        "telegram_stars": user.get("telegram_stars", 0),
        "gems": user.get("gems", 0),
        "heartbeats": user.get("heartbeats", 0),
        "subscription_expiry": user.get("subscription_expiry", None),
    }

@app.post("/api/buy_stars")
async def buy_stars(request: Request):
    data = await request.json()
    uid = data.get("uid")
    qty = int(data.get("quantity", 0))
    if not uid or qty <= 0:
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid UID or quantity"})
    user = load_user(uid)
    user["telegram_stars"] = user.get("telegram_stars", 0) + qty
    save_user(uid, user)
    return {"success": True, "telegram_stars": user["telegram_stars"]}

@app.post("/api/buy_heartbeats")
async def buy_heartbeats(request: Request):
    data = await request.json()
    uid = data.get("uid")
    qty = int(data.get("quantity", 0))
    cost = qty * 5  # Example: 1 Heartbeat costs 5 stars
    if not uid or qty <= 0:
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid UID or quantity"})
    user = load_user(uid)
    if user.get("telegram_stars", 0) < cost:
        return JSONResponse(status_code=400, content={"success": False, "message": "Not enough Telegram Stars"})
    user["telegram_stars"] -= cost
    user["heartbeats"] = user.get("heartbeats", 0) + qty
    save_user(uid, user)
    return {"success": True, "heartbeats": user["heartbeats"], "telegram_stars": user["telegram_stars"]}

@app.post("/api/buy_gems")
async def buy_gems(request: Request):
    data = await request.json()
    uid = data.get("uid")
    qty = int(data.get("quantity", 0))
    cost = qty * 10  # Example: 1 Gem costs 10 stars
    if not uid or qty <= 0:
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid UID or quantity"})
    user = load_user(uid)
    if user.get("telegram_stars", 0) < cost:
        return JSONResponse(status_code=400, content={"success": False, "message": "Not enough Telegram Stars"})
    user["telegram_stars"] -= cost
    user["gems"] = user.get("gems", 0) + qty
    save_user(uid, user)
    return {"success": True, "gems": user["gems"], "telegram_stars": user["telegram_stars"]}

@app.post("/api/buy_subscription")
async def buy_subscription(request: Request):
    data = await request.json()
    uid = data.get("uid")
    qty = int(data.get("quantity", 0))
    cost = qty * 50  # Example: 1 subscription period costs 50 stars
    if not uid or qty <= 0:
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid UID or quantity"})
    user = load_user(uid)
    if user.get("telegram_stars", 0) < cost:
        return JSONResponse(status_code=400, content={"success": False, "message": "Not enough Telegram Stars"})
    user["telegram_stars"] -= cost
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
    return {"success": True, "subscription_expiry": user["subscription_expiry"], "telegram_stars": user["telegram_stars"]}

# ===========================
# NEW: DUAL PAYMENT ENDPOINTS
# ===========================

# --- Telegram Invoice ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "put-your-bot-token-here")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
TELEGRAM_PROVIDER_TOKEN = os.getenv("TELEGRAM_PROVIDER_TOKEN", "your-provider-token-here")

@app.post("/api/telegram_invoice")
async def telegram_invoice(request: Request):
    data = await request.json()
    uid = data.get("uid")
    amount = int(data.get("amount", 0))
    if not uid or amount <= 0:
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid UID or amount"})
    chat_id = int(uid)
    payload = {
        "chat_id": chat_id,
        "title": "Buy Gems",
        "description": f"Purchase {amount} Gems for your account.",
        "payload": f"buy_gems_{uid}_{amount}_{datetime.utcnow().timestamp()}",
        "provider_token": TELEGRAM_PROVIDER_TOKEN,
        "currency": "INR",
        "prices": [{"label": f"{amount} Gems", "amount": amount * 1000}],  # 1 Gem = ₹10.00 (1000 paise)
        "start_parameter": "gems_purchase",
        "need_email": False,
    }
    resp = requests.post(f"{TELEGRAM_API_URL}/sendInvoice", json=payload)
    if resp.status_code == 200:
        return {"success": True, "message": "Invoice sent in Telegram!"}
    else:
        return JSONResponse(status_code=500, content={"success": False, "message": "Could not send invoice", "error": resp.text})

# --- External Payment Gateway (Razorpay sample) ---
RAZORPAY_PUBLIC_KEY = os.getenv("RAZORPAY_PUBLIC_KEY", "")
RAZORPAY_SECRET_KEY = os.getenv("RAZORPAY_SECRET_KEY", "")

@app.post("/api/external_gems_payment")
async def external_gems_payment(request: Request):
    data = await request.json()
    uid = data.get("uid")
    amount = int(data.get("amount", 0))
    if not uid or amount <= 0:
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid UID or amount"})
    payment_link = create_razorpay_payment_link(uid, amount)
    if payment_link:
        return {"success": True, "url": payment_link}
    return JSONResponse(status_code=500, content={"success": False, "message": "Could not create payment link"})

def create_razorpay_payment_link(uid, amount):
    url = "https://api.razorpay.com/v1/payment_links"
    auth = (RAZORPAY_PUBLIC_KEY, RAZORPAY_SECRET_KEY)
    headers = {"Content-Type": "application/json"}
    payload = {
        "amount": amount * 1000,  # ₹10 per gem, 1000 paise = ₹10
        "currency": "INR",
        "description": f"Purchase {amount} Gems",
        "reference_id": f"{uid}_{datetime.utcnow().timestamp()}",
        # CHANGE THIS to your deployed webhook/callback URL:
        "callback_url": "https://yourdomain.com/api/gems_payment_webhook",  
        "callback_method": "get"
    }
    resp = requests.post(url, auth=auth, json=payload, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("short_url")
    return None

# --- Webhook for External Payment Success ---
@app.post("/api/gems_payment_webhook")
async def gems_payment_webhook(request: Request):
    data = await request.json()
    # Validate and parse Razorpay webhook (implement proper validation for production!)
    ref = data.get("reference_id", "")
    uid = ref.split("_")[0] if ref else None
    amount = int(data.get("amount", 0)) // 1000 if data.get("amount") else 0
    if not uid or amount <= 0:
        return JSONResponse(status_code=400, content={"success": False, "message": "Invalid payment"})
    user = load_user(uid)
    user["gems"] = user.get("gems", 0) + amount
    save_user(uid, user)
    return {"success": True}