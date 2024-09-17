import json
import logging
from datetime import datetime
from pathlib import Path

from tortoise import Tortoise, run_async
from tortoise.exceptions import IntegrityError

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

    inserted_count = 0
    skipped_count = 0

    for task_data in completed_task_data:
        try:
            tool = await Tool.get(name=task_data["tool_name"])
            completed_date = datetime.fromisoformat(
                task_data["completed_date"].replace("Z", "+00:00")
            )

            _, created = await CompletedTask.get_or_create(
                tool=tool,
                tool_title=task_data["tool_title"],
                field=task_data["field"],
                user=task_data["user"],
                completed_date=completed_date,
            )

            if created:
                inserted_count += 1
                logger.info(
                    f"Inserted task: {task_data['tool_name']} - {task_data['field']} by {task_data['user']}"
                )
            else:
                skipped_count += 1
                logger.info(
                    f"Skipped existing task: {task_data['tool_name']} - {task_data['field']} by {task_data['user']}"
                )

        except Tool.DoesNotExist:
            logger.error(f"Tool not found: {task_data['tool_name']}")
        except IntegrityError as e:
            logger.error(f"IntegrityError inserting task: {str(e)}")
            logger.error(f"Task data: {task_data}")
        except Exception as e:
            logger.error(f"Error inserting completed task: {str(e)}")
            logger.error(f"Task data: {task_data}")

    logger.info(
        f"Insertion complete. Inserted: {inserted_count}, Skipped: {skipped_count}"
    )


async def seed():
    """Run the seeding process to insert tools and completed tasks."""
    await init()
    await insert_tools()
    await Tortoise.close_connections()

    await insert_completed_tasks()
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(seed())
