import json
import random
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.expressions import F, Q
from tortoise.transactions import atomic

from backend.api.user import get_current_user, get_user_token
from backend.config import get_settings
from backend.models.pydantic import (
    TaskSchema,
    TaskSubmission,
    ToolhubSubmission,
    ToolSchema,
)
from backend.models.tortoise import CompletedTask, Task, Tool, User
from backend.utils import get_logger

router = APIRouter(prefix="/tasks", tags=["tasks"])
settings = get_settings()
logger = get_logger(__name__)


# CRUD functions
async def get_tasks_from_db(
    field_names: Optional[str] = None,
    tool_names: Optional[str] = None,
    randomized: bool = True,
    limit: int = 10,
) -> list[TaskSchema]:
    if not field_names and not tool_names:
        query = Task.filter(
            tool__deprecated=False,
            tool__experimental=False,
        ).prefetch_related("tool")

        if settings.ENVIRONMENT != "dev":
            twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
            query = query.filter(
                Q(last_attempted__isnull=True)
                | Q(last_attempted__lt=twenty_four_hours_ago)
            )

        tasks_from_db = await query.values(
            "id",
            "field",
            "last_attempted",
            "times_attempted",
            "tool__name",
            "tool__title",
            "tool__description",
            "tool__url",
        )

        if randomized:
            tasks_from_db = random.sample(tasks_from_db, min(len(tasks_from_db), limit))
        else:
            tasks_from_db = tasks_from_db[:limit]

        task_ids = [task["id"] for task in tasks_from_db]
        await Task.filter(id__in=task_ids).update(
            last_attempted=datetime.now(), times_attempted=F("times_attempted") + 1
        )

        return [
            TaskSchema(
                id=task["id"],
                tool=ToolSchema(
                    name=task["tool__name"],
                    title=task["tool__title"],
                    description=task["tool__description"],
                    url=task["tool__url"],
                ),
                field=task["field"],
            )
            for task in tasks_from_db
        ]

    query = Task.all().prefetch_related("tool")
    query = query.filter(tool__deprecated=False, tool__experimental=False)

    if field_names:
        query = query.filter(
            field__in=[name.strip() for name in field_names.split(",")]
        )
    if tool_names:
        query = query.filter(
            tool__name__in=[name.strip() for name in tool_names.split(",")]
        )

    if settings.ENVIRONMENT != "dev":
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        query = query.filter(
            Q(last_attempted__isnull=True) | Q(last_attempted__lt=twenty_four_hours_ago)
        )

    tasks_from_db = await query
    tasks = (
        random.sample(tasks_from_db, min(len(tasks_from_db), limit))
        if randomized
        else tasks_from_db
    )

    for task in tasks:
        task.last_attempted = datetime.now()
        task.times_attempted += 1
        await task.save(update_fields=["last_attempted", "times_attempted"])

    return [
        TaskSchema(
            id=task.id,
            tool=ToolSchema(
                name=task.tool.name,
                title=task.tool.title,
                description=task.tool.description,
                url=task.tool.url,
            ),
            field=task.field,
        )
        for task in tasks
    ]


async def get_task_from_db(task_id: int) -> TaskSchema:
    task = await Task.filter(id=task_id).prefetch_related("tool").first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskSchema(
        id=task.id,
        tool=ToolSchema(
            name=task.tool.name,
            title=task.tool.title,
            description=task.tool.description,
            url=task.tool.url,
        ),
        field=task.field,
    )


# Routes
@router.get(
    "", response_model=list[TaskSchema], responses={404: {"model": HTTPNotFoundError}}
)
async def get_tasks(
    field_names: Optional[str] = Query(
        None, description="Comma-separated list of field names"
    ),
    tool_names: Optional[str] = Query(
        None, description="Comma-separated list of tool names"
    ),
    limit: int = Query(5, description="Number of tasks to return", ge=1, le=20),
):
    tasks = await get_tasks_from_db(
        field_names=field_names, tool_names=tool_names, randomized=True, limit=limit
    )
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks


