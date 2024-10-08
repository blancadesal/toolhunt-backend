import random
from datetime import datetime, timedelta
from typing import Optional

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
from backend.utils import ToolhubClient, get_logger, prepare_toolhub_submission

router = APIRouter(prefix="/tasks", tags=["tasks"])
settings = get_settings()
logger = get_logger(__name__)
toolhub_client = ToolhubClient(settings.TOOLHUB_API_BASE_URL)


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


@router.post("/{task_id}")
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

        tool = await Tool.get_or_none(name=submission.tool_name)
        if not tool:
            logger.warning(
                f"Tool {submission.tool_name} not found in database. It may have been removed during a sync."
            )

        completed_task = await CompletedTask.create(
            tool_name=submission.tool_name,
            tool_title=submission.tool_title,
            field=submission.field,
            user=current_user.username,
            completed_date=submission.completed_date,
        )
        logger.info(f"Created CompletedTask: {completed_task}")

        if is_report and tool:
            await Tool.filter(name=submission.tool_name).update(
                **{submission.field: submission.value}
            )
            logger.info(f"Updated Tool: {submission.tool_name}")

        toolhub_data = await prepare_toolhub_submission(submission)
        background_tasks.add_task(
            submit_to_toolhub,
            submission.tool_name,
            toolhub_data,
            current_user.id,
        )

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

        if settings.ENVIRONMENT == "prod" and tool_names is not None:
            minutes_ago = datetime.now() - timedelta(minutes=20)
            query = query.filter(
                Q(last_attempted__isnull=True) | Q(last_attempted__lt=minutes_ago)
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


async def submit_to_toolhub(
    tool_name: str, toolhub_data: ToolhubSubmission, user_id: str
):
    try:
        token = await get_user_token(user_id)
        logger.info(f"Preparing Toolhub request for tool: {tool_name}")
        logger.info(f"Toolhub request data: {toolhub_data}")

        response = await toolhub_client.put_annotation(
            tool_name, toolhub_data, token.access_token
        )
        logger.info(f"Successfully submitted data to Toolhub for tool: {tool_name}")
        logger.info(f"Toolhub response: {response}")
    except HTTPException as e:
        logger.error(
            f"Error submitting data to Toolhub for tool {tool_name}: {e.detail}"
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error submitting data to Toolhub for tool {tool_name}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while submitting to Toolhub: {str(e)}",
        )
