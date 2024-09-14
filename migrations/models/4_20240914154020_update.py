from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `task` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `last_attempted` DATETIME(6),
    `times_attempted` INT NOT NULL  DEFAULT 0,
    `last_updated` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `field_id` VARCHAR(80) NOT NULL,
    `tool_id` VARCHAR(255) NOT NULL,
    UNIQUE KEY `uid_task_tool_id_98996c` (`tool_id`, `field_id`),
    CONSTRAINT `fk_task_field_00bca60c` FOREIGN KEY (`field_id`) REFERENCES `field` (`name`) ON DELETE CASCADE,
    CONSTRAINT `fk_task_tool_622d4aad` FOREIGN KEY (`tool_id`) REFERENCES `tool` (`name`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `task`;"""
