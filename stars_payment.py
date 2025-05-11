from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/api/buy_gems")
async def buy_gems(request: Request):
    data = await request.json()
    # Add your buy gems logic here
    return {"status": "success", "message": "Gems bought"}

@app.post("/api/user")
async def user_endpoint(request: Request):
    data = await request.json()
    # Add your user logic here
    return {"status": "success", "message": "User endpoint hit"}