from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ToolSchema(BaseModel):
    name: str
    title: str
    description: str
    url: str

    class Config:
        from_attributes = True


class TaskSchema(BaseModel):
    id: int
    tool: ToolSchema
    field: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class User(BaseModel):
    id: str
    username: str
    email: str
    token: Optional[Token] = None
    token_expires_at: Optional[datetime] = None


class UserInDB(User):
    encrypted_token: Optional[bytes] = None
