from fastapi.testclient import TestClient
from bson import ObjectId

def test_get_notes_empty(client: TestClient):
    with client:
        response = client.get("/api/notes")
        assert response.status_code == 200

def test_create_note(client: TestClient):
    with client:
        response = client.post("/api/notes", json={"title": "Test creating", "content": "Content", "send_to_telegram": False})
        assert response.status_code == 200

def test_update_note(client: TestClient):
    with client:
        response = client.post("/api/notes", json={"title": "Test update", "content": "Content"})
        assert response.status_code == 200
        data = response.json()
        note_id = data["_id"]
        response = client.put(f"/api/notes/{note_id}", json={"title": "Test updated", "content": "Updated"})
        assert response.status_code == 200

def test_delete_note(client: TestClient):
    with client:
        response = client.post("/api/notes", json={"title": "Test delete", "content": "Content"})
        assert response.status_code == 200
        data = response.json()
        note_id = data["_id"]
        response = client.delete(f"/api/notes/{note_id}")
        assert response.status_code == 200
