import httpx
from fastapi import Cookie, HTTPException, status
from datetime import UTC, datetime, timedelta
from jose import jwt, JWTError


from config import get_settings
from models.pydantic import User


settings = get_settings()

ALGORITHM = "HS256"

# In-memory user storage
users = {}

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id or user_id not in users:
            raise ValueError("Invalid user ID")
        return users[user_id]
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def create_or_update_user(user_data):
    user_id = str(user_data["id"])
    user = User(id=user_id, username=user_data["username"], email=user_data["email"])
    users[user_id] = user
    return user


async def fetch_user_data(access_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.TOOLHUB_API_BASE_URL}user/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return response.json()