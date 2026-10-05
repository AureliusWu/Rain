from __future__ import annotations

import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

from tools.build import sdk


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


class _InterruptedResponse(_Response):
    def __init__(self, payload: bytes):
        super().__init__(payload)
        self.calls = 0

    def read(self, size=-1):
        self.calls += 1
        if self.calls > 1:
            raise OSError("simulated interrupted download")
        return super().read(min(size, 16))


def _write_fake_sdk(root: Path, marker: str = "new") -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "renpy.py").write_text(marker, encoding="utf-8")
    interpreter = sdk._sdk_interpreter(root)
    interpreter.parent.mkdir(parents=True, exist_ok=True)
    interpreter.write_text(marker, encoding="utf-8")


def _zip_payload(valid: bool = True, marker: str = "new") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        base = f"renpy-{sdk.VERSION}-sdk/"
        bundle.writestr(base + "renpy.py", marker)
        if valid:
            interp = sdk._sdk_interpreter(Path(base)).as_posix()
            bundle.writestr(interp, marker)
    return buffer.getvalue()


class SdkRecoveryTests(unittest.TestCase):
    def test_existing_usable_sdk_skips_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)
            installed = destination / f"renpy-{sdk.VERSION}-sdk"
            _write_fake_sdk(installed, "old")
            opener = mock.Mock(side_effect=AssertionError("network should not be used"))
            result = sdk.ensure_sdk(destination, ext="zip", expected_sha256="0" * 64, opener=opener)
            self.assertEqual(result, installed.resolve())
            opener.assert_not_called()

    def test_corrupt_cached_archive_is_redownloaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)
            archive = destination / f"renpy-{sdk.VERSION}-sdk.zip"
            archive.write_bytes(b"corrupt")
            payload = _zip_payload()
            expected = hashlib.sha256(payload).hexdigest()
            result = sdk.ensure_sdk(
                destination,
                ext="zip",
                expected_sha256=expected,
                opener=lambda *args, **kwargs: _Response(payload),
            )
            self.assertTrue(sdk.sdk_is_usable(result))
            self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), expected)

    def test_interrupted_download_preserves_existing_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)
            installed = destination / f"renpy-{sdk.VERSION}-sdk"
            installed.mkdir()
            (installed / "old-marker").write_text("keep", encoding="utf-8")
            payload = _zip_payload()
            expected = hashlib.sha256(payload).hexdigest()
            with self.assertRaises(OSError):
                sdk.ensure_sdk(
                    destination,
                    ext="zip",
                    expected_sha256=expected,
                    opener=lambda *args, **kwargs: _InterruptedResponse(payload),
                )
            self.assertEqual((installed / "old-marker").read_text(encoding="utf-8"), "keep")
            self.assertFalse((destination / f"renpy-{sdk.VERSION}-sdk.zip.part").exists())

    def test_checksum_failure_discards_partial_and_preserves_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)
            installed = destination / f"renpy-{sdk.VERSION}-sdk"
            installed.mkdir()
            (installed / "old-marker").write_text("keep", encoding="utf-8")
            payload = _zip_payload()
            with self.assertRaises(RuntimeError):
                sdk.ensure_sdk(
                    destination,
                    ext="zip",
                    expected_sha256="0" * 64,
                    opener=lambda *args, **kwargs: _Response(payload),
                )
            self.assertTrue((installed / "old-marker").exists())
            self.assertFalse((destination / f"renpy-{sdk.VERSION}-sdk.zip").exists())
            self.assertFalse((destination / f"renpy-{sdk.VERSION}-sdk.zip.part").exists())

    def test_extract_failure_preserves_existing_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)
            installed = destination / f"renpy-{sdk.VERSION}-sdk"
            installed.mkdir()
            (installed / "old-marker").write_text("keep", encoding="utf-8")
            payload = _zip_payload(valid=False)
            expected = hashlib.sha256(payload).hexdigest()
            archive = destination / f"renpy-{sdk.VERSION}-sdk.zip"
            archive.write_bytes(payload)
            with self.assertRaises(RuntimeError):
                sdk.ensure_sdk(destination, ext="zip", expected_sha256=expected)
            self.assertEqual((installed / "old-marker").read_text(encoding="utf-8"), "keep")

    def test_successful_recovery_replaces_broken_runtime_and_cleans_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)
            installed = destination / f"renpy-{sdk.VERSION}-sdk"
            installed.mkdir()
            (installed / "old-marker").write_text("old", encoding="utf-8")
            payload = _zip_payload(marker="fresh")
            expected = hashlib.sha256(payload).hexdigest()
            archive = destination / f"renpy-{sdk.VERSION}-sdk.zip"
            archive.write_bytes(payload)
            result = sdk.ensure_sdk(destination, ext="zip", expected_sha256=expected)
            self.assertTrue(sdk.sdk_is_usable(result))
            self.assertFalse((result / "old-marker").exists())
            self.assertEqual((result / "renpy.py").read_text(encoding="utf-8"), "fresh")
            self.assertFalse((destination / f".renpy-{sdk.VERSION}-sdk.backup").exists())


if __name__ == "__main__":
    unittest.main()
