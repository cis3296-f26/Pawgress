import aiosqlite
from contextlib import asynccontextmanager
from createTables import DB_PATH


@asynccontextmanager
async def connect():
    """Opens a connection with foreign keys enforced."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        yield db


#gets a user info from the database if they exist otherwise it will add them
async def get_or_create_user(discord_id: int, username: str) -> int:
    """Returns the internal user_id, creating the user row if needed."""
    async with connect() as db:
        async with db.execute(
            'SELECT user_id FROM "user" WHERE discord_id = ?', (str(discord_id),)
        ) as cur:
            row = await cur.fetchone()
        if row:
            return row[0]

        cur = await db.execute(
            'INSERT INTO "user" (discord_id, username) VALUES (?, ?)',
            (str(discord_id), username),
        )
        await db.commit()
        return cur.lastrowid

# pet methods (1 per server)

    # get pet information from database
async def get_pet(guild_id: int):
    """Returns (pet_id, pet_name, pet_type, pet_hunger) or None."""
    async with connect() as db:
        async with db.execute(
            "SELECT pet_id, pet_name, pet_type, pet_hunger FROM pet WHERE guild_id = ?",
            (str(guild_id),),
        ) as cur:
            return await cur.fetchone()

    # creates pet in the database (will not work if one exists in the server already)
async def create_pet(guild_id: int, name: str, pet_type: str, hunger: int = 0):
    async with connect() as db:
        await db.execute(
            "INSERT INTO pet (pet_name, pet_type, pet_hunger, guild_id) "
            "VALUES (?, ?, ?, ?)",
            (name, pet_type, hunger, str(guild_id)),
        )
        await db.commit()

#lets the pet rename save into the database
async def rename_pet(guild_id: int, new_name: str):
    async with connect() as db:
        await db.execute(
            "UPDATE pet SET pet_name = ? WHERE guild_id = ?",
            (new_name, str(guild_id)),
        )
        await db.commit()


# inventory methods

    #allows an item to be added to the database for a user
async def add_item(user_id: int, item_id: int, amount: int = 1):
    async with connect() as db:
        await db.execute(
            """
            INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)
            ON CONFLICT(user_id, item_id)
            DO UPDATE SET quantity = quantity + excluded.quantity
            """,
            (user_id, item_id, amount),
        )
        await db.commit()

    #allows an item to be removed from user inventory
async def remove_item(user_id: int, item_id: int, amount: int = 1) -> bool:
    """Returns False if the user doesn't have enough."""
    async with connect() as db:
        cur = await db.execute(
            """
            UPDATE inventory SET quantity = quantity - ?
            WHERE user_id = ? AND item_id = ? AND quantity >= ?
            """,
            (amount, user_id, item_id, amount),
        )
        await db.commit()
        return cur.rowcount > 0

    # allows the user to see what they have in there inventory
async def get_inventory(user_id: int):
    """Returns a list of (item_name, quantity, item_hunger_value)."""
    async with connect() as db:
        async with db.execute(
            """
            SELECT s.item_name, i.quantity, s.item_hunger_value
            FROM inventory i
            JOIN store s ON s.item_id = i.item_id
            WHERE i.user_id = ? AND i.quantity > 0
            """,
            (user_id,),
        ) as cur:
            return await cur.fetchall()