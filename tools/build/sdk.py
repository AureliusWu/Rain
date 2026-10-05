"""Fetch the pinned official Ren'Py SDK with crash-safe cache recovery."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile

VERSION = "8.5.3"
HASHES = {
    "tar.bz2": "eb0a9be7f0fb13632fe25ceade9a8bed5a1b4d6b6e83bd19eeeb29e1a1bb4a45",
    "zip": "ff57648f9c04f27e381c48af6d8e3ee3cdec296bed4d3831f47f09b0a71b505e",
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _default_extension() -> str:
    return "zip" if os.name == "nt" else "tar.bz2"


def _sdk_interpreter(root: Path) -> Path:
    if os.name == "nt":
        return root / "lib" / "py3-windows-x86_64" / "python.exe"
    return root / "lib" / "py3-linux-x86_64" / "python"


def sdk_is_usable(root: Path) -> bool:
    return (
        root.is_dir()
        and (root / "renpy.py").is_file()
        and _sdk_interpreter(root).is_file()
    )


def archive_is_valid(path: Path, expected_sha256: str) -> bool:
    return path.is_file() and _sha256_file(path) == expected_sha256


def cache_status(destination: Path, *, ext: str | None = None, expected_sha256: str | None = None) -> dict[str, object]:
    ext = ext or _default_extension()
    expected_sha256 = expected_sha256 or HASHES[ext]
    archive = destination / f"renpy-{VERSION}-sdk.{ext}"
    sdk_root = destination / f"renpy-{VERSION}-sdk"
    return {
        "sdk_path": str(sdk_root),
        "sdk_usable": sdk_is_usable(sdk_root),
        "archive_path": str(archive),
        "archive_present": archive.exists(),
        "archive_valid": archive_is_valid(archive, expected_sha256) if archive.exists() else False,
        "partial_present": archive.with_name(archive.name + ".part").exists(),
    }


def _download_atomic(url: str, archive: Path, expected_sha256: str, *, opener=urllib.request.urlopen) -> None:
    partial = archive.with_name(archive.name + ".part")
    partial.unlink(missing_ok=True)
    digest = hashlib.sha256()
    try:
        with opener(url, timeout=180) as response, partial.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                output.write(chunk)
        if digest.hexdigest() != expected_sha256:
            raise RuntimeError("SDK checksum mismatch; discarded download.")
        os.replace(partial, archive)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise


def _extract_candidate(archive: Path, destination: Path, ext: str) -> tuple[Path, Path]:
    temp_root = Path(tempfile.mkdtemp(prefix=f".renpy-{VERSION}-extract-", dir=destination))
    try:
        if ext == "zip":
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(temp_root)
        else:
            with tarfile.open(archive) as bundle:
                bundle.extractall(temp_root, filter="data")
        candidate = temp_root / f"renpy-{VERSION}-sdk"
        if not sdk_is_usable(candidate):
            raise RuntimeError("Extracted SDK is incomplete; existing runtime was preserved.")
        return temp_root, candidate
    except BaseException:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise


def _install_candidate(candidate: Path, sdk_root: Path) -> None:
    backup = sdk_root.with_name(f".{sdk_root.name}.backup")
    if backup.exists():
        shutil.rmtree(backup, ignore_errors=True)

    moved_old = False
    try:
        if sdk_root.exists():
            os.replace(sdk_root, backup)
            moved_old = True
        os.replace(candidate, sdk_root)
    except BaseException:
        if not sdk_root.exists() and moved_old and backup.exists():
            os.replace(backup, sdk_root)
        raise
    else:
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)


def ensure_sdk(
    destination: Path,
    *,
    ext: str | None = None,
    expected_sha256: str | None = None,
    opener=urllib.request.urlopen,
) -> Path:
    ext = ext or _default_extension()
    expected_sha256 = expected_sha256 or HASHES[ext]
    destination.mkdir(parents=True, exist_ok=True)

    archive = destination / f"renpy-{VERSION}-sdk.{ext}"
    sdk_root = destination / f"renpy-{VERSION}-sdk"

    if sdk_is_usable(sdk_root):
        return sdk_root.resolve()

    if archive.exists() and not archive_is_valid(archive, expected_sha256):
        archive.unlink()

    if not archive.exists():
        url = f"https://www.renpy.org/dl/{VERSION}/{archive.name}"
        _download_atomic(url, archive, expected_sha256, opener=opener)

    temp_root, candidate = _extract_candidate(archive, destination, ext)
    try:
        _install_candidate(candidate, sdk_root)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    if not sdk_is_usable(sdk_root):
        raise RuntimeError("SDK installation did not produce a usable runtime.")
    return sdk_root.resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=Path(".runtime"))
    parser.add_argument("--check-cache", action="store_true", help="Report cache state without downloading.")
    args = parser.parse_args()
    if args.check_cache:
        status = cache_status(args.destination)
        for key, value in status.items():
            print(f"{key}={value}")
        if not status["sdk_usable"] and not status["archive_valid"]:
            raise SystemExit(2)
        return
    print(ensure_sdk(args.destination))


if __name__ == "__main__":
    main()
