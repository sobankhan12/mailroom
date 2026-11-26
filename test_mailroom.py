from mailroom.checks import (
    check_footer,
    check_greeting,
    check_issue,
    check_link,
    check_preview,
    check_subject,
    count_text,
)
from mailroom.subscribers import (
    DataFileError,
    count_by_group,
    count_joined_since,
    count_subscribers,
    next_send,
    read_subscribers,
)
from mailroom.issue import Issue, read_issue

SUBSCRIBERS = read_subscribers("data/subscribers.csv", "2026-11-20").subscribers


def test_there_are_24_subscribers_in_total() -> None:
    assert count_subscribers(SUBSCRIBERS) == 24


def test_there_are_three_groups() -> None:
    assert len(count_by_group(SUBSCRIBERS)) == 3


def test_shawl_lovers_has_8() -> None:
    assert count_by_group(SUBSCRIBERS)["shawl-lovers"] == 8


def test_gift_buyers_has_8() -> None:
    assert count_by_group(SUBSCRIBERS)["gift-buyers"] == 8


def test_loyal_shoppers_has_8() -> None:
    assert count_by_group(SUBSCRIBERS)["loyal-shoppers"] == 8


def test_7_joined_in_the_last_30_days_before_2026_11_20() -> None:
    # 2026-10-21 is exactly 30 days back, and it counts
    assert count_joined_since(SUBSCRIBERS, "2026-11-20", 30) == 7


def test_next_send_after_2026_11_20_is_first_monday_of_december() -> None:
    assert next_send("2026-11-20") == "2026-12-07"


def test_next_send_after_2026_12_07_is_first_monday_of_january() -> None:
    assert next_send("2026-12-07") == "2027-01-04"


def test_short_subject_has_no_problems() -> None:
    issue_text = "Subject: Charm of Winter 2026 opens Monday\nPreview: Shop first."
    assert check_subject(Issue(issue_text)) == []


def test_subject_of_50_characters_has_no_problems() -> None:
    issue_text = "Subject: Your winter shawl ships on Monday in bright maroon\nPreview: Shop first."
    assert check_subject(Issue(issue_text)) == []


def test_subject_of_51_characters_is_too_long() -> None:
    issue_text = "Subject: Your winter shawl ships on Monday in bright maroon.\nPreview: Shop first."
    assert check_subject(Issue(issue_text)) == ["too long"]


def test_empty_subject_is_empty() -> None:
    issue_text = "Subject: \nPreview: Shop first."
    assert check_subject(Issue(issue_text)) == ["empty"]


def test_subject_of_only_spaces_is_empty() -> None:
    issue_text = "Subject:      \nPreview: Shop first."
    assert check_subject(Issue(issue_text)) == ["empty"]


def test_no_subject_line_is_missing() -> None:
    issue_text = "Preview: Shop first.\n\nHi {{first_name}},"
    assert check_subject(Issue(issue_text)) == ["missing"]


PREVIEW_90 = "Warm shawls, wraps and winter suits in khaddar and karandi. Waitlist members shop it first"


def test_preview_from_issue_01_has_no_problems() -> None:
    issue_text = "Subject: Hi\nPreview: Warm shawls, wraps and winter suits. Waitlist members shop first."
    assert check_preview(Issue(issue_text)) == []


def test_preview_of_90_characters_has_no_problems() -> None:
    issue_text = "Subject: Hi\nPreview: " + PREVIEW_90
    assert check_preview(Issue(issue_text)) == []


def test_preview_of_91_characters_is_too_long() -> None:
    issue_text = "Subject: Hi\nPreview: " + PREVIEW_90 + "."
    assert check_preview(Issue(issue_text)) == ["too long"]


def test_empty_preview_is_empty() -> None:
    issue_text = "Subject: Hi\nPreview: \n\nHi {{first_name}},"
    assert check_preview(Issue(issue_text)) == ["empty"]


def test_preview_of_only_spaces_is_empty() -> None:
    issue_text = "Subject: Hi\nPreview:      \n\nHi {{first_name}},"
    assert check_preview(Issue(issue_text)) == ["empty"]


def test_no_preview_line_is_missing() -> None:
    issue_text = "Subject: Hi\n\nHi {{first_name}},"
    assert check_preview(Issue(issue_text)) == ["missing"]


def test_greeting_with_first_name_has_no_problems() -> None:
    issue_text = "Subject: Hi\n\nHi {{first_name}},\n\nOur winter shawls are here."
    assert check_greeting(Issue(issue_text)) == []


def test_greeting_without_first_name_is_missing() -> None:
    issue_text = "Subject: Hi\n\nHi there,\n\nOur winter shawls are here."
    assert check_greeting(Issue(issue_text)) == ["missing"]


def test_one_link_has_no_problems() -> None:
    issue_text = "Hi {{first_name}},\n\n[Shop Charm of Winter](https://gulahmed.example/charm)\n\nStay warm,"
    assert check_link(Issue(issue_text)) == []


def test_no_link_is_missing() -> None:
    issue_text = "Hi {{first_name}},\n\nShop Charm of Winter on Monday.\n\nStay warm,"
    assert check_link(Issue(issue_text)) == ["missing"]


