from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from tortoise.functions import Count

from backend.models.tortoise import CompletedTask, User

router = APIRouter(prefix="/metrics", tags=["metrics"])


class ContributionData(BaseModel):
    rank: int
    username: str
    contributions: int


class ContributionsResponse(BaseModel):
    contributions: list[ContributionData]


@router.get("/contributions", response_model=ContributionsResponse)
async def get_contribution_metrics(
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


class UserContribution(BaseModel):
    date: datetime
    tool_title: str
    field: str


class UserContributionsResponse(BaseModel):
    contributions: list[UserContribution]
    total_contributions: int


@router.get("/contributions/{username}", response_model=UserContributionsResponse)
async def get_user_contributions(
    username: str,
    limit: Optional[int] = Query(10, ge=1, le=100, description="Maximum number of results to return")
):
    # First, check if the user exists
    user_exists = await User.filter(username=username).exists()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the total number of contributions
    total_contributions = await CompletedTask.filter(user=username).count()

    # Get the limited list of contributions
    contributions = await CompletedTask.filter(user=username) \
        .order_by("-completed_date") \
        .limit(limit) \
        .values("completed_date", "tool_title", "field")

    return UserContributionsResponse(
        contributions=[
            UserContribution(
                date=contrib["completed_date"],
                tool_title=contrib["tool_title"],
                field=contrib["field"]
            ) for contrib in contributions
        ],
        total_contributions=total_contributions
    )