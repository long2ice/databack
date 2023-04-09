from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `restorelog` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `message` LONGTEXT,
    `status` VARCHAR(7) NOT NULL  COMMENT 'success: success\nfailed: failed\nrunning: running',
    `start_at` DATETIME(6) NOT NULL,
    `end_at` DATETIME(6),
    `task_log_id` INT NOT NULL,
    CONSTRAINT `fk_restorel_tasklog_452898fe` FOREIGN KEY (`task_log_id`) REFERENCES `tasklog` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `restorelog`;"""
