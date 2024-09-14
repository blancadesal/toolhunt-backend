from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `tool` (
    `name` VARCHAR(255) NOT NULL  PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `description` LONGTEXT NOT NULL,
    `url` VARCHAR(2047) NOT NULL,
    `last_updated` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `tool`;"""
