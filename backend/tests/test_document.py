import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_document_upload():
    response = client.post("/api/document/upload", files={"file": ("test.pptx", open("test.pptx", "rb"))})
    assert response.status_code == 200
    assert "file_url" in response.json()

def test_document_translation():
    response = client.post("/api/translation", json={"document_id": "123", "target_language": "es"})
    assert response.status_code == 200
    assert "translated_text" in response.json()

def test_translation_editor():
    response = client.put("/api/editor", json={"document_id": "123", "edited_text": "Texto editado"})
    assert response.status_code == 200
    assert response.json()["message"] == "Translation updated successfully"

def test_invalid_document_upload():
    response = client.post("/api/document/upload", files={"file": ("test.txt", open("test.txt", "rb"))})
    assert response.status_code == 400
    assert "error" in response.json()