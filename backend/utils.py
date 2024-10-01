import logging

import httpx
from fastapi import HTTPException

from backend.models.pydantic import TaskSubmission, ToolhubSubmission


def setup_logging(log_level: str = "INFO") -> None:
    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


logger = get_logger(__name__)


class ToolhubClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Toolhunt API",
            "Content-Type": "application/json",
        }

    async def get(self, tool_name):
        """Get data on a single tool and return a list"""
        url = f"{self.base_url}/tools/{tool_name}"
        tool_data = []
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                api_response = response.json()
                tool_data.append(api_response)
                return tool_data
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all(self):
        """Get data on all Toolhub tools."""
        url = f"{self.base_url}/tools/"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                api_response = response.json()
                tool_data = api_response["results"]
                while api_response["next"]:
                    response = await client.get(
                        api_response["next"], headers=self.headers
                    )
                    api_response = response.json()
                    tool_data.extend(api_response["results"])
                return tool_data
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_count(self):
        """Get number of tools on Toolhub."""
        url = f"{self.base_url}/tools/"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                api_response = response.json()
                count = api_response["count"]
                return count
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def put_annotation(self, tool_name: str, data: ToolhubSubmission, token: str):
        """Submit an annotation for a tool to Toolhub."""
        url = f"{self.base_url}/tools/{tool_name}/annotations/"
        headers = dict(self.headers)
        headers.update({"Authorization": f"Bearer {token}"})
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url, json=data.model_dump(exclude_unset=True), headers=headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Toolhub API error: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500, detail=f"Error communicating with Toolhub: {str(e)}"
            )


def format_url_list(value):
    return [{"language": item["language"], "url": item["url"]} for item in value]


async def prepare_toolhub_submission(submission: TaskSubmission) -> ToolhubSubmission:
    toolhub_data = ToolhubSubmission(
        comment=f"Updated {submission.field} field using Toolhunt"
    )

    special_fields = {
        "user_docs_url",
        "developer_docs_url",
        "feedback_url",
        "privacy_policy_url",
    }
    valid_fields = set(ToolhubSubmission.model_fields.keys())

    if submission.field in valid_fields:
        if submission.field in special_fields:
            value = format_url_list(submission.value)
        else:
            value = submission.value
        setattr(toolhub_data, submission.field, value)
    else:
        logger.warning(f"Unhandled field: {submission.field}")

    return toolhub_data
