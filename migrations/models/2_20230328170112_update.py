from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `task` DROP COLUMN `last_run_at`;
        ALTER TABLE `tasklog` ADD `is_deleted` BOOL NOT NULL  DEFAULT 0;
        ALTER TABLE `tasklog` MODIFY COLUMN `path` VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `task` ADD `last_run_at` DATETIME(6);
        ALTER TABLE `tasklog` DROP COLUMN `is_deleted`;
        ALTER TABLE `tasklog` MODIFY COLUMN `path` VARCHAR(255) NOT NULL;"""
