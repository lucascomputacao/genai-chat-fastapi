def test_add_message(client):
    response = client.post(
        "/sessions/1/messages", json={"role": "user", "content": "What is AI?"}
    )

    assert response.status_code == 201
    assert response.json() == {"role": "user", "content": "What is AI?"}
    assert client.get("/sessions/1/messages").json()[-1]["content"] == "What is AI?"


def test_add_message_unknown_session(client):
    response = client.post(
        "/sessions/99/messages", json={"role": "user", "content": "Hello"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session 99 not found"


def test_add_message_invalid_role(client):
    response = client.post(
        "/sessions/1/messages", json={"role": "system", "content": "Hello"}
    )

    assert response.status_code == 422


def test_get_messages(client):
    response = client.get("/sessions/1/messages")

    assert response.status_code == 200
    assert response.json() == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]


def test_get_messages_filtered_by_role(client):
    response = client.get("/sessions/1/messages", params={"role": "assistant"})

    assert response.status_code == 200
    assert response.json() == [{"role": "assistant", "content": "Hi there!"}]


def test_get_messages_invalid_role_filter(client):
    response = client.get("/sessions/1/messages", params={"role": "system"})

    assert response.status_code == 422


def test_get_messages_unknown_session(client):
    response = client.get("/sessions/99/messages")

    assert response.status_code == 404
