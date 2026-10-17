import pytest
from tracker import calculate_streak
from datetime import date

def test_streak_empty():
    assert calculate_streak([]) == 0

def test_streak_one_day():
    from datetime import date, timedelta
    yesterday = str(date.today() - timedelta(days=1))
    assert calculate_streak([yesterday]) == 1

def test_streak_consecutive():
    today = str(date.today())
    assert calculate_streak([today]) >= 1