# GenAI Chat App — FastAPI Backend

Backend service for managing chat sessions and messages of a GenAI chat app.

Storage is **in-memory** (plain Python data structures) — no database required. State
lives in the process and resets on every restart.

## Requirements

- Python 3.11+

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

```bash
uvicorn app.main:app --reload
```

Interactive docs: http://127.0.0.1:8000/docs

## Tests

```bash
pytest
```

Lint and type checks:

```bash
ruff check app tests
mypy
```

## Project structure

```
pyproject.toml   Dependencies and ruff/mypy/pytest configuration
app/
  main.py        FastAPI app and endpoints
  schemas.py     Pydantic request/response models and validation
  store.py       In-memory session_store / chat_store
tests/
  conftest.py        TestClient fixture, re-seeding the store per test
  test_sessions.py   Session creation tests
  test_messages.py   Message add/list/filter tests
```

## Storage

The store is seeded on application startup with one sample session, so the API is
usable right away:

```python
session_store = [
    {"session_id": 1, "session_user": "abc", "created_at": datetime(2025, 6, 30, 16, 0, tzinfo=utc)}
]

chat_store = {
    1: [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
}
```

## API

### `POST /sessions` — create a new chat session

Request:

```json
{ "session_user": "abc" }
```

Response `201 Created`:

```json
{
  "session_id": 2,
  "session_user": "abc",
  "created_at": "2025-06-30T16:05:00Z"
}
```

Behavior:

- Username is normalized: trailing/leading spaces removed and lowercased.
- Empty (or whitespace-only) usernames are rejected with `422`.
- `session_id` is assigned as `len(session_store) + 1`.
- `created_at` is the current UTC timestamp.
- An empty message list is initialized at `chat_store[session_id]`.

### `POST /sessions/{session_id}/messages` — add a message

Request:

```json
{ "role": "user", "content": "What is AI?" }
```

Response `201 Created` echoes the stored message.

Behavior:

- `404` if the session does not exist.
- `422` if `role` is not `user` or `assistant`, or if `content` is empty.

### `GET /sessions/{session_id}/messages` — list messages

Response `200 OK`:

```json
[
  { "role": "user", "content": "Hello" },
  { "role": "assistant", "content": "Hi there!" }
]
```

Behavior:

- Returns the full chat history for the session.
- Optional `role` query param filters the history, e.g.
  `GET /sessions/1/messages?role=assistant`.
- `404` if the session does not exist; `422` for an invalid `role` value.

## Example requests

```bash
curl -X POST http://127.0.0.1:8000/sessions \
  -H 'content-type: application/json' \
  -d '{"session_user": "  ABC  "}'

curl -X POST http://127.0.0.1:8000/sessions/2/messages \
  -H 'content-type: application/json' \
  -d '{"role": "user", "content": "What is AI?"}'

curl 'http://127.0.0.1:8000/sessions/1/messages?role=assistant'
```

## Notes

- Validation errors return `422` because they are handled by Pydantic models
  (`Literal["user", "assistant"]` for roles, a field validator for usernames),
  which keeps the endpoint bodies free of manual checks.
- Missing sessions return `404` via a single `get_session_messages` helper shared
  by both message endpoints.
- Endpoints are `async def` so each one runs to completion on the event loop.
  With sync handlers FastAPI would run them in a thread pool, where the
  `len(session_store) + 1` id assignment could race between concurrent requests.
- The stores are typed with `TypedDict`, which keeps them plain Python data
  structures while still passing `mypy --strict`.
