import asyncio
from itertools import islice
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import database
import techniques
from TimeTracker import TimeTracker


def first(n, technique):
    return list(islice(technique.schedule(), n))


def test_pomodoro_pattern():
    phases = first(8, techniques.POMODORO)

    assert phases[:2] == [("Focus", 1500), ("Break", 300)]
    assert phases[7] == ("Break", 900)


def test_pomodoro_repeats():
    phases = first(16, techniques.POMODORO)

    assert phases[8:] == phases[:8]


def test_ninety_minute_block():
    assert first(4, techniques.NINETY_MIN_BLOCK) == [
        ("Focus", 5400), ("Break", 1200),
        ("Focus", 5400), ("Break", 1200),
    ]


def test_flowtime_has_no_end():
    assert list(techniques.FLOWTIME.schedule()) == [("Focus", None)]


def test_base_technique_needs_a_schedule():
    with pytest.raises(NotImplementedError):
        techniques.StudyTechnique().schedule()


@pytest.fixture
def user():
    return SimpleNamespace(id=7, name="sam", mention="<@7>")


@pytest.fixture
def no_db(monkeypatch):
    monkeypatch.setattr(database, "add_coins", AsyncMock(return_value=True))
    monkeypatch.setattr(database, "get_coins", AsyncMock(return_value=0))


async def test_flowtime_session_counts_minutes(clock, no_db, user):
    session = techniques.StudySession(user, MagicMock(), techniques.FLOWTIME, TimeTracker())
    session.start()
    await asyncio.sleep(0)

    clock.advance(42)

    assert await session.stop() == 42


async def test_stop_only_counts_this_session(clock, no_db, user):
    tracker = TimeTracker()
    tracker.timer_start(user.id)
    clock.advance(30)
    await tracker.timer_stop(user.id, user.name)

    session = techniques.StudySession(user, MagicMock(), techniques.FLOWTIME, tracker)
    session.start()
    await asyncio.sleep(0)
    clock.advance(10)

    assert await session.stop() == 10


async def test_pomodoro_breaks_dont_count(clock, no_db, user, monkeypatch):
    sleeps = []

    async def fake_sleep(seconds):
        clock.now += seconds
        sleeps.append(seconds)
        if len(sleeps) == 3:
            raise asyncio.CancelledError

    monkeypatch.setattr(techniques, "asyncio", SimpleNamespace(sleep=fake_sleep))

    channel = MagicMock()
    channel.send = AsyncMock()
    session = techniques.StudySession(user, channel, techniques.POMODORO, TimeTracker())

    with pytest.raises(asyncio.CancelledError):
        await session.run()

    # 25 focus, 5 break, then stopped partway through the next 25 focus
    assert sleeps == [1500, 300, 1500]
    assert await session.stop() == 50

    messages = [c.args[0] for c in channel.send.call_args_list]
    assert messages == [
        "<@7> Break time for 5 minutes.",
        "<@7> Focus time for 25 minutes.",
    ]
