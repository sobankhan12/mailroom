from mailroom import EMAIL_COLUMN, GROUP_COLUMN, count_unique, read_lines

# A tiny made-up sample: the same email appears twice, so it must count once.
sample = [
    "first_name,last_name,email,group,joined_on,consent",
    "Sara,Ali,sara.ali@example.com,shawl-lovers,2026-09-01,waitlist form",
    "Sara,Ali,sara.ali@example.com,shawl-lovers,2026-09-01,waitlist form",
    "Omar,Shah,omar.shah@example.com,gift-buyers,2026-09-02,waitlist form",
]
assert count_unique(sample, EMAIL_COLUMN) == 2
assert count_unique(sample, GROUP_COLUMN) == 2

# The real file: 24 subscribers in 3 groups.
lines = read_lines("data/subscribers.csv")
assert count_unique(lines, EMAIL_COLUMN) == 24
assert count_unique(lines, GROUP_COLUMN) == 3

print("all checks passed")
