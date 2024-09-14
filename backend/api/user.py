import asyncio

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, status
from jose import JWTError, jwt

from backend.config import get_settings
from backend.models.pydantic import Token, User, UserInDB
from backend.security import ALGORITHM, decrypt_token, encrypt_token

router = APIRouter(prefix="/user", tags=["user"])

# In-memory user storage
users = {}

# helpers
async def fetch_user_data(access_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.TOOLHUB_API_BASE_URL}user/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return response.json()


async def get_user_token(user_id: str) -> Token:
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    user_in_db = users[user_id]
    return await decrypt_token(user_in_db.encrypted_token)


async def get_current_user(access_token: str = Cookie(None)) -> User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id or user_id not in users:
            raise ValueError("Invalid user ID")
        user_in_db = users[user_id]
        return User(**user_in_db.dict(exclude={"encrypted_token"}))
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


# endpoints
@router.get("/")
async def read_user(current_user: User = Depends(get_current_user)):
    return current_user


# crud
settings = get_settings()

async def create_or_update_user(user_data, token_response):
    user_id = str(user_data["id"])
    user = User(id=user_id, username=user_data["username"], email=user_data["email"])
    token = Token(**token_response)
    encrypted_token = await encrypt_token(token)
    user_in_db = UserInDB(**user.dict(), encrypted_token=encrypted_token)
    await asyncio.to_thread(users.update, {user_id: user_in_db})

    return user
