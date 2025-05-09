import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import your user data management functions as needed
# from data_manager import load_user

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

@app.get("/")
async def health():
    return {"status": "ok"}

class UserRequest(BaseModel):
    telegram_id: int
    hash: str

@app.post("/api/user")
async def get_user_data(req: UserRequest):
    # Placeholder: Replace with your real user data function
    data = {
        "gems": 100,
        "heartbeats": 7,
        "subscription_expires": "2025-12-31"
    }
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))