from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `task` DROP FOREIGN KEY `fk_task_field_00bca60c`;
        ALTER TABLE `completed_task` DROP FOREIGN KEY `fk_complete_field_13aeb922`;
        ALTER TABLE `completed_task` ADD `field` VARCHAR(80) NOT NULL;
        ALTER TABLE `completed_task` DROP COLUMN `field_id`;
        ALTER TABLE `task` RENAME COLUMN `field_id` TO `field`;
        DROP TABLE IF EXISTS `field`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `completed_task` ADD `field_id` VARCHAR(80);
        ALTER TABLE `task` RENAME COLUMN `field` TO `field_id`;
        ALTER TABLE `completed_task` ADD CONSTRAINT `fk_complete_field_13aeb922` FOREIGN KEY (`field_id`) REFERENCES `field` (`name`) ON DELETE SET NULL;
        ALTER TABLE `task` ADD CONSTRAINT `fk_task_field_00bca60c` FOREIGN KEY (`field_id`) REFERENCES `field` (`name`) ON DELETE CASCADE;"""
