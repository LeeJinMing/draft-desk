"""Show the draft board for a locally supplied series JSON file."""

import argparse
import json
import sys
from pathlib import Path

from draft import Game, draft_board


def champion_ids(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError("Champion lists must contain nonempty strings.")
    return tuple(value)


def board_for(document: object) -> dict:
    if not isinstance(document, dict):
        raise ValueError("The series document must be a JSON object.")
    mode = document.get("mode", "fearless")
    if mode not in ("fearless", "standard"):
        raise ValueError("Mode must be fearless or standard.")
    history = document.get("history", [])
    if not isinstance(history, list) or not all(isinstance(game, dict) for game in history):
        raise ValueError("History must be a list of completed games.")
    if len(history) > 5:
        raise ValueError("A series can contain up to five games.")
    if "blue" in document or "red" in document:
        blue = champion_ids(document.get("blue", []))
        red = champion_ids(document.get("red", []))
        if len(blue) > 5 or len(red) > 5:
            raise ValueError("A side can pick up to five champions.")
    else:
        picks = champion_ids(document.get("picks", []))
        blue, red = picks[:5], picks[5:]
    bans = champion_ids(document.get("bans", []))
    if len(history) == 5 and (blue or red or bans):
        raise ValueError("The series is complete. Remove the extra picks or bans.")
    games = tuple(Game(champion_ids(game["blue"]), champion_ids(game["red"])) for game in history)
    board = draft_board(champion_ids(document["pool"]), games,
                        picks=blue + red,
                        bans=bans,
                        fearless=mode == "fearless")
    return {"game": min(len(games) + 1, 5), "complete": len(games) == 5,
            "mode": mode, "blue": blue, "red": red, **board}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("series", type=Path)
    args = parser.parse_args()
    try:
        board = board_for(json.loads(args.series.read_text(encoding="utf-8-sig")))
    except (OSError, KeyError, ValueError) as error:
        print(f"Could not read the draft: {error}", file=sys.stderr)
        return 2
    print(json.dumps(board, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
