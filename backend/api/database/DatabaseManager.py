import asyncio
import sqlite3
from sqlite3 import Connection, Cursor

from api.database.queries import users_table_schema_query


class DatabaseManager:
    def __init__(self, db_path: str = "applicationDB.db", build_schema: bool = True):
        self.db_path = db_path
        self.conn: Connection | None = None
        self.cursor: Cursor | None = None
        self.build_schema: bool = build_schema
        self._lock = asyncio.Lock()
        self._connect_sync()
        if self.build_schema:
            self.initialize_schema()

    def _connect_sync(self) -> None:
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def connect(self) -> tuple[Cursor, Connection]:
        if self.conn is None:
            self._connect_sync()
        assert self.cursor is not None and self.conn is not None
        return self.cursor, self.conn

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def execute(self, query: str, params: tuple = ()) -> Cursor:
        self.connect()
        assert self.cursor is not None and self.conn is not None
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor

    def initialize_schema(self) -> None:
        self.connect()
        assert self.cursor is not None and self.conn is not None
        self.cursor.execute(users_table_schema_query)
        self.conn.commit()

    async def get_user_balance_by_id(self, user_id: int) -> float | None:
        async with self._lock:
            self.connect()
            assert self.conn is not None
            cur = self.conn.execute(
                "SELECT balance FROM user WHERE id = ?",
                (user_id,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        if row[0] is None:
            return 0.0
        return float(row[0])

    async def update_user_balance_by_id(self, new_balance: float, user_id: int) -> None:
        async with self._lock:
            self.connect()
            assert self.conn is not None
            self.conn.execute(
                "UPDATE user SET balance = ? WHERE id = ?",
                (new_balance, user_id),
            )
            self.conn.commit()


database_manager = DatabaseManager()
