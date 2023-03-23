from databack.datasource.postgres import Postgres


async def test_postgres():
    pg_backup = Postgres(
        __host="localhost",
        __port=5432,
        __user="postgres",
        password="123456",
        compress=True,
    )
    backup = await pg_backup.get_backup()
    pg_restore = Postgres(
        __host="localhost",
        __port=5432,
        __user="postgres",
        password="123456",
        compress=True,
    )
    await pg_restore.restore(backup)
