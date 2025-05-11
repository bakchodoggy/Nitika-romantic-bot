from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/create_stars_invoice")
async def create_stars_invoice(request: Request):
    data = await request.json()
    gem_pack = data.get("gemPack", "100")
    price_stars = 100  # Example: 100 stars for 100 gems

    # TODO: Integrate with Telegram's Bot API to create a real invoice
    invoice_url = f"https://t.me/your_bot?start=stars_invoice_{gem_pack}"

    return JSONResponse(content={"invoice_url": invoice_url})

@app.post("/api/telegram_webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    message = payload.get("message", {})
    if "successful_payment" in message:
        user_id = message["from"]["id"]
        gem_pack = message["successful_payment"]["invoice_payload"]  # Adjust as needed
        # TODO: Credit gems to user in your database
        print(f"User {user_id} paid for {gem_pack}, credit gems here!")
        return JSONResponse(content={"ok": True})
    return JSONResponse(content={"ok": False})