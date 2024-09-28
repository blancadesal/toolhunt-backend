from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `completed_task` ADD UNIQUE INDEX `uid_completed_t_tool_na_818efc` (`tool_name`, `field`, `user`, `completed_date`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `completed_task` DROP INDEX `uid_completed_t_tool_na_818efc`;"""
