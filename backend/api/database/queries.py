users_table_schema_query = """
        CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            password_hash TEXT NOT NULL
        )
        """

