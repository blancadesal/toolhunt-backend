import random
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.expressions import Q

from backend.config import get_settings
from backend.models.pydantic import TaskSchema, ToolSchema
from backend.models.tortoise import CompletedTask, Task, User

router = APIRouter(prefix="/tasks", tags=["tasks"])

settings = get_settings()


# CRUD
async def get_tasks_from_db(
    field_names: Optional[str] = None,
    tool_names: Optional[str] = None,
    randomized: bool = True,
    limit: int = 20,
) -> List[TaskSchema]:
    query = Task.all().prefetch_related("tool")

    if field_names:
        field_name_list = [name.strip() for name in field_names.split(",")]
        query = query.filter(field__in=field_name_list)
    if tool_names:
        tool_name_list = [name.strip() for name in tool_names.split(",")]
        query = query.filter(tool__name__in=tool_name_list)

    if settings.ENVIRONMENT != "dev":
        # Filter out tasks attempted in the last 24 hours
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        query = query.filter(
            Q(last_attempted__isnull=True) | Q(last_attempted__lt=twenty_four_hours_ago)
        )

    tasks_from_db = await query
    if randomized:
        tasks = random.sample(tasks_from_db, min(len(tasks_from_db), limit))
    else:
        tasks = tasks_from_db

    # Update last_attempted and times_attempted fields
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
    query = Task.filter(id=task_id).prefetch_related("tool")
    task = await query.first()

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


# Updated Pydantic models for the request body
class ToolData(BaseModel):
    name: str
    title: str


class UserData(BaseModel):
    id: str


class TaskSubmission(BaseModel):
    tool: ToolData
    user: UserData
    completed_date: str
    value: str | list[str]


# Routes
@router.get(
    "",
    response_model=List[TaskSchema],
    responses={404: {"model": HTTPNotFoundError}},
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
    response_model=List[TaskSchema],
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
    task = await get_task_from_db(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/submit")
async def submit_task(task_id: int, submission: TaskSubmission):
    print(f"Received submission for task {task_id}: {submission}")  # Add this line
    try:
        # Fetch the task
        task = await Task.get_or_none(id=task_id).prefetch_related("tool")
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Verify that the tool data matches
        if (
            task.tool.name != submission.tool.name
            or task.tool.title != submission.tool.title
        ):
            raise HTTPException(status_code=400, detail="Tool data mismatch")

        # Fetch the user
        user = await User.get_or_none(id=submission.user.id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create a new CompletedTask entry
        completed_task = await CompletedTask.create(
            tool=task.tool,
            tool_title=task.tool.title,
            field=task.field,
            user=user.username,  # Use username instead of ID
            completed_date=submission.completed_date,
        )

        # We need to send the submission to Toolhub here, using a background task

        # We also need to delete the task from the task table

        return {
            "message": "Task submitted successfully",
            "completed_task_id": completed_task.id,
        }
    except Exception as e:
        print(f"Error processing submission: {str(e)}")  # Add this line
        raise HTTPException(status_code=422, detail=str(e))