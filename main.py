from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os
import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

events = []  # webhook history (memory)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "events": events
        }
    )

@app.post("/webhook")
async def webhook(
    request: Request,
    file: UploadFile = File(None)
):
    payload = None
    filename = None

    # ---- Handle FILE upload ----
    if file:
        filename = f"{datetime.datetime.now().timestamp()}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(await file.read())

        payload = {
            "type": "file",
            "filename": file.filename
        }

    # ---- Handle JSON / other payloads ----
    else:
        try:
            payload = await request.json()
        except:
            raw = await request.body()
            payload = raw.decode(errors="ignore") if raw else None

    event = {
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": payload,
        "file": filename
    }

    events.insert(0, event)
    events[:] = events[:20]  # keep last 20 only

    print("📩 Webhook received:", event)

    return JSONResponse({"success": True})

@app.get("/download/{filename}")
async def download_file(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    return FileResponse(path, filename=filename)
