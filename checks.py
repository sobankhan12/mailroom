from mailroom import (
    count_by_group,
    count_joined_since,
    count_subscribers,
    next_send,
    read_lines,
)

lines = read_lines("data/subscribers.csv")

# 24 in total
assert count_subscribers(lines) == 24

# 8 in each of the three groups
groups = count_by_group(lines)
assert len(groups) == 3
assert groups["shawl-lovers"] == 8
assert groups["gift-buyers"] == 8
assert groups["loyal-shoppers"] == 8

# Run date 2026-11-20: 7 joined in the last 30 days (2026-10-21 counts)
assert count_joined_since(lines, "2026-11-20", 30) == 7

# Next send is the first Monday of the next month
assert next_send("2026-11-20") == "2026-12-07"
assert next_send("2026-12-07") == "2027-01-04"

print("all checks passed")
