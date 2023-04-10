from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `datasource` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `type` VARCHAR(8) NOT NULL  COMMENT 'mysql: mysql\npostgres: postgres\nlocal: local\nssh: ssh\nmongo: mongo\nredis: redis',
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `options` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `storage` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `type` VARCHAR(5) NOT NULL  COMMENT 'local: local\nssh: ssh\ns3: s3',
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `path` VARCHAR(255) NOT NULL  DEFAULT '',
    `options` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `task` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `compress` BOOL NOT NULL  DEFAULT 1,
    `keep_num` INT NOT NULL  DEFAULT 0,
    `keep_days` INT NOT NULL  DEFAULT 0,
    `enabled` BOOL NOT NULL  DEFAULT 1,
    `sub_path` VARCHAR(255) NOT NULL  DEFAULT '',
    `cron` VARCHAR(255) NOT NULL,
    `next_run_at` DATETIME(6),
    `data_source_id` INT NOT NULL,
    `storage_id` INT NOT NULL,
    CONSTRAINT `fk_task_datasour_a6c05e58` FOREIGN KEY (`data_source_id`) REFERENCES `datasource` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_task_storage_da90270e` FOREIGN KEY (`storage_id`) REFERENCES `storage` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `tasklog` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `status` VARCHAR(7) NOT NULL  COMMENT 'success: success\nfailed: failed\nrunning: running',
    `path` VARCHAR(255),
    `size` INT,
    `message` LONGTEXT,
    `is_deleted` BOOL NOT NULL  DEFAULT 0,
    `start_at` DATETIME(6) NOT NULL,
    `end_at` DATETIME(6),
    `task_id` INT NOT NULL,
    CONSTRAINT `fk_tasklog_task_ed604b07` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `restorelog` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `message` LONGTEXT,
    `restore_type` VARCHAR(8) NOT NULL  COMMENT 'mysql: mysql\npostgres: postgres\nlocal: local\nssh: ssh\nmongo: mongo\nredis: redis',
    `options` JSON NOT NULL,
    `status` VARCHAR(7) NOT NULL  COMMENT 'success: success\nfailed: failed\nrunning: running' DEFAULT 'running',
    `start_at` DATETIME(6) NOT NULL,
    `end_at` DATETIME(6),
    `task_log_id` INT NOT NULL,
    CONSTRAINT `fk_restorel_tasklog_452898fe` FOREIGN KEY (`task_log_id`) REFERENCES `tasklog` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
