from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Создаем экземпляр FastAPI
app = FastAPI()

# Модель для заметки
class Note(BaseModel):
    title: str
    content: str

# Модель для заметки с идентификатором (ObjectId)
class NoteInDB(Note):
    id: str

# Настроим подключение к MongoDB
@app.on_event("startup")
async def startup_db_client():
    client = AsyncIOMotorClient(os.environ["MONGO_URI"])
    app.db = client.notesdb  # Подключаемся к базе данных 'notesdb'

@app.on_event("shutdown")
async def shutdown_db_client():
    app.db.client.close()  # Закрываем соединение с базой данных

# Инициализация шаблонов
templates = Jinja2Templates(directory="templates")

# Функция для получения коллекции заметок
def get_notes_collection():
    return app.db.notes  # Получаем коллекцию заметок из базы данных

# Главная страница - отображение всех заметок
@app.get("/", response_class=HTMLResponse)
async def read_notes(request: Request):
    notes_collection = get_notes_collection()
    notes = []
    async for note in notes_collection.find():
        note["_id"] = str(note["_id"])  # Преобразуем ObjectId в строку
        notes.append(note)
    return templates.TemplateResponse("index.html", {"request": request, "notes": notes})

# Страница добавления новой заметки
@app.get("/add", response_class=HTMLResponse)
async def add_note_form(request: Request):
    return templates.TemplateResponse("add_note.html", {"request": request})

@app.post("/add")
async def add_note(request: Request, note: Note):
    notes_collection = get_notes_collection()
    result = await notes_collection.insert_one(note.dict())
    return {"message": "Note added successfully"}

# Страница редактирования заметки
@app.get("/edit/{note_id}", response_class=HTMLResponse)
async def edit_note_form(request: Request, note_id: str):
    notes_collection = get_notes_collection()
    note = await notes_collection.find_one({"_id": ObjectId(note_id)})
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note["_id"] = str(note["_id"])  # Преобразуем ObjectId в строку
    return templates.TemplateResponse("edit_note.html", {"request": request, "note": note})

@app.post("/edit/{note_id}")
async def edit_note(note_id: str, note: Note):
    notes_collection = get_notes_collection()
    updated_note = await notes_collection.find_one_and_update(
        {"_id": ObjectId(note_id)},
        {"$set": note.dict()},
        return_document=True,
    )
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    updated_note["_id"] = str(updated_note["_id"])  # Преобразуем ObjectId в строку
    return {"message": "Note updated successfully"}

# Страница удаления заметки
@app.get("/delete/{note_id}")
async def delete_note(note_id: str):
    notes_collection = get_notes_collection()
    result = await notes_collection.delete_one({"_id": ObjectId(note_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}
