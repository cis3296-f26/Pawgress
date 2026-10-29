import asyncio
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "database.db"

async def init_db():
    # path to database
    DB_PATH.parent.mkdir(exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        # creates pet table if is not already created
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pet (
                pet_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_name   TEXT NOT NULL,
                pet_type   TEXT,
                pet_hunger INTEGER NOT NULL DEFAULT 0,
                guild_id   TEXT NOT NULL UNIQUE
            )
        """)

        # creates user table if is not already created
        await db.execute("""
            CREATE TABLE IF NOT EXISTS "user" (
                user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id    TEXT NOT NULL UNIQUE,
                username      TEXT NOT NULL,
                coins INTEGER NOT NULL DEFAULT 0,
                total_study_time INTEGER DEFAULT 0

            )
        """)

        # creates store table if is not already created
        await db.execute("""
            CREATE TABLE IF NOT EXISTS store (
                item_id           INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name         TEXT NOT NULL UNIQUE,
                item_hunger_value INTEGER NOT NULL,
                item_cost         INTEGER NOT NULL
            )
        """)

        # creates inventory table if is not already created
        await db.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id  INTEGER NOT NULL,
                item_id  INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
                PRIMARY KEY (user_id, item_id),
                FOREIGN KEY (user_id) REFERENCES "user"(user_id),
                FOREIGN KEY (item_id) REFERENCES store(item_id)
            )
        """)

        # placeholder for shop items (feel free to remove later)
        await db.executemany(
            "INSERT OR IGNORE INTO store (item_name, item_hunger_value, item_cost) "
            "VALUES (?, ?, ?)",
            [("Bone", 10, 5), ("Fish", 20, 10), ("Treat", 5, 2)],
        )

        await db.commit()

if __name__ == "__main__":
    asyncio.run(init_db())
    print(f"Database ready at {DB_PATH}")