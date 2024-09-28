from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `completed_task` DROP FOREIGN KEY `fk_complete_tool_cd7f7189`;
        ALTER TABLE `completed_task` ADD `tool_name` VARCHAR(255) NOT NULL;
        ALTER TABLE `completed_task` DROP COLUMN `tool_id`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `completed_task` ADD `tool_id` VARCHAR(255);
        ALTER TABLE `completed_task` DROP COLUMN `tool_name`;
        ALTER TABLE `completed_task` ADD CONSTRAINT `fk_complete_tool_cd7f7189` FOREIGN KEY (`tool_id`) REFERENCES `tool` (`name`) ON DELETE SET NULL;"""
