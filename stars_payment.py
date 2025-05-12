from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["https://gems-miniapp.vercel.app"] for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/user")
async def user_endpoint(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "unknown_user")
    # TODO: In a real app, fetch these from your database using user_id
    return {
        "status": "success",
        "user_id": user_id,
        "gems": 42,  # example value
        "heartbeats": 7,  # example value
        "subscription_expiry": "2025-06-01T00:00:00Z"  # example date
    }

@app.post("/api/buy_gems")
async def buy_gems(request: Request):
    data = await request.json()
    # You can customize logic here!
    return {"status": "success", "message": "Gems bought", "data": data}

@app.post("/api/buy_heartbeats")
async def buy_heartbeats(request: Request):
    data = await request.json()
    # You can customize logic here!
    return {"status": "success", "message": "Heartbeats bought", "data": data}

@app.post("/api/buy_subscription")
async def buy_subscription(request: Request):
    data = await request.json()
    # You can customize logic here!
    return {"status": "success", "message": "Subscription bought", "data": data}

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}