import httpx
from fastapi import HTTPException


class ToolhubClient:
    def __init__(self, endpoint):
        self.headers = {
            "User-Agent": "Toolhunt API",
            "Content-Type": "application/json",
        }
        self.endpoint = endpoint

    async def get(self, tool):
        """Get data on a single tool and return a list"""
        url = f"{self.endpoint}{tool}"
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
        url = f"{self.endpoint}"
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
        url = f"{self.endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                api_response = response.json()
                count = api_response["count"]
                return count
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def put(self, tool, data, token):
        """Take request data from the frontend and make a PUT request to Toolhub."""
        url = f"{self.endpoint}{tool}/annotations/"
        headers = dict(self.headers)
        headers.update({"Authorization": f"Bearer {token}"})
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(url, json=data, headers=headers)
                response.raise_for_status()
                api_response = response.json()
                return api_response
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))
