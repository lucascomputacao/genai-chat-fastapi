from datetime import UTC, datetime
from typing import TypedDict

from app.schemas import Role


class SessionRecord(TypedDict):
    session_id: int
    session_user: str
    created_at: datetime


class MessageRecord(TypedDict):
    role: Role
    content: str


session_store: list[SessionRecord] = []
chat_store: dict[int, list[MessageRecord]] = {}


def reset() -> None:
    session_store.clear()
    chat_store.clear()
    session_store.append(
        {
            "session_id": 1,
            "session_user": "abc",
            "created_at": datetime(2025, 6, 30, 16, 0, 0, tzinfo=UTC),
        }
    )
    chat_store[1] = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
