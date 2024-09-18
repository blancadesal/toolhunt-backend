from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `encrypted_token` LONGBLOB;
        ALTER TABLE `users` DROP COLUMN `token`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `token` LONGTEXT;
        ALTER TABLE `users` DROP COLUMN `encrypted_token`;"""
