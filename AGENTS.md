# Mailroom

Mailroom is a command-line tool for one sample newsletter: Gul Ahmed's winter collection, "Charm of Winter 2026".
It reads the subscribers, checks an issue, and sends it to a practice mail server.

## Rules

- Use Python 3.12 or newer.
- Use uv for everything: `uv run`, `uv add`, `uv sync`. Never use pip or a bare `python` command.
- Never use a real person's email address. Use @example.com, and @resend.dev for practice sends.
- Commit and push after every step.
- Before calling a step done, run it with uv and show me the real output.
- Behaviors first. I give the expected answers, you write them as pytest tests (one test per behavior, run with `uv run pytest`), show them failing, then write the code.
- I decide the test cases and their answers. Never change an expected answer to make a test pass.
- Never read today's date inside the logic. Pass the run date in. Only the command line may read today's date.
- When something breaks, show me the full error before changing anything.
- Mailroom is a package under `src/mailroom`. One module per job: `subscribers` (subscribers and dates), `issue`, `checks`, `commands`. Run it with `uv run mailroom`.
- Only the `commands` module prints.
- Pass `Subscriber` and `Issue` objects around, never raw rows or raw text.
- Every function has type hints, and pyright must be clean (`uv run pyright` shows 0 errors). When pyright complains, fix the call, not the hint.

## Decisions

- Length limits (subject 50, preview 90) count what Python's `len()` counts: code points. An emoji like 👍🏽 is 2 pieces, so it counts as 2, even though the reader sees 1.

## How I learn

- I am new to Python. I have completed up to 14.4 of https://agentfactory.panaversity.org/building-ai-workers/programming-fundamentals/ and I update this number as I learn.
- Write only with what I have learned. If something new would really help, stop and tell me its name in one line. I decide.
- When the code uses something new, show me that piece first and ask me to predict what it does. Stay quiet while I guess. Then run it, and explain a line only when I ask.
