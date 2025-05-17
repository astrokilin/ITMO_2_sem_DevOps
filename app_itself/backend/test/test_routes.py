from fastapi.testclient import TestClient
from bson import ObjectId

def test_serve_index(client: TestClient):
    with client:
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

def test_get_notes_empty(client: TestClient):
    with client:
        response = client.get("/notes")
        assert response.status_code == 200
        assert response.text == ""

def test_create_note(client: TestClient):
    with client:
        response = client.post("/notes", data={"title": "Test creating", "content": "Content"})
        assert response.status_code == 200
        assert "Test creating" in response.text
        assert "Content" in response.text

def test_update_note(client: TestClient):
    with client:
        response = client.post("/notes", data={"title": "Test update", "content": "Content"})
        assert response.status_code == 200
        note_id = response.text.split("id=\"")[1].split("\"",1)[0][5:]
        response = client.put(f"/notes/{note_id}", data={"title": "Test updated", "content": "Updated"})
        assert response.status_code == 200
        assert "updated" in response.text

def test_delete_note(client: TestClient):
    with client:
        response = client.post("/notes", data={"title": "Test delete", "content": "Content"})
        assert response.status_code == 200
        note_id = response.text.split("id=\"")[1].split("\"",1)[0][5:]
        response = client.delete(f"/notes/{note_id}")
        assert response.status_code == 200
