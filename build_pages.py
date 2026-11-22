"""Export the browser-only Draft Desk site to a new directory."""

import argparse
from pathlib import Path
from shutil import copyfile


def build(destination: Path) -> None:
    root = Path(__file__).resolve().parent
    destination.mkdir(parents=True)
    html = (root / "web/index.html").read_text(encoding="utf-8")
    (destination / "index.html").write_text(
        html.replace('name="draft-validator" content="server"', 'name="draft-validator" content="browser"'),
        encoding="utf-8",
    )
    for file in ("draft.js", "validator.js", "site.css"):
        copyfile(root / "web" / file, destination / file)
    for file in ("draft.py", "run.py", "LICENSE"):
        copyfile(root / file, destination / file)
    copyfile(root / "synthetic-series.json", destination / "demo.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    build(parser.parse_args().destination)
