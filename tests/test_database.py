import sqlite3

import pytest

import createTables
import database


async def test_store_is_seeded(db):
    items = await database.get_store_catalog()

    assert [i["item_name"] for i in items] == ["Regular Food", "Super Food", "Mega"]


async def test_init_twice_doesnt_duplicate_items(db):
    await createTables.init_db()

    assert len(await database.get_store_catalog()) == 3


async def test_get_or_create_user_reuses_row(db):
    first = await database.get_or_create_user(123, "alex")
    second = await database.get_or_create_user(123, "alex")
    other = await database.get_or_create_user(456, "sam")

    assert first == second
    assert other != first


async def test_no_pet_yet(db):
    assert await database.get_pet(999) is None


async def test_create_and_get_pet(db):
    await database.create_pet(999, "Biscuit", "Dog")

    _, name, kind, hunger = await database.get_pet(999)
    assert (name, kind, hunger) == ("Biscuit", "Dog", 0)


async def test_only_one_pet_per_server(db):
    await database.create_pet(999, "Biscuit", "Dog")

    with pytest.raises(sqlite3.IntegrityError):
        await database.create_pet(999, "Mochi", "Cat")


async def test_each_server_gets_its_own_pet(db):
    await database.create_pet(1, "Biscuit", "Dog")
    await database.create_pet(2, "Mochi", "Cat")

    assert (await database.get_pet(1))[1] == "Biscuit"
    assert (await database.get_pet(2))[1] == "Mochi"


async def test_rename_pet(db):
    await database.create_pet(999, "Biscuit", "Dog")
    await database.rename_pet(999, "Waffles")

    assert (await database.get_pet(999))[1] == "Waffles"


async def test_change_pet_type(db):
    await database.create_pet(999, "Biscuit", "Dog")
    await database.set_pet_type(999, "Capybara")

    assert (await database.get_pet(999))[2] == "Capybara"


async def test_coins_start_at_zero(db):
    assert await database.get_coins(123) == 0


async def test_add_coins(db):
    await database.add_coins(123, "alex", 10)
    await database.add_coins(123, "alex", 5)

    assert await database.get_coins(123) == 15


async def test_purchase_without_enough_coins(db):
    await database.add_coins(123, "alex", 10)

    assert await database.purchase_item(123, "alex", 1, 15) is None
    assert await database.get_coins(123) == 10

    user_id = await database.get_or_create_user(123, "alex")
    assert await database.get_inventory(user_id) == []


async def test_purchase_takes_coins_and_adds_item(db):
    await database.add_coins(123, "alex", 50)

    assert await database.purchase_item(123, "alex", 1, 15) == 35
    assert await database.purchase_item(123, "alex", 1, 15) == 20

    user_id = await database.get_or_create_user(123, "alex")
    assert await database.get_inventory(user_id) == [("Regular Food", 2, 15)]


async def test_purchase_with_exact_amount(db):
    await database.add_coins(123, "alex", 20)

    assert await database.purchase_item(123, "alex", 2, 20) == 0


async def test_add_and_remove_items(db):
    user_id = await database.get_or_create_user(123, "alex")
    await database.add_item(user_id, 3, 2)

    assert await database.remove_item(user_id, 3) is True
    assert await database.get_inventory(user_id) == [("Mega", 1, 50)]


async def test_cant_remove_more_than_you_have(db):
    user_id = await database.get_or_create_user(123, "alex")
    await database.add_item(user_id, 1)

    assert await database.remove_item(user_id, 1, 2) is False
    assert await database.get_inventory(user_id) == [("Regular Food", 1, 15)]


async def test_empty_items_hidden_from_inventory(db):
    user_id = await database.get_or_create_user(123, "alex")
    await database.add_item(user_id, 1)
    await database.remove_item(user_id, 1)

    assert await database.get_inventory(user_id) == []


async def test_study_time(db):
    assert await database.get_study_time(123) == 0

    await database.add_study_time(123, "alex", 30)
    await database.add_study_time(123, "alex", 15)

    assert await database.get_study_time(123) == 45
