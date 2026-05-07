import asyncio
import os
import tempfile

from api.database.DatabaseManager import DatabaseManager


def test_get_user_balance_by_id_returns_float():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        db = DatabaseManager(db_path=path, build_schema=True)
        db.execute(
            "INSERT INTO user (name, last_name, balance) VALUES (?, ?, ?)",
            ("Ada", "Lovelace", 42.5),
        )

        async def _run():
            balance = await db.get_user_balance_by_id(1)
            assert balance == 42.5
            await db.update_user_balance_by_id(10.0, 1)
            assert await db.get_user_balance_by_id(1) == 10.0

        asyncio.run(_run())
    finally:
        db.close()
        os.unlink(path)


def test_get_user_balance_missing_user_returns_none():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        db = DatabaseManager(db_path=path, build_schema=True)

        async def _run():
            assert await db.get_user_balance_by_id(999) is None

        asyncio.run(_run())
    finally:
        db.close()
        os.unlink(path)
