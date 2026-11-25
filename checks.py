from mailroom import count_by_group, count_subscribers, read_lines

lines = read_lines("data/subscribers.csv")

# 24 in total
assert count_subscribers(lines) == 24

# 8 in each of the three groups
groups = count_by_group(lines)
assert len(groups) == 3
assert groups["shawl-lovers"] == 8
assert groups["gift-buyers"] == 8
assert groups["loyal-shoppers"] == 8

print("all checks passed")
