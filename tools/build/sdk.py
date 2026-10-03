"""Fetch the pinned official Ren'Py SDK and verify its published SHA-256."""
import argparse
import hashlib
import os
from pathlib import Path
import tarfile
import urllib.request
import zipfile

VERSION = "8.5.3"
HASHES = {
    "tar.bz2": "eb0a9be7f0fb13632fe25ceade9a8bed5a1b4d6b6e83bd19eeeb29e1a1bb4a45",
    "zip": "ff57648f9c04f27e381c48af6d8e3ee3cdec296bed4d3831f47f09b0a71b505e",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=Path(".runtime"))
    args = parser.parse_args()
    ext = "zip" if os.name == "nt" else "tar.bz2"
    args.destination.mkdir(parents=True, exist_ok=True)
    archive = args.destination / f"renpy-{VERSION}-sdk.{ext}"
    if not archive.exists():
        url = f"https://www.renpy.org/dl/{VERSION}/{archive.name}"
        with urllib.request.urlopen(url, timeout=180) as response, archive.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != HASHES[ext]:
        archive.unlink()
        raise SystemExit("SDK checksum mismatch; discarded download.")
    if ext == "zip":
        with zipfile.ZipFile(archive) as z:
            z.extractall(args.destination)
    else:
        with tarfile.open(archive) as tar:
            # Python's data filter strips original ownership and unsafe paths.
            tar.extractall(args.destination, filter="data")
    print((args.destination / f"renpy-{VERSION}-sdk").resolve())


if __name__ == "__main__":
    main()
