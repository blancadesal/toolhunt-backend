"""
This script updates the database with tool and task information from the Toolhub API.
It performs the following steps:
1. Extracts raw tool data from the Toolhub API.
2. Cleans and transforms the raw data.
3. Upserts tool records and removes stale tools.
4. Inserts or updates task records and removes stale tasks.
"""

import datetime
import logging
from dataclasses import dataclass

from tortoise import Tortoise, run_async
from tortoise.exceptions import DoesNotExist, IntegrityError

from backend.config import get_settings
from backend.db import TORTOISE_ORM
from backend.models.tortoise import Task, Tool
from backend.utils import ToolhubClient

settings = get_settings()

tools_endpoint = f"{settings.TOOLHUB_API_BASE_URL}/tools/"
toolhub_client = ToolhubClient(tools_endpoint)

logging.basicConfig(
    filename="db_update.log",
    format="%(asctime)s:%(levelname)s:%(message)s",
    filemode="w",
    encoding="utf-8",
    level=logging.INFO,
)

logger = logging.getLogger()


async def init():
    """Initialize the Tortoise ORM with the given configuration."""
    await Tortoise.init(config=TORTOISE_ORM)


# Functions
@dataclass
class ToolhuntTool:
    name: str
    title: str
    description: str
    url: str
    missing_annotations: set[str]
    deprecated: bool
    experimental: bool

    @property
    def is_completed(self):
        return len(self.missing_annotations) == 0


def is_deprecated(tool):
    return tool["annotations"]["deprecated"] is True or tool["deprecated"] is True


def is_experimental(tool):
    return tool["annotations"]["experimental"] is True or tool["experimental"] is True


def get_missing_annotations(tool_info, filter_by=settings.active_annotations):
    missing = set()

    for k, v in tool_info["annotations"].items():
        value = v or tool_info.get(k, v)
        if value in (None, [], "") and k in filter_by:
            missing.add(k)

    return missing


def clean_tool_data(tool_data):
    tools = []
    for tool in tool_data:
        missing_annotations = get_missing_annotations(tool)
        t = ToolhuntTool(
            name=tool["name"],
            title=tool["title"],
            description=tool["description"],
            url=tool["url"],
            missing_annotations=missing_annotations,
            deprecated=is_deprecated(tool),
            experimental=is_experimental(tool),
        )
        if not t.deprecated and not t.experimental and missing_annotations:
            tools.append(t)
        else:
            logger.info(
                f"Tool {t.name} is deprecated:{t.deprecated}, experimental:{t.experimental}, has {len(t.missing_annotations)} missing annotations. It will not be added to the database."
            )
    return tools


async def upsert_tool(tool):
    """Inserts a tool in the Tool table if it doesn't exist, and updates it if it does."""
    await Tool.update_or_create(
        defaults={
            "title": tool.title,
            "description": tool.description,
            "url": tool.url,
        },
        name=tool.name,
    )


async def remove_stale_tools(timestamp):
    """Removes expired tools from the Tool table."""
    logger.info(f"Removing stale tools with last_updated < {timestamp}")
    stale_tools = await Tool.filter(last_updated__lt=timestamp)
    for tool in stale_tools:
        logger.info(
            f"Removing tool: name={tool.name}, last_updated={tool.last_updated}"
        )
    await Tool.filter(last_updated__lt=timestamp).delete()


async def update_tool_table(tools, timestamp):
    """Upserts tool records and removes stale tools"""
    for tool in tools:
        await upsert_tool(tool)
    await remove_stale_tools(timestamp)


async def upsert_task(tool, field):
    """Inserts a task in the Task table if it doesn't exist or updates a timestamp."""
    await Task.update_or_create(
        tool=tool,
        field=field,
    )
    logger.info(f"Task created or already exists: tool_name={tool.name}, field={field}")


async def remove_stale_tasks(timestamp):
    """Removes expired tasks from the Task table."""
    logger.info(f"Removing stale tasks with last_updated < {timestamp}")
    stale_tasks = await Task.filter(last_updated__lt=timestamp).all()
    for task in stale_tasks:
        logger.info(
            f"Removing task: tool_name={task.tool.name}, field={task.field}, last_updated={task.last_updated}"
        )
    await Task.filter(last_updated__lt=timestamp).delete()


async def update_task_table(tools, timestamp):
    """Inserts task records"""
    for tool in tools:
        for field_name in tool.missing_annotations:
            try:
                tool_instance = await Tool.get(name=tool.name)
                await Task.update_or_create(
                    tool=tool_instance,
                    field=field_name,
                )
                logger.info(
                    f"Task created or updated: tool={tool.name}, field={field_name}"
                )
            except IntegrityError:
                logger.info(
                    f"Task for tool {tool.name} and field {field_name} already exists."
                )
            except DoesNotExist:
                logger.warning(
                    f"Tool does not exist for task with tool {tool.name} and field {field_name}."
                )

    await remove_stale_tasks(timestamp)


# Pipeline
# This will populate the db if empty, or update all tool and task records if not.
async def run_pipeline(test_data=None):
    try:
        # Extract
        logger.info("Starting database update...")
        await init()
        tools_raw_data = test_data if test_data else await toolhub_client.get_all()
        logger.info("Raw data received. Cleaning...")
        # Transform
        tools_clean_data = clean_tool_data(tools_raw_data)
        logger.info("Raw data cleaned. Updating tools..")
        # Load
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        await update_tool_table(tools_clean_data, timestamp)
        logger.info("Tools updated. Updating tasks...")
        await update_task_table(tools_clean_data, timestamp)
        logger.info("Tasks updated. Database update completed.")
    except Exception as err:
        logger.error(f"{err.args}")
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(run_pipeline())
