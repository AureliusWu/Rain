"""Bind formal v1 publication to the exact technically and human-reviewed ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import zipfile

HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
GROUPS = ("ordinary_windows", "display_dpi", "listening", "creative_and_freeze")
ERROR_COUNTS = ("failed", "xfailed", "xpassed", "skipped", "not_run")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def has_text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_machine(machine, version):
    require(isinstance(version, str) and re.fullmatch(r"[1-9][0-9]*\.[0-9]+\.[0-9]+", version), "Formal gate requires a v1+ version")
    require(isinstance(machine, dict), "Machine acceptance must be a JSON object")
    require(machine.get("status") == "technical_and_visual_passed_with_human_limits", "Machine/visual acceptance incomplete")
    require(machine.get("unresolved_machine_issues") == [], "Unresolved or missing machine issue record")
    candidate = machine.get("candidate_commit", "")
    package = machine.get("package", {})
    require(isinstance(package, dict), "Invalid package record")
    require(isinstance(candidate, str) and HEX40.fullmatch(candidate), "Invalid candidate commit")
    require(machine.get("version") == version, "Machine version mismatch")
    digest = package.get("sha256")
    require(isinstance(digest, str) and HEX64.fullmatch(digest), "Invalid package SHA-256")
    require(package.get("file") == f"BeforeTheRainStops-{version}-win.zip", "Package filename/version mismatch")
    require(type(package.get("size_in_bytes")) is int and package["size_in_bytes"] > 0, "Missing package size")
    require(package.get("crc") == "passed" and package.get("test_scripts_in_original_zip") is False, "Package cleanliness/CRC not accepted")
    python_tests = machine.get("python_tests")
    require(isinstance(python_tests, dict) and type(python_tests.get("passed")) is int
            and python_tests["passed"] > 0 and machine.get("lint") == "passed", "Authoring/lint acceptance incomplete")
    suites = machine.get("suites")
    require(isinstance(suites, dict), "Missing suite records")
    for scope in ("source", "standalone", "fresh_process"):
        suite = suites.get(scope)
        require(isinstance(suite, dict), f"Missing {scope} suite")
        process = suite.get("process", {})
        require(all(type(suite.get(k)) is int and suite[k] > 0 for k in ("cases", "assertions")), f"Invalid {scope} test counts")
        require(all(type(suite.get(k)) is int and suite[k] == 0 for k in ERROR_COUNTS), f"Incomplete {scope} suite")
        require(isinstance(process, dict) and type(process.get("returncode")) is int
                and process["returncode"] == 0 and process.get("timed_out") is False, f"Unaccepted {scope} process")
    require(all(suites["source"][k] == suites["standalone"][k] for k in ("cases", "assertions")), "Source/EXE suite counts differ")
    require(type(machine.get("run_id")) is int and machine["run_id"] > 0, "Missing accepted CI run")
    artifacts = machine.get("artifacts")
    require(isinstance(artifacts, list) and all(isinstance(a, dict) for a in artifacts), "Invalid artifact records")
    artifacts = [a for a in artifacts if a.get("name") == f"windows-{candidate}"]
    require(len(artifacts) == 1 and type(artifacts[0].get("id")) is int and artifacts[0]["id"] > 0, "Missing unique accepted package artifact")
    return {"version": version, "candidate": candidate, "run_id": machine["run_id"],
            "artifact_id": artifacts[0]["id"], "package": package["file"],
            "sha256": package["sha256"], "size": package["size_in_bytes"]}


def validate_approval(machine, human, version):
    selection = validate_machine(machine, version)
    require(isinstance(human, dict), "Human acceptance must be a JSON object")
    require(human.get("schema_version") == 1 and human.get("status") == "approved", "Human acceptance pending")
    require(human.get("version") == version and human.get("candidate_commit") == selection["candidate"], "Human acceptance targets another candidate")
    require(human.get("package_sha256") == selection["sha256"], "Human acceptance targets another ZIP")
    require(has_text(human.get("reviewer")) and has_text(human.get("reviewed_at")), "Missing human reviewer/date")
    require(human.get("unresolved_issues") == [], "Unresolved human issues")
    for group in GROUPS:
        item = human.get(group, {})
        require(isinstance(item, dict) and item.get("status") == "passed" and has_text(item.get("evidence")), f"Human {group} pending or lacks evidence")
    timing = human.get("reading_time", {})
    require(isinstance(timing, dict) and timing.get("status") == "passed" and has_text(timing.get("evidence")), "Human reading timing pending")
    for ending in ("normal", "true"):
        minutes = timing.get(f"{ending}_minutes")
        require(type(minutes) in (int, float) and math.isfinite(minutes) and 30 <= minutes <= 60,
                f"{ending} measured playtime must be 30–60 minutes; revise or record a user-approved scope change first")
    return selection


def validate_zip(path, selection):
    path = Path(path)
    require(path.name == selection["package"], "Downloaded ZIP filename mismatch")
    require(path.stat().st_size == selection["size"], "Downloaded ZIP size mismatch")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    require(digest.hexdigest() == selection["sha256"], "Downloaded ZIP differs from reviewed bytes")
    with zipfile.ZipFile(path) as archive:
        require(archive.testzip() is None, "ZIP CRC failure")
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate ZIP entries")
        roots = {name.split('/')[0] for name in names}
        require(len(roots) == 1, "Unexpected ZIP roots")
        root = next(iter(roots))
        require(f"{root}/BeforeTheRainStops.exe" in names, "Standalone EXE missing")
        for name in names:
            require(not name.startswith('/') and '..' not in name.split('/'), "Unsafe ZIP path")
            relative = name.removeprefix(root + '/')
            require(not relative.startswith(("game/data/", "game/tests/", "game/saves/", "assets_source/", "tools/", "tests/", "prompts/", ".git/")), "Authoring/private files in ZIP")
            require(not relative.startswith("game/testcases."), "Injected tests in original ZIP")
            require(not relative.endswith((".onnx", ".pt", ".pth", ".safetensors")), "Inference model in ZIP")
        info = json.loads(archive.read(f"{root}/game/cache/build_info.json"))
        require(info.get("version") == selection["version"], "ZIP build version mismatch")
        for file in ("PLAYER_README.txt", "CREDITS.md", "LICENSE", "licenses/RENPY.txt", "licenses/SourceHanSans-OFL.txt", "licenses/Kokoro-model-Apache-2.0.txt"):
            require(f"{root}/{file}" in names, f"Missing player/license file: {file}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine", type=Path, default=Path("docs/evidence/v10-acceptance.json"))
    parser.add_argument("--human", type=Path, default=Path("docs/review/V10_HUMAN_ACCEPTANCE.json"))
    parser.add_argument("--version", required=True)
    parser.add_argument("--zip", type=Path)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        machine = json.loads(args.machine.read_text(encoding="utf-8"))
        selection = validate_approval(machine,
                                      json.loads(args.human.read_text(encoding="utf-8")), args.version)
        if args.zip:
            validate_zip(args.zip, selection)
        if args.preview:
            shots = [s for s in machine.get("screenshots", []) if s.get("scope") == "standalone"
                     and s.get("path") == "reports/package/screenshots/native-main-menu.png"]
            require(len(shots) == 1, "Accepted main-menu preview evidence missing")
            require(args.preview.name == f"BeforeTheRainStops-{args.version}-preview.png", "Preview filename mismatch")
            require(hashlib.sha256(args.preview.read_bytes()).hexdigest() == shots[0]["sha256"], "Preview differs from accepted EXE screenshot")
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as stream:
                for key, value in selection.items():
                    stream.write(f"{key}={value}\n")
        print("Formal release acceptance passed for the exact reviewed candidate.")
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Release blocked: {exc}\n")


if __name__ == "__main__":
    main()
