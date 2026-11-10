from unittest.mock import AsyncMock, MagicMock

import pytest

import createTables
import database
import TimeTracker


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def time(self):
        return self.now

    def advance(self, minutes):
        self.now += minutes * 60


@pytest.fixture(autouse=True)
def fresh_tracker(monkeypatch):
    # hashmap lives on the class, so every test would share it otherwise
    monkeypatch.setattr(TimeTracker.TimeTracker, "hashmap", {})


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(TimeTracker, "time", fake)
    return fake


@pytest.fixture
async def db(tmp_path, monkeypatch):
    path = tmp_path / "data" / "test.db"
    monkeypatch.setattr(createTables, "DB_PATH", path)
    monkeypatch.setattr(database, "DB_PATH", path)
    await createTables.init_db()
    return path


@pytest.fixture
def make_interaction():
    def make(user_id=111, guild_id=999, name="alex"):
        interaction = MagicMock()
        interaction.guild_id = guild_id
        interaction.user.id = user_id
        interaction.user.name = name
        interaction.user.display_name = name.title()
        interaction.user.mention = f"<@{user_id}>"
        interaction.response.send_message = AsyncMock()
        interaction.channel.send = AsyncMock()
        return interaction

    return make
