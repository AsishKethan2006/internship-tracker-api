from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_list_application():
    original_database = main.DATABASE

    with TemporaryDirectory() as temp_directory:
        main.DATABASE = Path(temp_directory) / "test.db"
        main.init_db()

        try:
            create_response = client.post(
                "/applications",
                json={"company": "Example Labs", "role": "Backend Intern", "status": "applied", "notes": "Submitted through campus portal"},
            )
            assert create_response.status_code == 201
            assert create_response.json()["company"] == "Example Labs"

            list_response = client.get("/applications")
            assert list_response.status_code == 200
            assert len(list_response.json()) == 1
            assert list_response.json()[0]["status"] == "applied"
        finally:
            main.DATABASE = original_database