from datetime import UTC, datetime, timedelta

import httpx
from fastapi import APIRouter, Cookie, Depends
from jose import JWTError, jwt
from tortoise.exceptions import DoesNotExist

from backend.config import get_settings
from backend.exceptions import (
    AuthenticationError,
    InvalidToken,
    OAuthError,
    UserCreationError,
)
from backend.models.pydantic import Token, User
from backend.models.tortoise import User as DBUser
from backend.security import (
    ALGORITHM,
    decrypt_token,
    encrypt_token,
    refresh_access_token,
)
from backend.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/user", tags=["users"])
settings = get_settings()


# helpers
async def fetch_user_data(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.TOOLHUB_API_BASE_URL}/user/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return response.json()


# Use this when posting annotation data to toolhub
async def get_user_token(user_id: str) -> Token:
    try:
        user = await DBUser.get(id=user_id)
        if user.encrypted_token is None:
            raise AuthenticationError("No token found for user")

        token = await decrypt_token(user.encrypted_token)

        # Check if the token is expired or about to expire (within 5 minutes)
        if datetime.now(UTC) >= user.token_expires_at - timedelta(minutes=5):
            # Refresh the token
            new_token = await refresh_access_token(token.refresh_token)

            # Update the user's token in the database
            user.encrypted_token = await encrypt_token(new_token)
            user.token_expires_at = datetime.now(UTC) + timedelta(
                seconds=new_token.expires_in
            )
            await user.save()

            return new_token

        return token
    except DoesNotExist:
        raise AuthenticationError("User not found")
    except InvalidToken as e:
        raise AuthenticationError(str(e))
    except OAuthError as e:
        raise AuthenticationError(f"Failed to refresh token: {str(e)}")


async def get_current_user(access_token: str = Cookie(None)) -> User:
    if not access_token:
        raise AuthenticationError("Not authenticated")

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid user ID")
        user = await DBUser.get(id=user_id)
        return User(id=user.id, username=user.username, email=user.email)
    except (JWTError, ValueError, DoesNotExist):
        raise AuthenticationError("Invalid token")


# endpoints
@router.get("")
async def read_user(current_user: User = Depends(get_current_user)):
    return current_user


# crud
async def create_or_update_user(user_data: dict, token_response: dict) -> User:
    user_id = str(user_data["id"])
    token = Token(**token_response)

    try:
        encrypted_token = await encrypt_token(token)
    except Exception as e:
        logger.error(f"Error encrypting token for user {user_id}: {str(e)}")
        encrypted_token = None

    try:
        user, _ = await DBUser.update_or_create(
            id=user_id,
            defaults={
                "username": user_data["username"],
                "email": user_data["email"],
                "encrypted_token": encrypted_token,
                "token_expires_at": datetime.now(UTC)
                + timedelta(seconds=token.expires_in),
            },
        )
    except Exception as e:
        logger.error(f"Error creating or updating user {user_id}: {str(e)}")
        raise UserCreationError(f"Failed to create or update user: {str(e)}")

    return User(id=user.id, username=user.username, email=user.email)
