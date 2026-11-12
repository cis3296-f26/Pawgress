import aiosqlite
from contextlib import asynccontextmanager
from createTables import DB_PATH
import time

#Global Vairables for Hunger
HUNGER_MAX = 100
HUNGER_LOSS_PER_HOUR = 5

@asynccontextmanager
async def connect():
    """Opens a connection with foreign keys enforced."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        yield db
#Methods to interact with the database, get or add information (read, write)

#Gets a user info from the database if they exist otherwise it will add them
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

#Pet methods (1 per server)

    #Get pet information from database
async def get_pet(guild_id: int):
    """Returns (pet_id, pet_name, pet_type, pet_hunger) or None."""
    async with connect() as db:
        async with db.execute(
            "SELECT pet_id, pet_name, pet_type, pet_hunger FROM pet WHERE guild_id = ?",
            (str(guild_id),),
        ) as cur:
            return await cur.fetchone()

    #Creates a pet in the database (will not work if one exists in the server already)
async def create_pet(guild_id: int, name: str, pet_type: str, hunger: int = 100):
    async with connect() as db:
        await db.execute(
            "INSERT INTO pet (pet_name, pet_type, pet_hunger, guild_id) "
            "VALUES (?, ?, ?, ?)",
            (name, pet_type, hunger, str(guild_id)),
        )
        await db.commit()

#Let's the pet rename save into the database
async def rename_pet(guild_id: int, new_name: str):
    async with connect() as db:
        await db.execute(
            "UPDATE pet SET pet_name = ? WHERE guild_id = ?",
            (new_name, str(guild_id)),
        )
        await db.commit()

    # changes the pet's type in the database
async def set_pet_type(guild_id: int, new_type: str):
    async with connect() as db:
        await db.execute(
            'UPDATE pet SET pet_type = ? WHERE guild_id = ?',
            (new_type, str(guild_id)),
        )
        await db.commit()


#Inventory & Shop methods

    #Allows an item to be added to the database for a user
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

    #Allows an item to be removed from user inventory
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

    #Allows the user to see what they have in there inventory
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

    #will return all the items avilable in the database
async def get_store_catalog():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT item_name, item_hunger_value, item_cost FROM store ORDER BY item_cost"
        ) as cursor:
            return await cursor.fetchall()

    # adds a purchased item to there inventory
async def purchase_item(discord_id: int, username: str, item_id: int, cost: int):
    user_id = await get_or_create_user(discord_id, username)
    async with connect() as db:
        cur = await db.execute(
            'UPDATE "user" SET coins = coins - ? WHERE user_id = ? AND coins >= ?',
            (cost,user_id, cost),
        )

        if cur.rowcount == 0:
            return None

        await db.execute(
            """
            INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, 1)
            ON CONFLICT(user_id, item_id)
            DO UPDATE SET quantity = quantity + 1
            """,
            (user_id, item_id),
        )

        async with db.execute(
            'SELECT coins FROM "user" WHERE user_id = ?',
                (user_id,),
        ) as cur:
            row = await cur.fetchone()
        new_balance = row[0]

        await db.commit()
        return new_balance




#study time methods
    #Will get a users total time studied
async def get_study_time(discord_id: int) -> int:
    """Returns total study time in minutes, or 0 if the user has no row yet."""
    async with connect() as db:
        async with db.execute(
            'SELECT total_study_time FROM "user" WHERE discord_id = ?',
            (str(discord_id),),
        ) as cur:
            row = await cur.fetchone()
        return row[0] if row else 0


    #Will add study time to the total study time of the user
async def add_study_time(discord_id: int, username: str, minutes: int):
    """Adds seconds to the user's total, creating the user row if needed."""
    user_id = await get_or_create_user(discord_id, username)
    async with connect() as db:
        await db.execute(
            'UPDATE "user" SET total_study_time = total_study_time + ? WHERE user_id = ?',
            (minutes, user_id),
        )
        await db.commit()


# coin methods

    # will add coins to the users current coin balance
async def add_coins(discord_id: int, username: str, coins_int: int) -> bool:
    """Adds coins to a user, creating the user row if needed."""
    await get_or_create_user(discord_id, username)
    async with connect() as db:
        cur = await db.execute(
        'UPDATE "user" SET coins = coins + ? WHERE discord_id = ?',
            (coins_int, str(discord_id)),
        )
        await db.commit()
        return cur.rowcount > 0

    # gets the users coins that are in the database
