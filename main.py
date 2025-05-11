from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# Basic root endpoint for debugging/deployment check
@app.get("/")
def root():
    return {"status": "ok"}

# Example dashboard endpoint
@app.post("/api/user")
async def get_user(request: Request):
    # Dummy response for now; replace with your actual logic
    # To access POSTed data: data = await request.json()
    # To validate user: add your logic
    return {
        "gems": 10,
        "heartbeats": 5,
        "subscription_expiry": "2025-12-31T00:00:00Z"
    }

# Add your other dashboard endpoints here (copy your real logic)
# Example:
# @app.post("/api/buy_gems")
# async def buy_gems(request: Request):
#     # Implement your gem purchase logic here
#     return {"success": True}

# Error handler example
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )