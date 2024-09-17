from datetime import UTC, datetime, timedelta

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from tortoise.exceptions import DoesNotExist

from backend.config import get_settings
from backend.models.pydantic import Token, User
from backend.models.tortoise import User as DBUser
from backend.security import ALGORITHM, decrypt_token, encrypt_token

router = APIRouter(prefix="/user", tags=["users"])


# helpers
async def fetch_user_data(access_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.TOOLHUB_API_BASE_URL}user/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return response.json()


async def get_user_token(user_id: str) -> Token:
    try:
        user = await DBUser.get(id=user_id)
        return await decrypt_token(user.token)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")


async def get_current_user(access_token: str = Cookie(None)) -> User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid user ID")
        user = await DBUser.get(id=user_id)
        return User(id=user.id, username=user.username, email=user.email)
    except (JWTError, ValueError, DoesNotExist):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


# endpoints
@router.get("")
async def read_user(current_user: User = Depends(get_current_user)):
    return current_user


# crud
settings = get_settings()


async def create_or_update_user(user_data, token_response):
    user_id = str(user_data["id"])
    token = Token(**token_response)
    encrypted_token = await encrypt_token(token)

    user, _ = await DBUser.update_or_create(
        id=user_id,
        defaults={
            "username": user_data["username"],
            "email": user_data["email"],
            "token": encrypted_token,
            "token_expires_at": datetime.now(UTC) + timedelta(seconds=token.expires_in),
        },
    )

    return User(id=user.id, username=user.username, email=user.email)
