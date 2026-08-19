from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Role = Literal["user", "assistant"]


class SessionCreate(BaseModel):
    session_user: str

    @field_validator("session_user")
    @classmethod
    def normalize_user(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("session_user must not be empty")
        return normalized


class SessionOut(BaseModel):
    session_id: int
    session_user: str
    created_at: datetime


class Message(BaseModel):
    role: Role
    content: str = Field(min_length=1)
