import os

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from bleach import clean

ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'u', 'a', 'br', 'p']

def sanitize_html(content: str) -> str:
    return clean(content, tags=ALLOWED_TAGS, strip=True)

app = FastAPI()
templates = Jinja2Templates(directory="/frontend/templates")

# connect MongoDB
@app.on_event("startup")
async def startup_db_client():
    client = AsyncIOMotorClient(os.environ["MONGO_URI"])
    app.db = client.notesdb

@app.on_event("shutdown")
async def shutdown_db_client():
    app.db.client.close()


# main page
@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/notes", response_class=HTMLResponse)
async def get_notes(request: Request):
    result = await app.db.notes.find().to_list(100)
    rendered = ""
    print("getting nodes...")
    for note in result:
        rendered += templates.get_template("note_item.html").render(
            request=request, id=str(note["_id"]), title=note["title"], content=note["content"]
        )
    return HTMLResponse(content=rendered)

@app.post("/notes", response_class=HTMLResponse)
async def create_note(request: Request, title: str = Form(...), content: str = Form(...)):
    title = sanitize_html(title)
    content = sanitize_html(content)
    print(f"adding note {title} with {content}")
    doc = {"title": title, "content": content}
    result = await app.db.notes.insert_one(doc)
    html = templates.get_template("note_item.html").render(
        request=request, id=str(result.inserted_id), title=title, content=content
    )
    return HTMLResponse(content=html)

@app.get("/notes/{id}/edit", response_class=HTMLResponse)
async def editable_note(id: str, title: str = Form(...), content: str = Form(...), request: Request = None):
    print(f"updating note {id} with {title} and {content}")
    title = sanitize_html(title)
    content = sanitize_html(content)
    updated = await app.db.notes.update_one({"_id": ObjectId(id)}, {"$set": {"title": title, "content": content}})
    if updated.matched_count == 0:
        raise HTTPException(status_code=404)
    html = templates.get_template("note_item.html").render(
        request=request, id=id, title=title, content=content
    )
    return HTMLResponse(content=html)

@app.put("/notes/{id}", response_class=HTMLResponse)
async def update_note(id: str, title: str = Form(...), content: str = Form(...), request: Request = None):
    print(f"updating note {id} with {title} and {content}")
    title = sanitize_html(title)
    content = sanitize_html(content)
    updated = await app.db.notes.update_one({"_id": ObjectId(id)}, {"$set": {"title": title, "content": content}})
    if updated.matched_count == 0:
        raise HTTPException(status_code=404)
    html = templates.get_template("note_item.html").render(
        request=request, id=id, title=title, content=content
    )
    return HTMLResponse(content=html)

@app.delete("/notes/{id}", response_class=HTMLResponse)
async def delete_note(id: str):
    deleted = await app.db.notes.delete_one({"_id": ObjectId(id)})
    if deleted.deleted_count == 0:
        raise HTTPException(status_code=404)
    return HTMLResponse(content="")
