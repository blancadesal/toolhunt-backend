from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


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


class TaskSubmission(BaseModel):
    tool_name: str
    tool_title: str
    completed_date: str
    value: Any
    field: str

    class Config:
        from_attributes = True


class ToolhubSubmission(BaseModel):
    wikidata_qid: Optional[str] = Field(None, pattern=r"^Q\d+$", max_length=32)
    audiences: Optional[list[str]] = Field(
        None, enum=["admin", "organizer", "editor", "reader", "researcher", "developer"]
    )
    content_types: Optional[list[str]] = Field(
        None,
        enum=[
            "article",
            "audio",
            "book",
            "data::bibliography",
            "data::category",
            "data::diff",
            "data::event",
            "data::geography",
            "data::linguistic",
            "data::page_metadata",
            "data::structured",
            "data::user",
            "discussion",
            "draft",
            "email",
            "image",
            "link",
            "list",
            "log",
            "map",
            "reference",
            "software",
            "template",
            "video",
            "watchlist",
            "webpage",
            "wikitext",
        ],
    )
    tasks: Optional[list[str]] = Field(
        None,
        enum=[
            "analysis",
            "annotating",
            "archiving",
            "categorizing",
            "citing",
            "communication",
            "converting",
            "creating",
            "deleting",
            "disambiguation",
            "downloading",
            "editing",
            "event_planning",
            "tools",
            "policy_violation",
            "spam",
            "vandalism",
            "ranking",
            "merging",
            "migrating",
            "patrolling",
            "project_management",
            "reading",
            "recommending",
            "translating",
            "uploading",
            "user_management",
            "warnings",
        ],
    )
    subject_domains: Optional[list[str]] = Field(
        None,
        enum=[
            "biography",
            "cultural",
            "education",
            "geography",
            "glam",
            "history",
            "language",
            "outreach",
            "science",
        ],
    )
    deprecated: Optional[bool] = None
    replaced_by: Optional[str] = Field(None, json_schema_extra={"format": "uri"})
    experimental: Optional[bool] = None
    for_wikis: Optional[list[str]] = Field(
        None,
        max_length=255,
        pattern=r"^(\*|(.*)?\.?(mediawiki|wiktionary|wiki(pedia|quote|books|source|news|versity|data|voyage|media))\.org)$",
    )
    icon: Optional[str] = Field(
        None,
        max_length=2047,
        pattern=r"^https://commons\.wikimedia\.org/wiki/File:.+\..+$",
    )
    available_ui_languages: Optional[list[str]] = Field(
        None, max_length=16, pattern=r"^(x-.*|[A-Za-z]{2,3}(-.*)?)$"
    )
    tool_type: Optional[str] = Field(
        None,
        enum=[
            "web app",
            "desktop app",
            "bot",
            "gadget",
            "user script",
            "command line tool",
            "coding framework",
            "lua module",
            "template",
            "other",
        ],
    )
    repository: Optional[str] = Field(None, max_length=2047)
    api_url: Optional[str] = Field(None, json_schema_extra={"format": "uri"})
    developer_docs_url: Optional[list[dict]] = None
    user_docs_url: Optional[list[dict]] = None
    feedback_url: Optional[list[dict]] = None
    privacy_policy_url: Optional[list[dict]] = None
    translate_url: Optional[str] = Field(None, json_schema_extra={"format": "uri"})
    bugtracker_url: Optional[str] = Field(None, json_schema_extra={"format": "uri"})
    comment: Optional[str] = Field(None, min_length=1)
