# Draft Desk

A League of Legends coaching prototype for a series of up to five games. It models a standard draft or Hard Fearless and makes the remaining champion pool explicit before the next pick.

Run `python run.py synthetic-series.json` from this directory. The output contains the current game number and four lists: champions locked by previous games, current picks, current bans, and available champions. Change the JSON's mode to `standard` to see the regular rules.

Run `python -m unittest -v` to verify both draft modes and rejection of impossible drafts.

## Interactive draft board

Run `python serve.py` and open `http://127.0.0.1:5185/`. A synthetic 70-champion series starts on game two with ten champions locked by game one. Choose a destination for the next champion, add or remove picks and bans, and record the game once both sides have five picks. Recording a game carries its picks into Hard Fearless and clears its bans. The board closes after five games. Export the series before reloading to keep the in-progress draft, and import the JSON to resume it. To start an empty series, import a document with a `pool` array and a `mode` of `fearless` or `standard`.

## JetBrains workflow

PyCharm 2026.3.0.1 opened the project and ran its code inspector. The first report identified a CLI error branch and unresolved frontend assets. The CLI now returns explicitly on invalid input, the page uses relative asset URLs, and the browser's champion state mapping has explicit string types.

To inspect the app interactively in PyCharm, open this directory, select Python 3.10 or newer, run `test_draft.py` as a unittest, and run `serve.py` to start the browser demo.

## Methodology

The board derives available champions from three sets: picks in recorded games under Hard Fearless, picks in the current game, and bans in the current game. A candidate is available only when it belongs to the supplied pool and to none of those sets. The same Python validator handles imported series, browser edits and CLI input. Invalid imports leave the current series intact.

The [organizer's GRID data license](https://github.com/cloud9esports/stl-hackathon-2026-grid-starter/blob/main/LICENSE.md) governs the official dataset. Registered participants can retrieve it from the organizer during the event and keep it outside this project directory. Test fixtures in this project are synthetic. Any future public demonstration should use synthetic fixtures or excerpts allowed by that license.
