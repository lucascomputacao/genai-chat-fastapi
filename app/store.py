from datetime import datetime, timezone
from typing import Any

session_store: list[dict[str, Any]] = []
chat_store: dict[int, list[dict[str, str]]] = {}


def reset() -> None:
    session_store.clear()
    chat_store.clear()
    session_store.append(
        {
            "session_id": 1,
            "session_user": "abc",
            "created_at": datetime(2025, 6, 30, 16, 0, 0, tzinfo=timezone.utc),
        }
    )
    chat_store[1] = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]


reset()
