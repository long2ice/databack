from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `storage` ADD `path` VARCHAR(255) NOT NULL  DEFAULT '';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `storage` DROP COLUMN `path`;"""
