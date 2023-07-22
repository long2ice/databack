from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `datasource` MODIFY COLUMN `type` VARCHAR(10) NOT NULL  COMMENT 'clickhouse: clickhouse\nmysql: mysql\npostgres: postgres\nlocal: local\nssh: ssh\nmongo: mongo\nredis: redis';
        ALTER TABLE `datasource` MODIFY COLUMN `type` VARCHAR(10) NOT NULL  COMMENT 'clickhouse: clickhouse\nmysql: mysql\npostgres: postgres\nlocal: local\nssh: ssh\nmongo: mongo\nredis: redis';
        ALTER TABLE `restorelog` MODIFY COLUMN `restore_type` VARCHAR(10) NOT NULL  COMMENT 'clickhouse: clickhouse\nmysql: mysql\npostgres: postgres\nlocal: local\nssh: ssh\nmongo: mongo\nredis: redis';
        ALTER TABLE `restorelog` MODIFY COLUMN `restore_type` VARCHAR(10) NOT NULL  COMMENT 'clickhouse: clickhouse\nmysql: mysql\npostgres: postgres\nlocal: local\nssh: ssh\nmongo: mongo\nredis: redis';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `datasource` MODIFY COLUMN `type` VARCHAR(8) NOT NULL  COMMENT 'mysql: mysql\npostgres: postgres\nlocal: local\nssh: ssh\nmongo: mongo\nredis: redis';
        ALTER TABLE `datasource` MODIFY COLUMN `type` VARCHAR(8) NOT NULL  COMMENT 'mysql: mysql\npostgres: postgres\nlocal: local\nssh: ssh\nmongo: mongo\nredis: redis';
        ALTER TABLE `restorelog` MODIFY COLUMN `restore_type` VARCHAR(8) NOT NULL  COMMENT 'mysql: mysql\npostgres: postgres\nlocal: local\nssh: ssh\nmongo: mongo\nredis: redis';
        ALTER TABLE `restorelog` MODIFY COLUMN `restore_type` VARCHAR(8) NOT NULL  COMMENT 'mysql: mysql\npostgres: postgres\nlocal: local\nssh: ssh\nmongo: mongo\nredis: redis';"""
