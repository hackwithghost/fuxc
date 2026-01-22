from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Store last webhook (memory)
last_webhook = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "data": last_webhook
        }
    )

@app.post("/webhook")
async def receive_webhook(request: Request):
    global last_webhook
    payload = await request.json()

    last_webhook = {
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": payload
    }

    print("📩 Webhook received:", payload)

    return JSONResponse({"success": True})
