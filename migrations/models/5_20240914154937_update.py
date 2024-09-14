from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `completed_task` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `tool_title` VARCHAR(255) NOT NULL,
    `user` VARCHAR(255) NOT NULL,
    `completed_date` DATETIME(6) NOT NULL,
    `tool_id` VARCHAR(255),
    CONSTRAINT `fk_complete_tool_cd7f7189` FOREIGN KEY (`tool_id`) REFERENCES `tool` (`name`) ON DELETE SET NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `completed_task`;"""
