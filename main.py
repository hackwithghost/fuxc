from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import datetime

app = FastAPI()

last_webhook = {}

@app.post("/webhook")
async def receive_webhook(request: Request):
    global last_webhook

    content_type = request.headers.get("content-type", "")
    payload = None

    try:
        if "application/json" in content_type:
            payload = await request.json()
        elif "application/x-www-form-urlencoded" in content_type:
            payload = dict(await request.form())
        else:
            raw = await request.body()
            payload = raw.decode("utf-8") if raw else None

    except Exception as e:
        payload = {"error": "Invalid payload", "details": str(e)}

    last_webhook = {
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "headers": dict(request.headers),
        "payload": payload
    }

    print("📩 Webhook received:", payload)

    return JSONResponse({"success": True})
