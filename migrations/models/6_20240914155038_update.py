from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `completed_task` ADD `field_id` VARCHAR(80);
        ALTER TABLE `completed_task` ADD CONSTRAINT `fk_complete_field_13aeb922` FOREIGN KEY (`field_id`) REFERENCES `field` (`name`) ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `completed_task` DROP FOREIGN KEY `fk_complete_field_13aeb922`;
        ALTER TABLE `completed_task` DROP COLUMN `field_id`;"""
