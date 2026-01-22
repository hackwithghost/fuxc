from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os
import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

events = []


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "events": events}
    )


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    file: UploadFile = File(None)
):
    payload = None
    saved_file = None

    # ---------- FILE UPLOAD ----------
    if file is not None:
        filename = f"{int(datetime.datetime.now().timestamp())}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, filename)

        with open(path, "wb") as f:
            f.write(await file.read())

        payload = {
            "type": "file",
            "original_name": file.filename,
            "saved_as": filename
        }
        saved_file = filename

    # ---------- JSON / OTHER ----------
    else:
        content_type = request.headers.get("content-type", "")

        try:
            if "application/json" in content_type:
                payload = await request.json()
            else:
                raw = await request.body()
                payload = raw.decode("utf-8", errors="ignore") if raw else None
        except Exception as e:
            payload = {"error": str(e)}

    event = {
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": payload,
        "file": saved_file
    }

    events.insert(0, event)
    events[:] = events[:20]

    print("📩 Webhook received:", event)

    return JSONResponse({"success": True})


@app.get("/download/{filename}")
async def download_file(filename: str):
    return FileResponse(os.path.join(UPLOAD_DIR, filename), filename=filename)


@app.get("/webhook")
async def webhook_info():
    return {
        "status": "Webhook active",
        "supports": ["JSON", "multipart/form-data"]
    }
