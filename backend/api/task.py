import logging
import random
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import OperationalError
from tortoise.expressions import Q, F
from tortoise.transactions import atomic

from backend.config import get_settings
from backend.models.pydantic import TaskSchema, TaskSubmission, ToolSchema
from backend.models.tortoise import CompletedTask, Task, Tool, User

router = APIRouter(prefix="/tasks", tags=["tasks"])
settings = get_settings()
logger = logging.getLogger(__name__)


# CRUD functions
async def get_tasks_from_db(
    field_names: Optional[str] = None,
    tool_names: Optional[str] = None,
    randomized: bool = True,
    limit: int = 10,
) -> list[TaskSchema]:
    # For unfiltered queries, use a more efficient approach
    if not field_names and not tool_names:
        query = Task.filter(
            tool__deprecated=False,
            tool__experimental=False,
        ).prefetch_related("tool")

        if settings.ENVIRONMENT != "dev":
            twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
            query = query.filter(
                Q(last_attempted__isnull=True) | Q(last_attempted__lt=twenty_four_hours_ago)
            )

        # Use `values()` to fetch only necessary fields
        tasks_from_db = await query.values(
            "id", "field", "last_attempted", "times_attempted",
            "tool__name", "tool__title", "tool__description", "tool__url"
        )

        # Randomize and limit the results in Python
        if randomized:
            tasks_from_db = random.sample(tasks_from_db, min(len(tasks_from_db), limit))
        else:
            tasks_from_db = tasks_from_db[:limit]

        # Update last_attempted and times_attempted
        task_ids = [task["id"] for task in tasks_from_db]
        await Task.filter(id__in=task_ids).update(
            last_attempted=datetime.now(),
            times_attempted=F("times_attempted") + 1
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

    # For filtered queries, use the existing approach
    query = Task.all().prefetch_related("tool")

    # Add filter for non-deprecated and non-experimental tools
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
):
    tasks = await get_tasks_from_db(
        field_names=field_names, tool_names=tool_names, randomized=True, limit=10
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
async def submit_task(task_id: int, submission: TaskSubmission):
    logger.info(f"Received submission for task {task_id}: {submission}")
    try:
        task = await Task.get_or_none(id=task_id).prefetch_related("tool")
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if (
            task.tool.name != submission.tool.name
            or task.tool.title != submission.tool.title
        ):
            raise HTTPException(status_code=400, detail="Tool data mismatch")

        user = await User.get_or_none(id=submission.user.id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        is_report = submission.field in ["deprecated", "experimental"]

        completed_task = await CompletedTask.create(
            tool=task.tool,
            tool_title=task.tool.title,
            field=submission.field if is_report else task.field,
            user=user.username,
            completed_date=submission.completed_date,
        )
        logger.info(f"Created CompletedTask: {completed_task}")

        if is_report:
            await Tool.filter(name=task.tool.name).update(
                **{submission.field: submission.value}
            )
            logger.info(f"Updated Tool: {task.tool.name}")
        else:
            await Task.filter(id=task_id).delete()
            logger.info(f"Deleted task: {task_id}")

        return {
            "message": "Task submitted successfully",
            "completed_task_id": completed_task.id,
        }

    except OperationalError as e:
        logger.error(f"Database operational error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}", exc_info=True)
        logger.error(f"Submission data: {submission}")
        logger.error(f"Task ID: {task_id}")
        raise HTTPException(
            status_code=422, detail=f"Error processing submission: {str(e)}"
        )
