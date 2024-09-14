from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `field` MODIFY COLUMN `field_type` VARCHAR(20) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `field` MODIFY COLUMN `field_type` VARCHAR(20) NOT NULL  COMMENT 'STRING: string\nMULTI_SELECT: multi_select\nSINGLE_SELECT: single_select\nBOOLEAN: boolean\nURI: uri';"""
