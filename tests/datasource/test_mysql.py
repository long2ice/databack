import pytest

from databack.datasource.mysql import MySQL


@pytest.mark.skip
async def test_mysql():
    kwargs = {
        "--host": "localhost",
        "--port": 3306,
        "--user": "root",
        "--password": "123456",
        "compress": True,
    }
    backup_kwargs = {
        "--include-databases": "test",
        "--set-gtid-purged": "OFF",
        "--add-drop-database": True,
    }
    mysql_backup = MySQL(
        **kwargs,
        **backup_kwargs,
    )
    backup = await mysql_backup.get_backup()
    mysql_restore = MySQL(**kwargs)
    await mysql_restore.restore(backup)
