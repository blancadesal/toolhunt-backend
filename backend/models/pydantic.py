from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel


class ToolSchema(BaseModel):
    name: str
    title: str
    description: str
    url: str

    class Config:
        from_attributes = True


class ToolNamesResponse(BaseModel):
    all_titles: list[str]
    titles: dict[str, list[str]]


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
    encrypted_token: Optional[bytes] = None
    token_expires_at: Optional[datetime] = None


class ToolData(BaseModel):
    name: str
    title: str

    class Config:
        from_attributes = True


class UserData(BaseModel):
    id: str

    class Config:
        from_attributes = True


class TaskSubmission(BaseModel):
    tool: ToolData
    user: UserData
    completed_date: str
    value: Union[bool, str, list[str]]
    field: Optional[Literal["deprecated", "experimental"]] = None

    class Config:
        from_attributes = True
