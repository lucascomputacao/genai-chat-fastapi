from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query, status

from app.schemas import Message, Role, SessionCreate, SessionOut
from app.store import MessageRecord, SessionRecord, chat_store, reset, session_store


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    reset()
    yield


app = FastAPI(title="GenAI Chat App", lifespan=lifespan)

SessionId = Annotated[int, Path(ge=1)]


def get_session_messages(session_id: int) -> list[MessageRecord]:
    if session_id not in chat_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return chat_store[session_id]


@app.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(payload: SessionCreate) -> SessionOut:
    session: SessionRecord = {
        "session_id": len(session_store) + 1,
        "session_user": payload.session_user,
        "created_at": datetime.now(UTC),
    }
    session_store.append(session)
    chat_store[session["session_id"]] = []
    return SessionOut(**session)


@app.post(
    "/sessions/{session_id}/messages",
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
)
async def add_message(session_id: SessionId, message: Message) -> Message:
    messages = get_session_messages(session_id)
    messages.append({"role": message.role, "content": message.content})
    return message


@app.get("/sessions/{session_id}/messages", response_model=list[Message])
async def list_messages(
    session_id: SessionId,
    role: Annotated[Role | None, Query()] = None,
) -> list[MessageRecord]:
    messages = get_session_messages(session_id)
    if role is None:
        return messages
    return [message for message in messages if message["role"] == role]