@router.get(
    "/{tool_name}",
    response_model=list[TaskSchema],
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_tasks_by_tool_name(tool_name: str):
    tasks = await get_tasks_from_db(tool_names=tool_name)
    if not tasks:
        raise HTTPException(
            status_code=404, detail="No tasks found for the specified tool name"
        )
    return tasks


@router.get(
    "/{task_id}",
    response_model=TaskSchema,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_task(task_id: int):
    return await get_task_from_db(task_id)


@router.post("/{task_id}/submit")
@atomic()
async def submit_task(
    task_id: int,
    submission: TaskSubmission,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    logger.info(f"Received submission for task {task_id}: {submission}")
    try:
        is_report = submission.field in ["deprecated", "experimental"]

        # Check if the tool still exists
        tool = await Tool.get_or_none(name=submission.tool.name)
        if not tool:
            logger.warning(
                f"Tool {submission.tool.name} not found in database. It may have been removed during a sync."
            )

        # Create CompletedTask entry regardless of whether the tool still exists
        completed_task = await CompletedTask.create(
            tool_name=submission.tool.name,
            tool_title=submission.tool.title,
            field=submission.field,
            user=current_user.username,
            completed_date=submission.completed_date,
        )
        logger.info(f"Created CompletedTask: {completed_task}")

        if is_report and tool:
            await Tool.filter(name=submission.tool.name).update(
                **{submission.field: submission.value}
            )
            logger.info(f"Updated Tool: {submission.tool.name}")

        # Prepare and submit data to Toolhub as a background task
        toolhub_data = await prepare_toolhub_submission(submission)
        background_tasks.add_task(
            submit_to_toolhub, submission.tool.name, toolhub_data, current_user.id
        )

        # Attempt to delete the task if it exists
        deleted_count = await Task.filter(id=task_id).delete()
        if deleted_count:
            logger.info(f"Deleted task: {task_id}")
        else:
            logger.info(
                f"Task {task_id} not found for deletion. It may have already been removed."
            )

        return {
            "message": "Task submission recorded successfully",
            "completed_task_id": completed_task.id,
        }

    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}", exc_info=True)
        logger.error(f"Submission data: {submission}")
        logger.error(f"Task ID: {task_id}")
        raise HTTPException(
            status_code=422, detail=f"Error processing submission: {str(e)}"
        )


def format_url_list(value):
    return [{"language": item["language"], "url": item["url"]} for item in value]


async def prepare_toolhub_submission(submission: TaskSubmission) -> ToolhubSubmission:
    toolhub_data = ToolhubSubmission(
        comment=f"Updated {submission.field} field using Toolhunt"
    )

    special_fields = {
        "user_docs_url",
        "developer_docs_url",
        "feedback_url",
        "privacy_policy_url",
    }
    valid_fields = set(ToolhubSubmission.model_fields.keys())

    if submission.field in valid_fields:
        if submission.field in special_fields:
            value = format_url_list(submission.value)
        else:
            value = submission.value
        setattr(toolhub_data, submission.field, value)
    else:
        logger.warning(f"Unhandled field: {submission.field}")

    return toolhub_data


async def submit_to_toolhub(tool_name: str, toolhub_data: ToolhubSubmission, user_id: str):
    try:
        token = await get_user_token(user_id)
        logger.info(f"Token: {token}")
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }

        # Update the URL to use the correct structure
        url = f"{settings.TOOLHUB_API_BASE_URL}/tools/{tool_name}/annotations/"

        # Prepare the JSON data with double-quoted property names
        json_data = json.dumps(toolhub_data.model_dump(exclude_unset=True), ensure_ascii=False)

        # Log the request details
        logger.info(f"Preparing Toolhub request: PUT {url}")
        logger.info(f"Toolhub request data: {json_data}")

        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                content=json_data,
                headers=headers
            )
            response.raise_for_status()
        logger.info(f"Successfully submitted data to Toolhub for tool: {tool_name}")
        logger.info(f"Toolhub response: {response.text}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred while submitting to Toolhub: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Error submitting to Toolhub: {e.response.text}")
    except Exception as e:
        logger.error(f"Error submitting data to Toolhub for tool {tool_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error while submitting to Toolhub: {str(e)}")
