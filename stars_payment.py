from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/create_stars_invoice")
async def create_stars_invoice(request: Request):
    data = await request.json()
    gem_pack = data.get("gemPack", "100")
    price_stars = 100  # Example: 100 stars for 100 gems

    # You would typically generate the invoice via the Telegram Bot API here
    # This is a placeholder. Replace with real invoice creation logic.
    invoice_url = f"https://t.me/your_bot?start=stars_invoice_{gem_pack}"

    return JSONResponse(content={"invoice_url": invoice_url})

@app.post("/api/telegram_webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    if "successful_payment" in payload.get("message", {}):
        user_id = payload["message"]["from"]["id"]
        gem_pack = payload["message"]["successful_payment"]["invoice_payload"]  # Adjust as needed
        # TODO: Credit gems to user in your database
        print(f"User {user_id} paid for {gem_pack}, credit gems here!")
        return {"ok": True}
    return {"ok": False}