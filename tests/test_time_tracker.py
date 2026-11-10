from unittest.mock import AsyncMock

import pytest

import database
from TimeTracker import TimeTracker


@pytest.fixture
def no_db(monkeypatch):
    monkeypatch.setattr(database, "add_coins", AsyncMock(return_value=True))
    monkeypatch.setattr(database, "get_coins", AsyncMock(return_value=0))


def test_start_for_new_user():
    tracker = TimeTracker()

    assert tracker.timer_start(1) == 0
    assert tracker.is_running(1)
    assert tracker.get_seconds(1) == 0


def test_cant_start_twice():
    tracker = TimeTracker()
    tracker.timer_start(1)

    assert tracker.timer_start(1) == 1


async def test_stop_records_elapsed_time(clock, no_db):
    tracker = TimeTracker()
    tracker.timer_start(1)
    clock.advance(10)

    assert await tracker.timer_stop(1, "alex") == 0
    assert tracker.get_seconds(1) == 600
    assert not tracker.is_running(1)


async def test_time_adds_up_over_sessions(clock, no_db):
    tracker = TimeTracker()
    for minutes in (5, 20):
        tracker.timer_start(1)
        clock.advance(minutes)
        await tracker.timer_stop(1, "alex")

    assert tracker.get_time(1) == "25 minutes"


async def test_stop_when_already_stopped(clock, no_db):
    tracker = TimeTracker()
    tracker.timer_start(1)
    await tracker.timer_stop(1, "alex")

    assert await tracker.timer_stop(1, "alex") == 1


async def test_stop_for_unknown_user(no_db):
    assert await TimeTracker().timer_stop(42, "nobody") == 2


def test_unknown_user_has_no_time():
    tracker = TimeTracker()

    assert tracker.get_seconds(42) == 0
    assert not tracker.is_running(42)


async def test_users_dont_share_timers(clock, no_db):
    tracker = TimeTracker()
    tracker.timer_start(1)
    clock.advance(10)
    tracker.timer_start(2)
    clock.advance(5)
    await tracker.timer_stop(1, "alex")

    assert tracker.get_seconds(1) == 900
    assert tracker.is_running(2)


async def test_one_coin_per_two_minutes(clock, db):
    tracker = TimeTracker()
    tracker.timer_start(1)
    clock.advance(10)
    await tracker.timer_stop(1, "alex")

    assert await database.get_coins(1) == 5


async def test_under_two_minutes_earns_nothing(clock, db):
    tracker = TimeTracker()
    tracker.timer_start(1)
    clock.now += 90
    await tracker.timer_stop(1, "alex")

    assert await database.get_coins(1) == 0
