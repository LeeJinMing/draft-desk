# How PyCharm helped make a draft board reproducible

At the start of game three, a coach needs two answers quickly: which champions were picked in the first two games, and which bans have just expired? Draft Desk runs one Python rule implementation in three places: a local server, a command-line reader and a browser with Pyodide. Keeping these entry points usable was part of the development work.

## From an inspection to a working handoff

PyCharm's first project inspection flagged a possible reference to the CLI variable `board` before assignment. Reading the error path showed that invalid input should return immediately. The current [CLI](run.py) prints a diagnostic, returns 2 and reaches the JSON output only after successful validation. To exercise the branch, save `{}` as `invalid-series.json` and run `python run.py invalid-series.json`. Then run `python run.py synthetic-series.json` and compare exit codes and outputs.

The inspector also flagged unresolved frontend assets and JavaScript state types. Relative asset paths let the board load under the repository's Pages subdirectory. The [frontend](web/draft.js) now gives its champion-to-state map explicit key and value types. The [shared PyCharm profile](.idea/inspectionProfiles/Draft_Desk.xml) lets another developer repeat the inspection. A later clean-source inspection still produced five findings, including naming and workflow metadata warnings. We checked actual board behavior separately.

## Try the coaching decision

Open the [draft board](https://leejinming.github.io/draft-desk/) in a fresh browser. The synthetic second game begins with 10 locked champions. Fill both teams to five picks, record the game and check that 20 champions are locked for game three while the previous game's bans are gone. Switch to Standard, then back to Hard Fearless. Export the series, reload and import it to verify the handoff. The [Game 5 fixture](synthetic-game-five.json) provides a second check with 40 prior locks.

Codex assisted with implementation and verification. PyCharm 2026.3.0.1 was the JetBrains tool used for the project inspection. The examples use synthetic data. The checks are reproducible with the [setup and inspection commands](README.md).
