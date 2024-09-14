from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField


class FieldType(str, Enum):
    STRING = "string"
    MULTI_SELECT = "multi_select"
    SINGLE_SELECT = "single_select"
    BOOLEAN = "boolean"
    URI = "uri"


class FieldSchema(BaseModel):
    name: str = PydanticField(..., max_length=80)
    description: str = PydanticField(..., max_length=2047)
    field_type: FieldType
    input_options: Optional[dict] = None
    pattern: Optional[str] = PydanticField(None, max_length=320)

    class Config:
        use_enum_values = True


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
    field: FieldSchema

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
