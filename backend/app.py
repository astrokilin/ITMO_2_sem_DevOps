import os
import threading
import psutil
import time

from http.server import HTTPServer
from prometheus_client import Gauge, MetricsHandler
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from bleach import clean
from aiogram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None

ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'u', 'a', 'br', 'p']

cpu_usage_gauge = Gauge('app_cpu_usage_percent', 'CPU usage percent of app')

def sanitize_html(content: str) -> str:
    return clean(content, tags=ALLOWED_TAGS, strip=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def update_resource_metrics():
    process = psutil.Process()
    while True:
        cpu = process.cpu_percent(interval=1)
        cpu_usage_gauge.set(cpu)
        time.sleep(5)

class PrometheusServer:
    def __init__(self, port=8000):
        self.httpd = HTTPServer(('', port), MetricsHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True

    def start(self):
        self.thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join()

# --- Модели ---
class NoteIn(BaseModel):
    title: str
    content: str

class NoteCreate(BaseModel):
    title: str
    content: str
    send_to_telegram: bool = False

# --- MongoDB ---
@app.on_event("startup")
async def startup_db_client():
    client = AsyncIOMotorClient(os.environ["MONGO_URI"])
    app.db = client.notesdb
    app.prom = PrometheusServer(int(os.environ.get("PROM_PORT", 8000)))
    app.prom.start()
    threading.Thread(target=update_resource_metrics, daemon=True).start()

@app.on_event("shutdown")
async def shutdown_db_client():
    app.db.client.close()
    app.prom.stop()

# --- CRUD API ---
@app.get("/api/notes")
async def get_notes():
    result = await app.db.notes.find().to_list(100)
    return [
        {"_id": str(note["_id"]), "title": note["title"], "content": note["content"]}
        for note in result
    ]

@app.post("/api/notes")
async def create_note(note: NoteCreate):
    title = sanitize_html(note.title)
    content = sanitize_html(note.content)
    doc = {"title": title, "content": content}
    result = await app.db.notes.insert_one(doc)
    new_note = {"_id": str(result.inserted_id), "title": title, "content": content}

    if note.send_to_telegram and bot and TELEGRAM_CHAT_ID:
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"New note!\n\n*{title}*\n{content}",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error while sending to Telegram: {e}", flush=True)

    return new_note

@app.put("/api/notes/{id}")
async def update_note(id: str, note: NoteIn):
    title = sanitize_html(note.title)
    content = sanitize_html(note.content)
    updated = await app.db.notes.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"title": title, "content": content}}
    )
    if updated.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"_id": id, "title": title, "content": content}

@app.delete("/api/notes/{id}")
async def delete_note(id: str):
    deleted = await app.db.notes.delete_one({"_id": ObjectId(id)})
    if deleted.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"status": "deleted", "id": id}
