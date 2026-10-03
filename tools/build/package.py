"""Build a Windows ZIP from the pinned SDK using absolute project paths."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from tools.story_model import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", required=True, type=Path)
    args = parser.parse_args()
    sdk = args.sdk.resolve()
    destination = ROOT / "dist"
    if os.name == "nt":
        command = [str(sdk / "lib/py3-windows-x86_64/python.exe"), str(sdk / "renpy.py")]
    else:
        command = [str(sdk / "renpy.sh")]
    command += [str(sdk / "launcher"), "distribute", str(ROOT), "--package", "win", "--destination", str(destination)]
    subprocess.run(command, check=True)
    version = (ROOT / "VERSION").read_text().strip()
    archive = destination / f"BeforeTheRainStops-{version}-win.zip"
    if not archive.is_file():
        raise SystemExit("Build exited without the expected Windows ZIP")
    print(archive)


if __name__ == "__main__":
    main()
