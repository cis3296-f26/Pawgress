import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "database.db"


async def get_or_create_user(discord_id: int, username: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT user_id FROM "user" WHERE discord_id = ?', (str(discord_id),)
        ) as cur:
            row = await cur.fetchone()
        if row:
            return row[0]

        cur = await db.execute(
            'INSERT INTO "user" (discord_id, username, user_coins) VALUES (?, ?, 0)',
            (str(discord_id), username),
        )
        await db.commit()
        return cur.lastrowid


async def get_pet(guild_id: int):
    """Returns (pet_id, pet_name, pet_type, pet_hunger) or None."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT pet_id, pet_name, pet_type, pet_hunger FROM pet WHERE guild_id = ?",
            (str(guild_id),),
        ) as cur:
            return await cur.fetchone()


async def create_pet(guild_id: int, user_id: int, name: str, pet_type: str, hunger: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO pet (pet_name, pet_type, pet_hunger, user_id, guild_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, pet_type, hunger, user_id, str(guild_id)),
        )
        await db.commit()


async def rename_pet(guild_id: int, new_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE pet SET pet_name = ? WHERE guild_id = ?", (new_name, str(guild_id))
        )
        await db.commit()