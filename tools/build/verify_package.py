"""Extract and execute the standalone Windows EXE; wait for all native tests."""
import argparse
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
import zipfile
from PIL import Image

DEFAULT_TEST_TIMEOUT = 900


def positive_timeout(value):
    seconds = int(value)
    if seconds <= 0:
        raise argparse.ArgumentTypeError('Timeout must be a positive number of seconds')
    return seconds


def output_text(value):
    return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')


def run_native_tests(command, *, cwd, evidence, timeout):
    """Keep process output and timing even when the native suite times out."""
    evidence.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    timed_out = False
    returncode = None
    stdout = stderr = ''
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, encoding='utf-8',
                                errors='replace', timeout=timeout)
        stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
        return result
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout, stderr = output_text(exc.stdout), output_text(exc.stderr)
        raise
    finally:
        (evidence / 'stdout.txt').write_text(stdout, encoding='utf-8')
        (evidence / 'stderr.txt').write_text(stderr, encoding='utf-8')
        (evidence / 'process.json').write_text(json.dumps({
            'timeout_seconds': timeout, 'elapsed_seconds': round(time.monotonic()-started, 3),
            'timed_out': timed_out, 'returncode': returncode,
            'scope': 'native process only; required screenshots are checked separately'
        }, indent=2)+'\n', encoding='utf-8')


def collect_runtime_evidence(exe, evidence):
    for log in ['log.txt', 'errors.txt', 'traceback.txt']:
        if (exe.parent / log).is_file():
            shutil.copy2(exe.parent / log, evidence / log)
    screenshots = exe.parent / 'reports/screenshots'
    if screenshots.exists():
        shutil.copytree(screenshots, evidence / 'screenshots', dirs_exist_ok=True)
    return screenshots


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument('--timeout', type=positive_timeout, default=DEFAULT_TEST_TIMEOUT,
                        help='Seconds allowed for the complete native suite (default: 900)')
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
        evidence = Path("reports/package")
        evidence.mkdir(parents=True, exist_ok=True)
        try:
            result = run_native_tests([str(exe), str(exe.parent), "test", "global", "--report-detailed", "--overwrite-screenshots", "--savedir", str(destination / "saves")],
                                      cwd=exe.parent, evidence=evidence, timeout=args.timeout)
        finally:
            screenshots = collect_runtime_evidence(exe, evidence)
        print(result.stdout)
        print(result.stderr)
        if result.returncode:
            raise SystemExit(result.returncode)
        required = ["first-choice", "settings", "chapter-prologue", "chapter-today",
                    "cg-letter", "branch-s04_open", "branch-s04_reserved", "revisit-choice",
                    "audio-true-voice", "audio-normal-voice"] + ["expression-" + name for name in
            ("normal", "smile", "happy", "sad", "angry", "surprised", "embarrassed")]
        # Once these candidate backgrounds are registered, missing native views
        # must block acceptance even if a generation bug omits their assertions.
        manifest = json.loads(Path('game/data/asset_manifest.json').read_text(encoding='utf-8'))
        backgrounds = {asset['id'] for asset in manifest['assets'] if asset['type'] == 'background'}
        required += [name for asset, name in (
            ('station_exit_covered', 'bg-exit-covered'),
            ('station_exit_after_rain', 'bg-exit-after-rain'),
            ('station_exit_after_rain', 'bg-s05_shared_path'),
            ('station_exit_after_rain', 'bg-s05_separate_path'),
            ('nearby_cafe', 'bg-nearby-cafe'),
        ) if asset in backgrounds]
        for name in required:
            file = screenshots / (name + ".png")
            if not file.is_file():
                raise SystemExit(f"Standalone EXE is missing UI evidence: {name}")
            with Image.open(file) as image:
                image.load()  # A present but truncated PNG is not usable evidence.
        print("Standalone Windows EXE: test process completed and UI evidence exists.")


if __name__ == "__main__":
    main()
