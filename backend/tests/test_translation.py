import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_translation_endpoint():
    response = client.post("/api/translate", json={
        "text": "Hello, world!",
        "target_language": "es"
    })
    assert response.status_code == 200
    assert "translated_text" in response.json()
    assert response.json()["translated_text"] == "¡Hola, mundo!"

def test_translation_with_empty_text():
    response = client.post("/api/translate", json={
        "text": "",
        "target_language": "es"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Text to translate cannot be empty."

def test_translation_with_invalid_language():
    response = client.post("/api/translate", json={
        "text": "Hello, world!",
        "target_language": "invalid_lang"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid target language specified."

def test_translation_editor_endpoint():
    response = client.post("/api/editor", json={
        "translated_text": "¡Hola, mundo!",
        "original_text": "Hello, world!"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Translation edited successfully."