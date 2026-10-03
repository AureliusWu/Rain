"""Enumerate all choice combinations and validate ending reachability."""
import argparse
import json
from pathlib import Path
from tools.story_model import load_story, enumerate_routes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--story", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = enumerate_routes(load_story(args.story) if args.story else load_story())
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scenes: {len(report['reachable'])}; complete routes: {len(report['routes'])}; endings: {sorted({r['ending'] for r in report['routes']})}")
    for e in report["errors"]:
        print("ERROR:", e)
    raise SystemExit(bool(report["errors"]))


if __name__ == "__main__":
    main()
