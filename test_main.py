import os
import pytest
from fastapi.testclient import TestClient
from main import app

# Setup environment for testing
os.environ["LOG_VIEW_TOKEN"] = "test-secret"

def test_view_no_token():
    client = TestClient(app)
    response = client.get("/view")
    # FastAPI returns 422 for missing required query params
    assert response.status_code == 422 

def test_view_wrong_token():
    client = TestClient(app)
    response = client.get("/view?token=wrong")
    assert response.status_code == 403

def test_view_success(tmp_path):
    client = TestClient(app)
    # Mock log directory
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "test.log"
    log_file.write_text('Hello <script>alert("xss")</script> world')
    
    # Patch LOG_DIR in main
    import main
    main.LOG_DIR = str(log_dir)
    
    # Ensure SECRET_TOKEN is set in environment for main to read
    os.environ["LOG_VIEW_TOKEN"] = "test-secret"
    
    response = client.get("/view?token=test-secret")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "test.log" in response.text
    # Check for HTML escaped content
    assert "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;" in response.text
