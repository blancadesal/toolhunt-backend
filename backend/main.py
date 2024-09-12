import logging
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from config import get_settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
settings = get_settings()

# Keep the SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory user storage
users = {}


class User(BaseModel):
    id: str
    username: str
    email: str


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.TOOLHUB_AUTH_URL,
    tokenUrl=settings.TOOLHUB_TOKEN_URL,
)

# In-memory storage for states (in production, use a proper database)
state_storage = {}


@app.get("/api/auth/login")
async def login(request: Request, redirect_after: str = "/profile"):
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    request.session["redirect_after"] = redirect_after
    logger.info(f"Storing state in session: {state}")
    logger.info(f"Storing redirect URL: {redirect_after}")

    params = {
        "client_id": settings.CLIENT_ID,
        "redirect_uri": settings.REDIRECT_URI,
        "state": state,
        "response_type": "code",
    }
    auth_url = f"{settings.TOOLHUB_AUTH_URL}?{urlencode(params)}"
    logger.info(f"Generated login URL: {auth_url}")

    return JSONResponse(content={"login_url": auth_url})


@app.post("/api/auth/callback")
async def oauth_callback(request: Request, response: Response):
    body = await request.json()
    code = body.get("code")
    received_state = body.get("state")

    logger.info(f"Received callback with code: {code} and state: {received_state}")

    stored_state = request.session.get("oauth_state")
    logger.info(f"Stored state in session: {stored_state}")

    if not stored_state or received_state != stored_state:
        logger.error(
            f"Invalid state. Received: {received_state}, Stored: {stored_state}"
        )
        raise HTTPException(status_code=400, detail="Invalid state")

    # Retrieve the stored redirect URL
    redirect_after = request.session.get("redirect_after", "/profile")

    # Remove the used state and redirect URL
    del request.session["oauth_state"]
    request.session.pop("redirect_after", None)

    token_response = await exchange_code_for_token(code)
    logger.info("Successfully exchanged code for token")

    user_data = await fetch_user_data(token_response["access_token"])
    logger.info(f"Fetched user data: {user_data}")

    db_user = create_or_update_user(user_data)
    access_token = create_access_token(data={"sub": db_user.id})

    logger.info(f"Created access token for user: {db_user.id}")

    # Set the access token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Set to True if using HTTPS
        samesite="lax",
        max_age=7200,  # 2 hours, adjust as needed
    )

    return {"user": db_user.dict(), "redirect_to": redirect_after}


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


async def fetch_user_data(access_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://toolhub-demo.wmcloud.org/api/user/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return response.json()


def create_or_update_user(user_data):
    user_id = str(user_data["id"])
    user = User(id=user_id, username=user_data["username"], email=user_data["email"])
    users[user_id] = user
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=120)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# Update this function
async def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = users.get(user_id)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


@app.get("/api/user")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


@app.get("/debug/session")
async def debug_session(request: Request):
    return JSONResponse(
        content={"session": dict(request.session), "cookies": request.cookies}
    )
