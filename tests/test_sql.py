from fastapi.testclient import TestClient
from nl2sql.main import app

client = TestClient(app)


def test_select_and_refuse_write():
    payload = client.post("/generate", json={"question": 'errors by service'}).json()
    assert "FROM errors" in payload["sql"]
    assert payload["read_only"] is True
    assert client.post("/generate", json={"question": "delete old rows"}).status_code == 422
