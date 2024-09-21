from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `tool` ADD `experimental` BOOL NOT NULL  DEFAULT 0;
        ALTER TABLE `tool` ADD `deprecated` BOOL NOT NULL  DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `tool` DROP COLUMN `experimental`;
        ALTER TABLE `tool` DROP COLUMN `deprecated`;"""
