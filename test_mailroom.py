from mailroom import (
    check_subject,
    count_by_group,
    count_joined_since,
    count_subscribers,
    next_send,
    read_lines,
)

LINES = read_lines("data/subscribers.csv")


def test_there_are_24_subscribers_in_total():
    assert count_subscribers(LINES) == 24


def test_there_are_three_groups():
    assert len(count_by_group(LINES)) == 3


def test_shawl_lovers_has_8():
    assert count_by_group(LINES)["shawl-lovers"] == 8


def test_gift_buyers_has_8():
    assert count_by_group(LINES)["gift-buyers"] == 8


def test_loyal_shoppers_has_8():
    assert count_by_group(LINES)["loyal-shoppers"] == 8


def test_7_joined_in_the_last_30_days_before_2026_11_20():
    # 2026-10-21 is exactly 30 days back, and it counts
    assert count_joined_since(LINES, "2026-11-20", 30) == 7


def test_next_send_after_2026_11_20_is_first_monday_of_december():
    assert next_send("2026-11-20") == "2026-12-07"


def test_next_send_after_2026_12_07_is_first_monday_of_january():
    assert next_send("2026-12-07") == "2027-01-04"


def test_short_subject_has_no_problems():
    issue_text = "Subject: Charm of Winter 2026 opens Monday\nPreview: Shop first."
    assert check_subject(issue_text) == []


def test_subject_of_50_characters_has_no_problems():
    issue_text = "Subject: Your winter shawl ships on Monday in bright maroon\nPreview: Shop first."
    assert check_subject(issue_text) == []


def test_subject_of_51_characters_is_too_long():
    issue_text = "Subject: Your winter shawl ships on Monday in bright maroon.\nPreview: Shop first."
    assert check_subject(issue_text) == ["too long"]


def test_empty_subject_is_empty():
    issue_text = "Subject: \nPreview: Shop first."
    assert check_subject(issue_text) == ["empty"]


def test_subject_of_only_spaces_is_empty():
    issue_text = "Subject:      \nPreview: Shop first."
    assert check_subject(issue_text) == ["empty"]


def test_no_subject_line_is_missing():
    issue_text = "Preview: Shop first.\n\nHi {{first_name}},"
    assert check_subject(issue_text) == ["missing"]
