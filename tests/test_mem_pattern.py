"""
Tests for MemPattern class
"""
from datetime import datetime, timedelta
from random import randrange
import pytest
from memory_consumer.mem_pattern import MemPattern


def test_creation_for_dhm_pattern():
    """tests attributes computed during __init__ for dhm (day, hour, minute) pattern"""
    mem_p = MemPattern("tests/patterns/dhm.csv")
    assert mem_p.pattern_type == ["d", "h", "m"]
    assert mem_p.smallest_unit_resolution == 5
    assert mem_p.pattern_duration == 7 * 24 * 60
    assert mem_p.get_pattern_duration_in_seconds() == mem_p.pattern_duration * 60


def test_creation_for_m_pattern():
    """tests attributes computed during __init__ for m (minute) pattern"""
    mem_p = MemPattern("tests/patterns/m.csv")
    assert mem_p.pattern_type == ["m"]
    assert mem_p.smallest_unit_resolution == 1
    assert mem_p.pattern_duration == 60
    assert mem_p.get_pattern_duration_in_seconds() == mem_p.pattern_duration * 60


def test_creation_for_ms_pattern():
    """tests attributes computed during __init__ for ms (minute, second) pattern"""
    mem_p = MemPattern("tests/patterns/ms.csv")
    assert mem_p.pattern_type == ["m", "s"]
    assert mem_p.smallest_unit_resolution == 30
    assert mem_p.pattern_duration == 60 * 60
    assert mem_p.get_pattern_duration_in_seconds() == mem_p.pattern_duration


def test_creation_for_s_pattern():
    """tests attributes computed during __init__ for s (second) pattern"""
    mem_p = MemPattern("tests/patterns/s.csv")
    assert mem_p.pattern_type == ["s"]
    assert mem_p.smallest_unit_resolution == 1
    assert mem_p.pattern_duration == 60
    assert mem_p.get_pattern_duration_in_seconds() == mem_p.pattern_duration


@pytest.mark.parametrize(
    "date_time, value",
    # for datetime it is important the day of week, hour and minute
    [
        (datetime(2023, 8, 1, 2, 55), 3),
        (datetime(2023, 8, 1, 2, 54), 3),
        (datetime(2023, 8, 1, 0, 0), 36),
        (datetime(2023, 8, 1, 0, 1), 36),
        (datetime(2023, 8, 1, 23, 55), 43),
        (datetime(2023, 8, 1, 23, 59), 43),
        (datetime(2023, 8, 6, 23, 59), 30),
    ],
)
def test_get_right_values_for_dhm_pattern(date_time, value):
    """tests the right values are taken depending on day,hour,minute of various datetime objects"""
    mem_p = MemPattern("tests/patterns/dhm.csv")
    assert mem_p.get_value(date_time) == value


@pytest.mark.parametrize(
    "date_time, value",
    # for datetime it is important only minute
    [
        (datetime(2023, 12, 11, 2, 0), 60),
        (datetime(2023, 2, 4, 2, 59), 10),
        (datetime(2023, 7, 5, 0, 22), 60),
    ],
)
def test_get_right_values_for_m_pattern(date_time, value):
    """tests the right values are taken depending on minute of various datetime objects"""
    mem_p = MemPattern("tests/patterns/m.csv")
    assert mem_p.get_value(date_time) == value


@pytest.mark.parametrize(
    "date_time, value",
    # for datetime it is important only second
    [
        (datetime(2023, 12, 11, 2, 0, 0), 60),
        (datetime(2023, 2, 4, 2, 59, 59), 10),
        (datetime(2023, 7, 5, 0, 22, 11), 10),
    ],
)
def test_get_right_values_for_s_pattern(date_time, value):
    """tests the right values are taken depending on second of various datetime objects"""
    mem_p = MemPattern("tests/patterns/s.csv")
    assert mem_p.get_value(date_time) == value


@pytest.mark.parametrize(
    "date_time, value",
    # for datetime it is important only minute and second
    [
        (datetime(2023, 12, 11, 2, 0, 0), 3),
        (datetime(2023, 2, 4, 2, 59, 30), 2),
        (datetime(2023, 2, 4, 2, 59, 59), 2),
        (datetime(2023, 7, 5, 0, 59, 29), 2),
        (datetime(2023, 7, 5, 0, 42, 1), 36),
        (datetime(2023, 7, 5, 0, 42, 30), 36),
    ],
)
def test_get_right_values_for_ms_pattern(date_time, value):
    """tests the right values are taken depending on minute and second of various datetime
    objects"""
    mem_p = MemPattern("tests/patterns/ms.csv")
    assert mem_p.get_value(date_time) == value


