import secrets
from datetime import timedelta

from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from backend.api.user import create_or_update_user, fetch_user_data
from backend.config import get_settings
from backend.exceptions import InternalServerError, InvalidStateError, OAuthError
from backend.security import (
    create_access_token,
    exchange_code_for_token,
    generate_oauth_url,
    get_and_clear_redirect_url,
    set_access_token_cookie,
    validate_oauth_state,
)
from backend.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"], include_in_schema=False)
settings = get_settings()


@router.get("/login")
async def login(request: Request, redirect_after: str = "/profile") -> RedirectResponse:
    try:
        state = secrets.token_urlsafe(32)
        request.session["oauth_state"] = state
        request.session["redirect_after"] = redirect_after

        auth_url = generate_oauth_url(state)
        logger.info(f"Initiating login process for redirect to: {redirect_after}")

        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Error during login process: {str(e)}")
        raise InternalServerError("Internal server error during login process")


@router.post("/callback")
async def oauth_callback(request: Request, response: Response):
    body = await request.json()
    code = body.get("code")
    received_state = body.get("state")

    try:
        await validate_oauth_state(request, received_state)
        redirect_after = get_and_clear_redirect_url(request)

        token_response = await exchange_code_for_token(code)
        user_data = await fetch_user_data(token_response["access_token"])

        db_user = await create_or_update_user(user_data, token_response)

        access_token = create_access_token(
            subject=str(db_user.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        set_access_token_cookie(response, access_token)

        user = db_user.dict(exclude={"token", "token_expires_at"})
        return {"user": user, "redirect_to": redirect_after}

    except (InvalidStateError, OAuthError) as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in oauth callback: {str(e)}")
        raise InternalServerError()


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}
