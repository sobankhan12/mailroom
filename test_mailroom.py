from pathlib import Path

from mailroom.checks import (
    check_footer,
    check_greeting,
    check_issue,
    check_link,
    check_preview,
    check_subject,
)
from mailroom.subscribers import (
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


PREVIEW_90 = "Warm shawls, wraps and winter suits in khaddar and karandi. Waitlist members shop it first"


def test_preview_from_issue_01_has_no_problems():
    issue_text = "Subject: Hi\nPreview: Warm shawls, wraps and winter suits. Waitlist members shop first."
    assert check_preview(issue_text) == []


def test_preview_of_90_characters_has_no_problems():
    issue_text = "Subject: Hi\nPreview: " + PREVIEW_90
    assert check_preview(issue_text) == []


def test_preview_of_91_characters_is_too_long():
    issue_text = "Subject: Hi\nPreview: " + PREVIEW_90 + "."
    assert check_preview(issue_text) == ["too long"]


def test_empty_preview_is_empty():
    issue_text = "Subject: Hi\nPreview: \n\nHi {{first_name}},"
    assert check_preview(issue_text) == ["empty"]


def test_preview_of_only_spaces_is_empty():
    issue_text = "Subject: Hi\nPreview:      \n\nHi {{first_name}},"
    assert check_preview(issue_text) == ["empty"]


def test_no_preview_line_is_missing():
    issue_text = "Subject: Hi\n\nHi {{first_name}},"
    assert check_preview(issue_text) == ["missing"]


def test_greeting_with_first_name_has_no_problems():
    issue_text = "Subject: Hi\n\nHi {{first_name}},\n\nOur winter shawls are here."
    assert check_greeting(issue_text) == []


def test_greeting_without_first_name_is_missing():
    issue_text = "Subject: Hi\n\nHi there,\n\nOur winter shawls are here."
    assert check_greeting(issue_text) == ["missing"]


def test_one_link_has_no_problems():
    issue_text = "Hi {{first_name}},\n\n[Shop Charm of Winter](https://gulahmed.example/charm)\n\nStay warm,"
    assert check_link(issue_text) == []


def test_no_link_is_missing():
    issue_text = "Hi {{first_name}},\n\nShop Charm of Winter on Monday.\n\nStay warm,"
    assert check_link(issue_text) == ["missing"]


def test_two_links_is_too_many():
    issue_text = (
        "Hi {{first_name}},\n\n"
        "[Shop shawls](https://gulahmed.example/shawls)\n"
        "[Shop suits](https://gulahmed.example/suits)\n\n"
        "Stay warm,"
    )
    assert check_link(issue_text) == ["too many"]


def test_footer_from_issue_01_has_no_problems():
    issue_text = (
        "Stay warm,\nThe Gul Ahmed team\n\n"
        "You're getting this because you joined the Gul Ahmed winter waitlist.\n"
        "Gul Ahmed, {{company_address}} · Unsubscribe: {{unsubscribe_url}}"
    )
    assert check_footer(issue_text) == []


def test_footer_without_reason_line_is_missing_reason():
    issue_text = (
        "Stay warm,\nThe Gul Ahmed team\n\n"
        "Gul Ahmed, {{company_address}} · Unsubscribe: {{unsubscribe_url}}"
    )
    assert check_footer(issue_text) == ["missing reason"]


def test_footer_without_unsubscribe_line_is_missing_unsubscribe():
    issue_text = (
        "Stay warm,\nThe Gul Ahmed team\n\n"
        "You're getting this because you joined the Gul Ahmed winter waitlist."
    )
    assert check_footer(issue_text) == ["missing unsubscribe"]


def test_issue_01_has_no_problems():
    issue_text = Path("issues/issue-01.md").read_text(encoding="utf-8")
    assert check_issue(issue_text) == []


def test_issue_with_long_subject_and_no_link_shows_both_problems():
    issue_text = (
        "Subject: Your winter shawl ships on Monday in bright maroon.\n"
        "Preview: Shop first.\n\n"
        "Hi {{first_name}},\n\n"
        "Shop Charm of Winter on Monday.\n\n"
        "Stay warm,\nThe Gul Ahmed team\n\n"
        "You're getting this because you joined the Gul Ahmed winter waitlist.\n"
        "Gul Ahmed, {{company_address}} · Unsubscribe: {{unsubscribe_url}}"
    )
    assert check_issue(issue_text) == ["subject: too long", "link: missing"]


def test_subject_length_is_counted_with_len():
    # The reader sees 50 characters, but 👍🏽 is 2 pieces for len(), so len() says 51.
    subject = "👍🏽 Thanks for joining Charm of Winter 2026 waitlist"
    assert len(subject) == 51
    assert check_subject("Subject: " + subject) == ["too long"]
