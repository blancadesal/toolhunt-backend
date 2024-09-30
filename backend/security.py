import asyncio
import json
from datetime import UTC, datetime, timedelta
from typing import Dict
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken as FernetInvalidToken
from fastapi import Request, Response
from jose import jwt

from backend.config import get_settings
from backend.exceptions import InvalidStateError, InvalidToken, OAuthError
from backend.models.pydantic import Token
from backend.utils import get_logger

logger = get_logger(__name__)

ALGORITHM = "HS256"
settings = get_settings()
fernet = Fernet(settings.ENCRYPTION_KEY)


# JWT Access Token functions
def create_access_token(subject: str, expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def set_access_token_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# OAuth related functions
def generate_oauth_url(state: str) -> str:
    params: Dict[str, str] = {
        "client_id": settings.CLIENT_ID,
        "redirect_uri": settings.REDIRECT_URI,
        "state": state,
        "response_type": "code",
    }
    return f"{settings.TOOLHUB_AUTH_URL}?{urlencode(params)}"


async def validate_oauth_state(request: Request, received_state: str) -> None:
    stored_state = request.session.get("oauth_state")
    if not stored_state or received_state != stored_state:
        logger.error(
            f"Invalid state. Received: {received_state}, Stored: {stored_state}"
        )
        raise InvalidStateError()


async def exchange_code_for_token(code: str) -> Dict[str, str]:
    try:
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
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"OAuth token exchange error: {str(e)}")
        raise OAuthError("Failed to exchange code for token")


# Token encryption/decryption
async def encrypt_token(token: Token) -> bytes:
    token_str = json.dumps(token.dict())
    return await asyncio.to_thread(fernet.encrypt, token_str.encode())


async def decrypt_token(encrypted_token: bytes) -> Token:
    try:
        decrypted = await asyncio.to_thread(fernet.decrypt, encrypted_token)
        token_dict = json.loads(decrypted.decode())
        return Token(**token_dict)
    except FernetInvalidToken:
        raise InvalidToken("The token is invalid or has been tampered with")
    except json.JSONDecodeError:
        raise InvalidToken("The decrypted token is not valid JSON")


# Utility function
def get_and_clear_redirect_url(request: Request) -> str:
    redirect_after = request.session.get("redirect_after", "/profile")
    del request.session["oauth_state"]
    request.session.pop("redirect_after", None)
    return redirect_after


async def refresh_access_token(refresh_token: str) -> Token:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.TOOLHUB_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                },
            )
        response.raise_for_status()
        return Token(**response.json())
    except httpx.HTTPError as e:
        logger.error(f"OAuth token refresh error: {str(e)}")
        raise OAuthError("Failed to refresh access token")
