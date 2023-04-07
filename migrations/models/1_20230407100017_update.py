from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `task` ADD `sub_path` VARCHAR(255) NOT NULL  DEFAULT '';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `task` DROP COLUMN `sub_path`;"""
