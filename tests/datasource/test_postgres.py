import pytest

from databack.datasource.postgres import Postgres


@pytest.mark.skip
async def test_postgres():
    pg_backup = Postgres(
        __host="localhost",
        __port=5432,
        __user="postgres",
        password="123456",
        backup_program="pg_dump",
        compress=True,
    )
    backup = await pg_backup.get_backup()
    pg_restore = Postgres(
        __host="localhost",
        __port=5432,
        __user="postgres",
        password="123456",
        compress=True,
        backup_program="pg_restore",
    )
    await pg_restore.restore(backup)
