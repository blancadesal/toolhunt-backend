import asyncio
import json
from datetime import UTC, datetime, timedelta

import httpx
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken as FernetInvalidToken
from jose import jwt

from backend.config import get_settings
from backend.models.pydantic import Token

ALGORITHM = "HS256"

settings = get_settings()

# Create a Fernet instance for token encryption
fernet = Fernet(settings.ENCRYPTION_KEY)


# Add this new exception
class InvalidToken(Exception):
    pass


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
