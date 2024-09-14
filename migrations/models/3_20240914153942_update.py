from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `field` (
    `name` VARCHAR(80) NOT NULL  PRIMARY KEY,
    `description` VARCHAR(2047) NOT NULL,
    `input_options` VARCHAR(2047),
    `pattern` VARCHAR(320)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `field`;"""