def test_two_links_is_too_many() -> None:
    issue_text = (
        "Hi {{first_name}},\n\n"
        "[Shop shawls](https://gulahmed.example/shawls)\n"
        "[Shop suits](https://gulahmed.example/suits)\n\n"
        "Stay warm,"
    )
    assert check_link(Issue(issue_text)) == ["too many"]


def test_footer_from_issue_01_has_no_problems() -> None:
    issue_text = (
        "Stay warm,\nThe Gul Ahmed team\n\n"
        "You're getting this because you joined the Gul Ahmed winter waitlist.\n"
        "Gul Ahmed, {{company_address}} · Unsubscribe: {{unsubscribe_url}}"
    )
    assert check_footer(Issue(issue_text)) == []


def test_footer_without_reason_line_is_missing_reason() -> None:
    issue_text = (
        "Stay warm,\nThe Gul Ahmed team\n\n"
        "Gul Ahmed, {{company_address}} · Unsubscribe: {{unsubscribe_url}}"
    )
    assert check_footer(Issue(issue_text)) == ["missing reason"]


def test_footer_without_unsubscribe_line_is_missing_unsubscribe() -> None:
    issue_text = (
        "Stay warm,\nThe Gul Ahmed team\n\n"
        "You're getting this because you joined the Gul Ahmed winter waitlist."
    )
    assert check_footer(Issue(issue_text)) == ["missing unsubscribe"]


def test_issue_01_has_no_problems() -> None:
    assert check_issue(read_issue("issues/issue-01.md")) == []


def test_issue_with_long_subject_and_no_link_shows_both_problems() -> None:
    issue_text = (
        "Subject: Your winter shawl ships on Monday in bright maroon.\n"
        "Preview: Shop first.\n\n"
        "Hi {{first_name}},\n\n"
        "Shop Charm of Winter on Monday.\n\n"
        "Stay warm,\nThe Gul Ahmed team\n\n"
        "You're getting this because you joined the Gul Ahmed winter waitlist.\n"
        "Gul Ahmed, {{company_address}} · Unsubscribe: {{unsubscribe_url}}"
    )
    assert check_issue(Issue(issue_text)) == ["subject: too long", "link: missing"]


def test_subject_length_is_counted_with_len() -> None:
    # The reader sees 50 characters, but 👍🏽 is 2 pieces for len(), so len() says 51.
    subject = "👍🏽 Thanks for joining Charm of Winter 2026 waitlist"
    assert len(subject) == 51
    assert check_subject(Issue("Subject: " + subject)) == ["too long"]


def test_issue_01_has_one_link() -> None:
    issue = read_issue("issues/issue-01.md")
    assert issue.links == ["https://gulahmed.example/charm-of-winter-2026"]


def test_personalize_puts_ayesha_where_first_name_was() -> None:
    text = read_issue("issues/issue-01.md").personalize("Ayesha")
    assert count_text(text, "Hi Ayesha,") == 1
    assert count_text(text, "{{first_name}}") == 0


def test_personalize_leaves_unsubscribe_url_as_it_is() -> None:
    text = read_issue("issues/issue-01.md").personalize("Ayesha")
    assert count_text(text, "Unsubscribe: {{unsubscribe_url}}") == 1


SIGNUPS = read_subscribers("data/new-signups.csv", "2026-11-20")


def test_new_signups_gives_2_good_subscribers() -> None:
    assert len(SIGNUPS.subscribers) == 2


def test_the_2_good_subscribers_are_maria_and_ines() -> None:
    assert SIGNUPS.subscribers[0].first_name == "Maria"
    assert SIGNUPS.subscribers[1].first_name == "Ines"


def test_new_signups_gives_6_problems() -> None:
    assert len(SIGNUPS.problems) == 6


def problem_fields_for_row(row: int) -> list[str]:
    fields: list[str] = []
    for problem in SIGNUPS.problems:
        if problem.row == row:
            fields.append(problem.field)
    return fields


# Row numbers are as in a spreadsheet: the header is row 1, Maria is row 2.
def test_omar_row_3_has_an_email_problem() -> None:
    assert problem_fields_for_row(3) == ["email"]


def test_lena_row_4_has_a_consent_problem() -> None:
    assert problem_fields_for_row(4) == ["consent"]


def test_kofi_row_5_has_a_group_problem() -> None:
    assert problem_fields_for_row(5) == ["group"]


def test_hana_row_6_has_a_joined_on_problem() -> None:
    assert problem_fields_for_row(6) == ["joined_on"]


def test_sara_row_7_has_an_email_problem_not_at_example_com() -> None:
    assert problem_fields_for_row(7) == ["email"]


def test_tom_row_8_has_a_joined_on_problem_after_the_run_date() -> None:
    # Tom joined 2027-01-15; the run date is 2026-11-20
    assert problem_fields_for_row(8) == ["joined_on"]


def test_no_file_stops_everything() -> None:
    try:
        read_subscribers("data/no-such-file.csv", "2026-11-20")
    except DataFileError:
        return
    raise AssertionError("expected DataFileError")


def test_wrong_columns_stops_everything() -> None:
    try:
        read_subscribers("data/wrong-columns.csv", "2026-11-20")
    except DataFileError:
        return
    raise AssertionError("expected DataFileError")
