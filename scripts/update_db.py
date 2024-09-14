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

from tortoise import run_async
from tortoise.exceptions import DoesNotExist, IntegrityError

from backend.config import get_settings
from backend.models.tortoise import Field, Task, Tool
from backend.utils import ToolhubClient

settings = get_settings()

tools_endpoint = f"{settings.TOOLHUB_API_BASE_URL}/tools"
toolhub_client = ToolhubClient(tools_endpoint)

logging.basicConfig(
    filename="db_update.log",
    format="%(asctime)s:%(levelname)s:%(message)s",
    filemode="w",
    encoding="utf-8",
    level=logging.INFO,
)

logger = logging.getLogger()

# Parameters
ANNOTATIONS = {
    "audiences",
    "content_types",
    "tasks",
    "subject_domains",
    "wikidata_qid",
    "icon",
    "tool_type",
    "repository",
    "api_url",
    "translate_url",
    "bugtracker_url",
}


# Functions
@dataclass
class ToolhuntTool:
    name: str
    title: str
    description: str
    url: str
    missing_annotations: set[str]
    deprecated: bool

    @property
    def is_completed(self):
        return len(self.missing_annotations) == 0


def is_deprecated(tool):
    return tool["deprecated"] or tool["annotations"]["deprecated"]


def get_missing_annotations(tool_info, filter_by=ANNOTATIONS):
    missing = set()

    for k, v in tool_info["annotations"].items():
        value = v or tool_info.get(k, v)
        if value in (None, [], "") and k in filter_by:
            missing.add(k)

    return missing


def clean_tool_data(tool_data):
    tools = []
    for tool in tool_data:
        t = ToolhuntTool(
            name=tool["name"],
            title=tool["title"],
            description=tool["description"],
            url=tool["url"],
            missing_annotations=get_missing_annotations(tool),
            deprecated=is_deprecated(tool),
        )
        if not t.deprecated:  # and not t.is_completed:
            tools.append(t)
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
        tool_name=tool,
        field_name=field,
    )
    logger.info(
        f"Task created or already exists: tool_name={tool.name}, field_name={field.name}"
    )


async def remove_stale_tasks(timestamp):
    """Removes expired tasks from the Task table."""
    logger.info(f"Removing stale tasks with last_updated < {timestamp}")
    stale_tasks = await Task.filter(last_updated__lt=timestamp).all()
    for task in stale_tasks:
        logger.info(
            f"Removing task: tool_name={task.tool_name_id}, field_name={task.field_name_id}, last_updated={task.last_updated}"
        )
    await Task.filter(last_updated__lt=timestamp).delete()


async def update_task_table(tools, timestamp):
    """Inserts task records"""
    for tool in tools:
        for field_name in tool.missing_annotations:
            try:
                tool_instance = await Tool.get(name=tool.name)
                field_instance = await Field.get(name=field_name)
                await Task.update_or_create(
                    tool=tool_instance,
                    field=field_instance,
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
                    f"Tool or Field does not exist for task with tool {tool.name} and field {field_name}."
                )

    await remove_stale_tasks(timestamp)


# Pipeline
# This will populate the db if empty, or update all tool and task records if not.
async def run_pipeline(test_data=None):
    try:
        # Extract
        logger.info("Starting database update...")
        tools_raw_data = test_data if test_data else toolhub_client.get_all()
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


if __name__ == "__main__":
    run_async(run_pipeline())
