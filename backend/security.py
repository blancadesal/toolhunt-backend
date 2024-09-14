import asyncio
import base64
from datetime import UTC, datetime, timedelta

import httpx
from cryptography.fernet import Fernet
from fastapi import Cookie, HTTPException, status
from jose import JWTError, jwt

from backend.config import get_settings
from backend.models.pydantic import Token, User, UserInDB

settings = get_settings()

ALGORITHM = "HS256"

# In-memory user storage
users = {}

# Create a Fernet instance for token encryption
fernet = Fernet(settings.ENCRYPTION_KEY)


async def exchange_code_for_token(code):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.TOOLHUB_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.REDIRECT_URI,
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
            },
        )
    return response.json()


def create_access_token(subject: str, expires_delta: timedelta):
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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


async def encrypt_token(token: Token) -> bytes:
    token_str = base64.b64encode(str(token.dict()).encode())
    return await asyncio.to_thread(fernet.encrypt, token_str)


async def decrypt_token(encrypted_token: bytes) -> Token:
    decrypted = await asyncio.to_thread(fernet.decrypt, encrypted_token)
    token_dict = eval(base64.b64decode(decrypted).decode())
    return Token(**token_dict)


async def create_or_update_user(user_data, token_response):
    user_id = str(user_data["id"])
    user = User(id=user_id, username=user_data["username"], email=user_data["email"])

    # Create Token object
    token = Token(**token_response)

    # Encrypt the token asynchronously
    encrypted_token = await encrypt_token(token)

    # Create UserInDB object
    user_in_db = UserInDB(**user.dict(), encrypted_token=encrypted_token)

    # Store user asynchronously
    await asyncio.to_thread(users.update, {user_id: user_in_db})

    return user


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
