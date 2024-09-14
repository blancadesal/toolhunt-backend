import logging
import json
from pathlib import Path

from tortoise import Tortoise, run_async
from tortoise.exceptions import DoesNotExist, IntegrityError

from scripts.update_db import run_pipeline
from backend.db import TORTOISE_ORM
from backend.models.tortoise import CompletedTask, Field, Tool


logging.basicConfig(
    filename="db_update.log",
    format="%(asctime)s:%(levelname)s:%(message)s",
    filemode="w",
    encoding="utf-8",
    level=logging.INFO,
)

logger = logging.getLogger()


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "tests" / "fixtures"

FIELD_DATA_PATH = DATA_DIR / "field_data.json"
TOOL_DATA_PATH = DATA_DIR / "tool_data.json"
COMPLETED_TASK_DATA_PATH = DATA_DIR / "completed_task_data.json"


async def init():
    """Initialize the Tortoise ORM with the given configuration."""
    await Tortoise.init(config=TORTOISE_ORM)


async def insert_fields():
    """Insert field data from a JSON file into the database."""
    with FIELD_DATA_PATH.open("r") as f:
        fields_data = json.load(f)

    for field_data in fields_data:
        try:
            await Field.get_or_create(
                name=field_data["name"],
                defaults={
                    "description": field_data["description"],
                    "input_options": json.dumps(field_data.get("input_options", None)),
                    "pattern": field_data.get("pattern", None),
                },
            )
        except IntegrityError:
            logger.info(f"Field {field_data['name']} already exists.")


async def insert_tools():
    """Insert tool data from a JSON file and create tasks."""
    with TOOL_DATA_PATH.open("r") as f:
        tool_data = json.load(f)

    await run_pipeline(test_data=tool_data)


async def insert_completed_tasks():
    """Insert completed task data from a JSON file into the database."""
    await init()

    with COMPLETED_TASK_DATA_PATH.open("r") as f:
        completed_task_data = json.load(f)

    for task_data in completed_task_data:
        try:
            tool = await Tool.get(name=task_data["tool_name"])
            field = await Field.get(name=task_data["field"])
            await CompletedTask.get_or_create(
                tool=tool,
                tool_title=task_data["tool_title"],
                field=field,
                user=task_data["user"],
                defaults={"completed_date": task_data["completed_date"]},
            )
        except IntegrityError:
            logger.info(
                f"CompletedTask for tool {task_data['tool_name']} and field {task_data['field']} already exists."
            )
        except DoesNotExist:
            logger.info(
                f"Tool or Field does not exist for CompletedTask with tool {task_data['tool_name']} and field {task_data['field']}."
            )


async def seed():
    """Run the seeding process to insert fields, tools, and completed tasks."""
    await init()
    await insert_fields()
    await Tortoise.close_connections()

    await insert_tools()
    await Tortoise.close_connections()

    await insert_completed_tasks()
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(seed())
