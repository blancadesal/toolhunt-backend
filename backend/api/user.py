from datetime import UTC, datetime, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, Query
from jose import JWTError, jwt
from tortoise.exceptions import DoesNotExist
from tortoise.functions import Count

from backend.config import get_settings
from backend.exceptions import (
    AuthenticationError,
    InvalidToken,
    OAuthError,
    UserCreationError,
)
from backend.models.pydantic import (
    ContributionData,
    ContributionsResponse,
    Token,
    User,
    UserContribution,
    UserContributionsResponse,
)
from backend.models.tortoise import CompletedTask
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


@router.get("")
async def read_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/contributions/leaderboard", response_model=ContributionsResponse)
async def get_leaderboard_metrics(
    days: Optional[int] = Query(
        None, description="Number of days to consider for the leaderboard"
    ),
    limit: Optional[int] = Query(
        None, ge=1, description="Maximum number of results to return"
    ),
):
    query = CompletedTask.all()

    if days:
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(completed_date__gte=start_date)

    contributions = (
        await query.annotate(contribution_count=Count("id"))
        .group_by("user")
        .order_by("-contribution_count")
        .values("user", "contribution_count")
    )

    ranked_contributions = []
    current_rank = 1
    previous_count = None
    rank_increment = 0

    for contribution in contributions:
        if (
            previous_count is not None
            and contribution["contribution_count"] < previous_count
        ):
            current_rank += rank_increment
            rank_increment = 1
        else:
            rank_increment += 1

        ranked_contributions.append(
            ContributionData(
                rank=current_rank,
                username=contribution["user"],
                contributions=contribution["contribution_count"],
            )
        )

        previous_count = contribution["contribution_count"]

        if limit and len(ranked_contributions) >= limit:
            break

    return ContributionsResponse(contributions=ranked_contributions)


async def get_contributions(
    username: Optional[str] = None, limit: Optional[int] = None
) -> UserContributionsResponse:
    query = CompletedTask.all().order_by("-completed_date")

    if username:
        query = query.filter(user=username)

    if limit:
        query = query.limit(limit)

    contributions = await query.values("user", "completed_date", "tool_title", "field")
    total_contributions = await query.count()

    return UserContributionsResponse(
        contributions=[
            UserContribution(
                username=contrib["user"],
                date=contrib["completed_date"],
                tool_title=contrib["tool_title"],
                field=contrib["field"],
            )
            for contrib in contributions
        ],
        total_contributions=total_contributions,
    )


@router.get("/contributions/{username}", response_model=UserContributionsResponse)
async def get_user_contributions(
    username: str,
    limit: Optional[int] = Query(
        None, ge=1, description="Maximum number of results to return (optional)"
    ),
):
    user_exists = await DBUser.filter(username=username).exists()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    result = await get_contributions(username=username, limit=limit)
    if not result.contributions:
        raise HTTPException(
            status_code=404, detail="No contributions found for this user"
        )

    return result


@router.get("/contributions", response_model=UserContributionsResponse)
async def get_all_contributions(
    limit: Optional[int] = Query(
        None, ge=1, description="Maximum number of contributions to return (optional)"
    ),
):
    return await get_contributions(limit=limit)


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


async def fetch_user_data(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.TOOLHUB_API_BASE_URL}/user/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return response.json()


async def get_user_token(user_id: str) -> Token:
    try:
        user = await DBUser.get(id=user_id)
        if user.encrypted_token is None:
            raise AuthenticationError("No token found for user")

        token = await decrypt_token(user.encrypted_token)

        if datetime.now(UTC) >= user.token_expires_at - timedelta(minutes=5):
            new_token = await refresh_access_token(token.refresh_token)

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
