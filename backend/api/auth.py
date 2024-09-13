import logging
import secrets
from datetime import timedelta
from urllib.parse import urlencode

from config import get_settings
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from security import (
    create_access_token,
    create_or_update_user,
    exchange_code_for_token,
    fetch_user_data,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.get("/login")
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

    return RedirectResponse(url=auth_url)


@router.post("/callback")
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

    db_user = await create_or_update_user(user_data, token_response)
    access_token = create_access_token(
        subject=str(db_user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    logger.info(f"Created access token for user: {db_user.id}")

    # Set the access token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Set to True if using HTTPS
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return {"user": db_user.dict(exclude={"token"}), "redirect_to": redirect_after}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}
