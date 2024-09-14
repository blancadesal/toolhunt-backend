import random
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.expressions import Q

from backend.config import get_settings
from backend.models.pydantic import FieldSchema, TaskSchema, ToolSchema
from backend.models.tortoise import Task

router = APIRouter(prefix="/tasks")

settings = get_settings()


# CRUD
async def get_tasks_from_db(
    field_names: Optional[str] = None, tool_name: Optional[str] = None
) -> List[TaskSchema]:
    query = Task.all().prefetch_related("tool", "field")

    if field_names:
        field_name_list = [name.strip() for name in field_names.split(",")]
        query = query.filter(field__name__in=field_name_list)
    if tool_name:
        query = query.filter(tool__name=tool_name)

    if settings.ENVIRONMENT != "dev":
        # Filter out tasks attempted in the last 24 hours
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        query = query.filter(
            Q(last_attempted__isnull=True) | Q(last_attempted__lt=twenty_four_hours_ago)
        )

    tasks = await query
    random_tasks = random.sample(tasks, min(len(tasks), 10))

    # Update last_attempted and times_attempted fields
    for task in random_tasks:
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
            field=FieldSchema(
                name=task.field.name,
                description=task.field.description,
                field_type=task.field.field_type_enum,
                input_options=task.field.input_options,
                pattern=task.field.pattern,
            ),
        )
        for task in random_tasks
    ]


async def get_task_from_db(task_id: int) -> TaskSchema:
    query = Task.filter(id=task_id).prefetch_related("tool", "field")
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
        field=FieldSchema(
            name=task.field.name,
            description=task.field.description,
            field_type=task.field.field_type_enum,
            input_options=task.field.input_options,
            pattern=task.field.pattern,
        ),
    )


# Routes
@router.get(
    "/",
    response_model=List[TaskSchema],
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_tasks(
    field_names: Optional[str] = Query(
        None, description="Comma-separated list of field names"
    ),
    tool_name: Optional[str] = Query(None),
):
    tasks = await get_tasks_from_db(field_names=field_names, tool_name=tool_name)
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
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
