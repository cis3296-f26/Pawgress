import asyncio
from unittest.mock import MagicMock

import pytest
from discord import app_commands

import database
from commands.help import help as Help
from commands.pet import Pets
from commands.store import Store
from commands.study import study as Study
from commands.user import User


async def run(cog, name, interaction, *args):
    command = getattr(cog, name)
    await command.callback(cog, interaction, *args)
    return interaction.response.send_message.call_args


def food(value):
    names = {1: "Regular Food", 2: "Super Food", 3: "Mega Food"}
    return app_commands.Choice(name=names[value], value=value)


def method(value):
    return app_commands.Choice(name=value, value=value)


@pytest.fixture
def bot():
    return MagicMock()


async def test_help_lists_every_section(bot, make_interaction):
    reply = await run(Help(bot), "help", make_interaction())

    sections = [f.name for f in reply.kwargs["embed"].fields]
    assert sections == ["General", "Pet", "Study", "Store", "User"]


async def test_create_pet(db, bot, make_interaction):
    reply = await run(Pets(bot), "create_pet", make_interaction())

    assert reply.args[0] == "Your new pet has been created!"
    assert await database.get_pet(999) is not None


async def test_create_pet_when_one_exists(db, bot, make_interaction):
    await database.create_pet(999, "Biscuit", "Dog")

    reply = await run(Pets(bot), "create_pet", make_interaction())

    assert "already has a pet: **Biscuit** the **Dog**" in reply.args[0]


async def test_rename_without_pet(db, bot, make_interaction):
    reply = await run(Pets(bot), "rename_pet", make_interaction(), "Waffles")

    assert reply.args[0] == "Pet not found."


async def test_rename_pet(db, bot, make_interaction):
    await database.create_pet(999, "Biscuit", "Dog")

    reply = await run(Pets(bot), "rename_pet", make_interaction(), "Waffles")

    assert "**Waffles**" in reply.args[0]
    assert (await database.get_pet(999))[1] == "Waffles"


async def test_change_pet_type(db, bot, make_interaction):
    await database.create_pet(999, "Biscuit", "Dog")
    cat = app_commands.Choice(name="Cat", value="Cat")

    reply = await run(Pets(bot), "change_pet", make_interaction(), cat)

    assert reply.args[0] == "You now have a **Cat**!"
    assert (await database.get_pet(999))[2] == "Cat"


async def test_change_type_without_pet(db, bot, make_interaction):
    cat = app_commands.Choice(name="Cat", value="Cat")

    reply = await run(Pets(bot), "change_pet", make_interaction(), cat)

    assert reply.args[0] == "Pet not found."


async def test_catalog_shows_items_cheapest_first(db, bot, make_interaction):
    reply = await run(Store(bot), "store_catalog", make_interaction())

    fields = reply.kwargs["embed"].fields
    assert [f.name for f in fields] == ["Regular Food", "Super Food", "Mega"]
    assert "Cost: **15** coins" in fields[0].value


async def test_buy_without_coins(db, bot, make_interaction):
    reply = await run(Store(bot), "store_buy", make_interaction(), food(1))

    assert reply.args[0] == "You don't have enough coins for Regular Food"
    assert reply.kwargs["ephemeral"] is True


async def test_buy_food(db, bot, make_interaction):
    await database.add_coins(111, "alex", 30)

    reply = await run(Store(bot), "store_buy", make_interaction(), food(2))

    assert reply.args[0] == "Alex bought **Super Food** for 20 coins!"
    assert await database.get_coins(111) == 10


@pytest.mark.xfail(strict=True, reason="store table says Mega costs 40, COSTS in store.py says 45")
async def test_buy_price_matches_catalog(db, bot, make_interaction):
    await database.add_coins(111, "alex", 100)
    catalog = {i["item_name"]: i["item_cost"] for i in await database.get_store_catalog()}

    await run(Store(bot), "store_buy", make_interaction(), food(3))

    assert await database.get_coins(111) == 100 - catalog["Mega"]


async def test_balance(db, bot, make_interaction):
    await database.add_coins(111, "alex", 12)

    reply = await run(User(bot), "check_balance", make_interaction())

    assert reply.args[0] == "You have **12** coins"
    assert reply.kwargs["ephemeral"] is True


async def test_empty_inventory(db, bot, make_interaction):
    reply = await run(User(bot), "check_inventory", make_interaction())

    assert reply.args[0] == "Alex has no items in their inventory."


async def test_inventory_after_buying(db, bot, make_interaction):
    await database.add_coins(111, "alex", 30)
    await database.purchase_item(111, "alex", 1, 15)
    await database.purchase_item(111, "alex", 1, 15)

    reply = await run(User(bot), "check_inventory", make_interaction())

    field = reply.kwargs["embed"].fields[0]
    assert (field.name, field.value) == ("Regular Food", "Quantity: **2**")


async def test_study_info(bot, make_interaction):
    reply = await run(Study(bot), "study_info", make_interaction())

    embed = reply.kwargs["embed"]
    assert len(embed.fields) == 3
    assert reply.kwargs["ephemeral"] is True


@pytest.mark.xfail(strict=True, reason="footer still says /start, command is /study_start")
async def test_study_info_footer_uses_real_command(bot, make_interaction):
    reply = await run(Study(bot), "study_info", make_interaction())

    assert "/study_start" in reply.kwargs["embed"].footer.text


async def test_start_and_stop_studying(db, clock, bot, make_interaction):
    await database.create_pet(999, "Biscuit", "Dog")
    cog = Study(bot)

    reply = await run(cog, "start", make_interaction(), method("freeflow"))
    assert reply.args[0] == "Started Flowtime Study Method!"

    await asyncio.sleep(0)
    clock.advance(20)

    reply = await run(cog, "stop", make_interaction())
    assert reply.args[0] == "Timer stopped. Studied for 20 minutes."
    assert await database.get_coins(111) == 10


async def test_stop_with_nothing_running(db, bot, make_interaction):
    await database.create_pet(999, "Biscuit", "Dog")

    reply = await run(Study(bot), "stop", make_interaction())

    assert reply.args[0] == "No timer to be stopped."


@pytest.mark.xfail(strict=True, reason="study_start works without a pet but study_stop refuses")
async def test_can_stop_session_without_pet(db, clock, bot, make_interaction):
    cog = Study(bot)
    await run(cog, "start", make_interaction(), method("freeflow"))
    await asyncio.sleep(0)

    await run(cog, "stop", make_interaction())

    assert cog.sessions == {}


@pytest.mark.xfail(strict=True, reason="starting again overwrites the old session without stopping it")
async def test_starting_again_stops_old_session(db, clock, bot, make_interaction):
    cog = Study(bot)
    await run(cog, "start", make_interaction(), method("pomodoro"))
    old = cog.sessions[111]

    await run(cog, "start", make_interaction(), method("pomodoro"))
    await asyncio.sleep(0)

    try:
        assert old._task.done()
    finally:
        for session in (old, cog.sessions[111]):
            session._task.cancel()
