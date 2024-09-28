import secrets
from datetime import timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from backend.api.user import create_or_update_user, fetch_user_data
from backend.config import get_settings
from backend.models.tortoise import User as DBUser
from backend.security import create_access_token, decrypt_token, exchange_code_for_token
from backend.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"], include_in_schema=False)
settings = get_settings()


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
    logger.info(f"Token response: {token_response}")

    user_data = await fetch_user_data(token_response["access_token"])
    logger.info(f"Fetched user data: {user_data}")

    try:
        db_user = await create_or_update_user(user_data, token_response)
    except Exception as e:
        logger.error(f"Error creating or updating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing user data")

    # Test token retrieval and decryption
    try:
        stored_user = await DBUser.get(id=db_user.id)
        if stored_user.encrypted_token:
            decrypted_token = await decrypt_token(stored_user.encrypted_token)
            logger.info(
                f"Successfully retrieved and decrypted token for user {db_user.username}"
            )
            logger.info(f"Decrypted token: {decrypted_token}")
        else:
            logger.warning(f"No token stored for user {db_user.username}")
    except Exception as e:
        logger.error(f"Error retrieving or decrypting token: {str(e)}")

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
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    user = db_user.dict(exclude={"token", "token_expires_at"})

    return {"user": user, "redirect_to": redirect_after}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}
