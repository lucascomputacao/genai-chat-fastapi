from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Path, Query, status

from app.schemas import Message, Role, SessionCreate, SessionOut
from app.store import chat_store, session_store

app = FastAPI(title="GenAI Chat App")


def get_session_messages(session_id: int) -> list[dict[str, str]]:
    if session_id not in chat_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return chat_store[session_id]


@app.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreate) -> SessionOut:
    session = {
        "session_id": len(session_store) + 1,
        "session_user": payload.session_user,
        "created_at": datetime.now(timezone.utc),
    }
    session_store.append(session)
    chat_store[session["session_id"]] = []
    return SessionOut(**session)


@app.post(
    "/sessions/{session_id}/messages",
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
)
def add_message(message: Message, session_id: int = Path(ge=1)) -> Message:
    messages = get_session_messages(session_id)
    messages.append(message.model_dump())
    return message


@app.get("/sessions/{session_id}/messages", response_model=list[Message])
def list_messages(
    session_id: int = Path(ge=1),
    role: Role | None = Query(default=None),
) -> list[dict[str, str]]:
    messages = get_session_messages(session_id)
    if role is None:
        return messages
    return [message for message in messages if message["role"] == role]
