"""Fast start-of-batch checks before authoring or release work."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from tools.build import sdk

ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str]) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def _git_output(*args: str) -> str | None:
    if not (ROOT / ".git").exists():
        return None
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=ROOT / ".runtime")
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--require-sdk", action="store_true")
    args = parser.parse_args()

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    story = json.loads((ROOT / "game/data/story.json").read_text(encoding="utf-8"))
    if story.get("version") != version:
        raise SystemExit(
            f"Version mismatch: VERSION={version!r}, story={story.get('version')!r}"
        )

    required = [
        ROOT / "AGENTS.md",
        ROOT / "game/data/story.json",
        ROOT / "game/data/asset_manifest.json",
        ROOT / "game/data/voice_manifest.json",
        ROOT / "game/script/story_generated.rpy",
        ROOT / "game/testcases.rpy",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing required project files: " + ", ".join(missing))

    _run(["-m", "tools.compile_story", "--check"])
    _run(["-m", "tools.compile_tests", "--check"])

    cache = sdk.cache_status(args.runtime)
    print(
        "SDK cache:",
        f"usable={cache['sdk_usable']}",
        f"archive_present={cache['archive_present']}",
        f"archive_valid={cache['archive_valid']}",
        f"partial_present={cache['partial_present']}",
    )
    if args.require_sdk and not cache["sdk_usable"]:
        raise SystemExit("Pinned Ren'Py SDK is not usable; run python -m tools.build.sdk.")

    branch = _git_output("branch", "--show-current")
    status = _git_output("status", "--porcelain")
    head = _git_output("rev-parse", "HEAD")
    if branch is not None:
        print(f"Git: branch={branch or '(detached)'} head={head}")
        if status:
            print("Git working tree has local changes.")
            if args.require_clean:
                raise SystemExit("Working tree must be clean for this operation.")
        else:
            print("Git working tree is clean.")
    else:
        print("Git metadata unavailable; connector write permission must be checked externally.")

    print(f"Preflight passed for v{version}.")


if __name__ == "__main__":
    main()
