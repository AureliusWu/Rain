"""Project-relative asset paths shared by importers and validators."""
import hashlib
import re
from pathlib import PurePosixPath

ASSET_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def project_file(root, relative, area, *, must_exist=True):
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative or "\x00" in relative:
        raise ValueError(f"Unsafe path: {relative!r}")
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or path.parts[0] != area or path.as_posix() != relative:
        raise ValueError(f"Path must stay under {area}: {relative!r}")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root.resolve() / area)
    except ValueError:
        raise ValueError(f"Path escapes {area}: {relative!r}") from None
    if must_exist and not resolved.is_file():
        raise ValueError(f"Missing file: {relative}")
    return resolved


def sha256(data):
    return hashlib.sha256(data).hexdigest()
