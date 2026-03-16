import os
import pytest
from fastapi.testclient import TestClient
from main import app

def test_view_no_token():
    client = TestClient(app)
    response = client.get("/view")
    assert response.status_code == 422 

def test_view_wrong_token():
    client = TestClient(app)
    os.environ["LOG_VIEW_TOKEN"] = "secret"
    response = client.get("/view?token=wrong")
    assert response.status_code == 403
