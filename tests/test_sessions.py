def test_create_session(client):
    response = client.post("/sessions", json={"session_user": "abc"})

    assert response.status_code == 201
    body = response.json()
    assert body["session_id"] == 2
    assert body["session_user"] == "abc"
    assert body["created_at"]


def test_create_session_normalizes_username(client):
    response = client.post("/sessions", json={"session_user": "  Alice  "})

    assert response.status_code == 201
    assert response.json()["session_user"] == "alice"


def test_create_session_starts_with_empty_history(client):
    session_id = client.post("/sessions", json={"session_user": "abc"}).json()[
        "session_id"
    ]

    response = client.get(f"/sessions/{session_id}/messages")

    assert response.status_code == 200
    assert response.json() == []


def test_create_session_rejects_empty_username(client):
    response = client.post("/sessions", json={"session_user": "   "})

    assert response.status_code == 422


def test_session_ids_increment(client):
    first = client.post("/sessions", json={"session_user": "abc"}).json()
    second = client.post("/sessions", json={"session_user": "def"}).json()

    assert (first["session_id"], second["session_id"]) == (2, 3)
