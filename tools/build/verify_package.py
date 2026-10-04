"""Extract and execute the standalone Windows EXE; wait for all native tests."""
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path
import zipfile
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", required=True, type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="galgame-package-") as temp:
        destination = Path(temp)
        with zipfile.ZipFile(args.zip) as package:
            package.extractall(destination)
        exe = next(destination.rglob("BeforeTheRainStops.exe"), None)
        if not exe:
            raise SystemExit("Missing standalone Windows EXE")
        game = exe.parent / "game"
        for forbidden in ["data", "testcases.rpy", "testcases.rpyc", "saves"]:
            if (game / forbidden).exists():
                raise SystemExit(f"Authoring data leaked into package: {forbidden}")
        # Inject tests only into the temporary extraction, never the release ZIP.
        shutil.copy2("game/testcases.rpy", game / "testcases.rpy")
        result = subprocess.run([str(exe), str(exe.parent), "test", "global", "--report-detailed", "--overwrite-screenshots", "--savedir", str(destination / "saves")], cwd=exe.parent, capture_output=True, encoding="utf-8", errors="replace", timeout=180)
        evidence = Path("reports/package")
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "stdout.txt").write_text(result.stdout, encoding="utf-8")
        (evidence / "stderr.txt").write_text(result.stderr, encoding="utf-8")
        print(result.stdout)
        print(result.stderr)
        for log in ["log.txt", "errors.txt", "traceback.txt"]:
            if (exe.parent / log).is_file():
                shutil.copy2(exe.parent / log, evidence / log)
        screenshots = exe.parent / "reports/screenshots"
        if screenshots.exists():
            shutil.copytree(screenshots, evidence / "screenshots", dirs_exist_ok=True)
        if result.returncode:
            raise SystemExit(result.returncode)
        required = ["first-choice", "settings", "chapter-prologue", "chapter-today",
                    "cg-letter", "branch-s04_open", "branch-s04_reserved", "revisit-choice",
                    "audio-true-voice", "audio-normal-voice"] + ["expression-" + name for name in
            ("normal", "smile", "happy", "sad", "angry", "surprised", "embarrassed")]
        for name in required:
            file = screenshots / (name + ".png")
            if not file.is_file():
                raise SystemExit(f"Standalone EXE is missing UI evidence: {name}")
            with Image.open(file) as image:
                image.load()  # A present but truncated PNG is not usable evidence.
        print("Standalone Windows EXE: test process completed and UI evidence exists.")


if __name__ == "__main__":
    main()
