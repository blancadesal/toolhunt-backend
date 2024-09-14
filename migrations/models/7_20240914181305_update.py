from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `field` ADD `field_type` VARCHAR(20) NOT NULL  COMMENT 'STRING: string\nMULTI_SELECT: multi_select\nSINGLE_SELECT: single_select\nBOOLEAN: boolean\nURI: uri';
        ALTER TABLE `field` MODIFY COLUMN `input_options` JSON;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `field` DROP COLUMN `field_type`;
        ALTER TABLE `field` MODIFY COLUMN `input_options` VARCHAR(2047);"""
