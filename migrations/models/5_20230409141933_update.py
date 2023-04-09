from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `restorelog` ADD `options` JSON NOT NULL;
        ALTER TABLE `restorelog` ALTER COLUMN `status` SET DEFAULT 'running';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `restorelog` DROP COLUMN `options`;
        ALTER TABLE `restorelog` ALTER COLUMN `status` DROP DEFAULT;"""
