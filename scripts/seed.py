import json
import logging
from pathlib import Path

from tortoise import Tortoise, run_async

from backend.db import TORTOISE_ORM
from backend.models.tortoise import CompletedTask, Tool
from scripts.update_db import run_pipeline

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

TOOL_DATA_PATH = DATA_DIR / "tool_data.json"
COMPLETED_TASK_DATA_PATH = DATA_DIR / "completed_task_data.json"


async def init():
    """Initialize the Tortoise ORM with the given configuration."""
    await Tortoise.init(config=TORTOISE_ORM)


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
            await CompletedTask.get_or_create(
                tool=tool,
                tool_title=task_data["tool_title"],
                field=task_data["field"],
                user=task_data["user"],
                defaults={"completed_date": task_data["completed_date"]},
            )
        except Exception as e:
            logger.error(f"Error inserting completed task: {str(e)}")
            logger.error(f"Task data: {task_data}")


async def seed():
    """Run the seeding process to insert tools and completed tasks."""
    await init()
    await insert_tools()
    await Tortoise.close_connections()

    await insert_completed_tasks()
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(seed())