def test_get_right_values_for_dhm_pattern_with_noise():
    """tests the right values are taken depending on day,hour,minute of various datetime objects
    with non-zero noise percent"""

    def rand_datetime(start: datetime, end: datetime) -> datetime:
        """Returns a random datetime between start and end."""

        return datetime.fromtimestamp(
            randrange(round(start.timestamp()), round(end.timestamp()))
        )

    noise_percent = 5
    mem_p = MemPattern("tests/patterns/dhm.csv")
    mem_p_noise = MemPattern("tests/patterns/dhm.csv", noise_percent=noise_percent)
    for _ in range(50):
        date_time = rand_datetime(datetime(2020, 1, 1), datetime(2023, 12, 31))
        value = mem_p.get_value(date_time)
        noised_value = mem_p_noise.get_value(date_time)
        margin = value * noise_percent // 100
        assert max(0, value - margin) <= noised_value <= value + margin


@pytest.mark.parametrize(
    "date_time, time_shift",
    [
        (datetime(2023, 12, 11, 2, 0, 15), timedelta(seconds=15)),
        (datetime(2023, 8, 14, 2, 59, 18), timedelta(minutes=59, seconds=18)),
        (datetime(2023, 2, 24, 2, 0, 0), timedelta(minutes=0, seconds=0)),
    ],
)
def test_get_time_shift_from_start_for_m_profile(date_time, time_shift):
    """tests the proper time shift from the beginning of m (minute) pattern is computed
    for specific datetime objects"""
    mem_p = MemPattern("tests/patterns/m.csv")
    assert mem_p.get_time_shift_from_start(date_time) == time_shift


@pytest.mark.parametrize(
    "date_time, time_shift",
    [
        (datetime(2023, 12, 11, 2, 0, 15), timedelta(seconds=15)),
        (datetime(2023, 2, 4, 2, 59, 18), timedelta(minutes=59, seconds=18)),
        (datetime(2023, 2, 4, 2, 0, 0), timedelta(minutes=0, seconds=0)),
    ],
)
def test_get_time_shift_from_start_for_ms_profile(date_time, time_shift):
    """tests the proper time shift from the beginning of ms (minute,second) pattern is computed
    for specific datetime objects"""
    mem_p = MemPattern("tests/patterns/ms.csv")
    assert mem_p.get_time_shift_from_start(date_time) == time_shift


@pytest.mark.parametrize(
    "date_time, time_shift",
    [
        (datetime(2023, 12, 11, 2, 0, 15), timedelta(seconds=15)),
        (datetime(2023, 2, 4, 2, 59, 18), timedelta(seconds=18)),
        (datetime(2023, 2, 4, 2, 1, 59), timedelta(seconds=59)),
        (datetime(2023, 2, 4, 2, 1, 0), timedelta(seconds=0)),
    ],
)
def test_get_time_shift_from_start_for_s_profile(date_time, time_shift):
    """tests the proper time shift from the beginning of s (second) pattern is computed
    for specific datetime objects"""
    mem_p = MemPattern("tests/patterns/s.csv")
    assert mem_p.get_time_shift_from_start(date_time) == time_shift


def test_get_time_shift_from_start_for_s_profile_for_none_date_time():
    """tests the proper time shift from the beginning of s (second) pattern is computed
    when date_time parameter is None - datetime.now() is used"""
    mem_p = MemPattern("tests/patterns/s.csv")
    assert mem_p.get_time_shift_from_start() >= timedelta(seconds=0)


@pytest.mark.parametrize(
    "date_time, time_shift",
    [
        (
            datetime(2023, 9, 21, 2, 0, 15),
            timedelta(days=3, hours=2, minutes=0, seconds=15),
        ),
        (
            datetime(2023, 9, 18, 2, 59, 18),
            timedelta(days=0, hours=2, minutes=59, seconds=18),
        ),
        (
            datetime(2023, 9, 24, 15, 1, 18),
            timedelta(days=6, hours=15, minutes=1, seconds=18),
        ),
        (
            datetime(2023, 9, 26, 2, 59, 0),
            timedelta(days=1, hours=2, minutes=59, seconds=0),
        ),
    ],
)
def test_get_time_shift_from_start_for_dhm_profile(date_time, time_shift):
    """tests the proper time shift from the beginning of dhm (day,hour,minute) pattern is computed
    for specific datetime objects"""
    mem_p = MemPattern("tests/patterns/dhm.csv")
    assert mem_p.get_time_shift_from_start(date_time) == time_shift


@pytest.mark.parametrize(
    "profile_file, first_value",
    [
        ("dhm.csv", 28),
        ("m.csv", 60),
        ("ms.csv", 3),
        ("s.csv", 60),
    ],
)
def test_get_first_value_for_any_datetime(profile_file, first_value):
    """tests the proper first value is retrieved from various patterns
    for any datetime objects"""
    mem_p = MemPattern(f"tests/patterns/{profile_file}")
    d_t_now = datetime.now()
    time_shift = mem_p.get_time_shift_from_start(d_t_now)
    assert mem_p.get_value(date_time=d_t_now - time_shift) == first_value