async def get_coins(discord_id: int) -> int:
    """Returns the user's current coins."""
    async with connect() as db:
        async with db.execute(
            'SELECT coins FROM "user" WHERE discord_id = ?',
            (str(discord_id),),
        ) as cur:
            row = await cur.fetchone()
        return row[0] if row else 0


# pet hunger methods
    #will return the pet's current hunger
    #Creates a time stamp and will
async def get_hunger(guild_id: int):
    """Returns the pet's current hunger (0-100) after applying decay, or None if no pet."""
    async with connect() as db:
        async with db.execute(
            "SELECT pet_hunger, pet_last_update FROM pet WHERE guild_id = ?",
            (str(guild_id),),
        ) as cur:
            row = await cur.fetchone()
        if row is None:
            return None

        hunger, previous_time_stamp = row
        current_time = time.time()
        if previous_time_stamp is None:
            previous_time_stamp = current_time

        lost = int((current_time - previous_time_stamp) / 3600 * HUNGER_LOSS_PER_HOUR)
        if lost > 0:
            hunger = max(0, hunger - lost)
            # only advance the timestamp by the time actually "spent", so fractions aren't lost
            previous_time_stamp += lost * 3600 / HUNGER_LOSS_PER_HOUR

        await db.execute(
            "UPDATE pet SET pet_hunger = ?, pet_last_update = ? WHERE guild_id = ?",
            (hunger, previous_time_stamp, str(guild_id)),
        )
        await db.commit()
        return hunger

#will allow the user to add hunger to the pet
async def add_hunger(guild_id: int, amount: int):
    """Feeds the pet. Applies decay first, then adds amount (capped at 100). Returns new hunger."""
    current = await get_hunger(guild_id)
    if current is None:
        return None
    new_hunger = min(HUNGER_MAX, current + amount)
    async with connect() as db:
        await db.execute(
            "UPDATE pet SET pet_hunger = ? WHERE guild_id = ?",
            (new_hunger, str(guild_id)),
        )
        await db.commit()
    return new_hunger

#will interact with the user logic to feed the pet
async def feed_pet(guild_id: int, discord_id: int, username: str, item_id: int):
    """
    Feeds the pet one item from the user's inventory.
    Returns (status, data):
      ("ok", (item_name, new_hunger))
      ("no_pet", None)
      ("full", None)
      ("no_item", item_name)
    """
    current = await get_hunger(guild_id)
    if current is None:
        return "no_pet", None
    if current >= HUNGER_MAX:
        return "full", None

    user_id = await get_or_create_user(discord_id, username)

    async with connect() as db:
        async with db.execute(
            "SELECT item_name, item_hunger_value FROM store WHERE item_id = ?",
            (item_id,),
        ) as cur:
            item = await cur.fetchone()
    item_name, hunger_value = item

    if not await remove_item(user_id, item_id):
        return "no_item", item_name

    new_hunger = await add_hunger(guild_id, hunger_value)
    return "ok", (item_name, new_hunger)

async def get_item_hunger(item_id: int):
    async with connect() as db:
        async with db.execute(
                "SELECT item_hunger_value FROM store WHERE item_id = ?",
                (item_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0

    # creates the hunger bar that is to be sent to the user
def hunger_bar(hunger: int, length: int = 10) -> str:
    filled = round(hunger / HUNGER_MAX * length)
    return "🟩" * filled + "⬛" * (length - filled) + f" {hunger}/{HUNGER_MAX}"

#alert/notification methods

    #will delegate one channel as the channel that will be reciving passive notifications
async def set_alert_channel(guild_id: int, channel_id: int):
    async with connect() as db:
        await db.execute(
            "UPDATE pet SET channel_id = ? WHERE guild_id = ?",
            (str(channel_id), str(guild_id)),
        )
        await db.commit()

    #will get all the pets information of alert and channel id relation
async def get_all_pets():
    """Returns (guild_id, pet_name, last_alert, channel_id) for every pet."""
    async with connect() as db:
        async with db.execute(
            "SELECT guild_id, pet_name, last_alert, channel_id FROM pet"
        ) as cur:
            return await cur.fetchall()

    #will set the time stamp of the last alert/notification sent
async def set_last_alert(guild_id: int, level: int):
    async with connect() as db:
        await db.execute(
            "UPDATE pet SET last_alert = ? WHERE guild_id = ?",
            (level, str(guild_id)),
        )
        await db.commit()