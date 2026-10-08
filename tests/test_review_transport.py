import base64
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.build.review_transport import (MAX_ENCODED_BYTES, canonical, decode_envelope,
    encoded_size, envelope_lines, load_bundles, pack_media, sha256, validate_audit, write_bundles)


CANDIDATE = "a" * 40
RUN_ID = 123


def audit_fixture(sizes=(12000, 18000, 5000)):
    screenshots, inspected, media = [], [], []
    for index, size in enumerate(sizes):
        raw = bytes([index + 1]) * size
        original = {"scope": "standalone", "name": f"view-{index}",
                    "path": f"reports/package/screenshots/view-{index}.png",
                    "pixels": [1920, 1080], "sha256": sha256(b"png" + bytes([index]))}
        screenshots.append(original)
        inspected.append({**original, "status": "needs_direct_view", "inspection_copy": {
            "source_png_sha256": original["sha256"], "sha256": sha256(raw), "pixels": original["pixels"]}})
        media.append({"scope": original["scope"], "name": original["name"],
                      "source_png_sha256": original["sha256"], "jpeg_sha256": sha256(raw),
                      "pixels": original["pixels"], "base64": base64.b64encode(raw).decode("ascii")})
    return {"machine": {"candidate_commit": CANDIDATE, "run_id": RUN_ID, "version": "1.1.1",
                        "screenshots": screenshots, "title": "雨停之前"},
            "visual": {"candidate_commit": CANDIDATE, "run_id": RUN_ID, "version": "1.1.1",
                       "inspected": inspected}, "media": media}


class ReviewBundleTests(unittest.TestCase):
    def test_actual_bytes_determine_groups_and_original_envelope_is_exact(self):
        audit = audit_fixture()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "review"
            manifest = write_bundles(audit, root, limit=43000)
            self.assertEqual([len(item["copies"]) for item in manifest["groups"]], [1, 2])
            self.assertTrue(all(item["encoded_bytes"] <= 43000 for item in manifest["groups"]))
            loaded, records, payloads = load_bundles(root, CANDIDATE, RUN_ID)
            self.assertEqual(loaded, manifest)
            reconstructed = {**records, "media": [image for item in loaded["groups"] for image in payloads[item["path"]]]}
            self.assertEqual(canonical(reconstructed), canonical(audit))
            self.assertEqual(manifest["original_audit"]["sha256"], sha256(canonical(audit)))

    def test_oversized_single_copy_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "review"
            with self.assertRaisesRegex(ValueError, "One inspection copy exceeds"):
                write_bundles(audit_fixture(), root, limit=20000)
            self.assertFalse(root.exists())

    def test_oversized_records_are_rejected_before_writing(self):
        audit = audit_fixture(())
        audit["machine"]["large_record"] = "x" * 10000
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "review"
            with self.assertRaisesRegex(ValueError, "Review records exceed"):
                write_bundles(audit, root, limit=8000)
            self.assertFalse(root.exists())

    def test_no_new_images_still_exports_records_and_empty_matrix(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "review"
            write_bundles(audit_fixture(()), root)
            output = Path(temp) / "github-output"
            result = subprocess.run([sys.executable, "-m", "tools.build.review_transport", "--root", str(root),
                "--candidate", CANDIDATE, "--run-id", str(RUN_ID), "--group", "records", "--github-output", str(output)],
                capture_output=True, text=True, check=True, timeout=10)
            metadata, raw = decode_envelope(result.stdout)
            self.assertEqual(metadata["label"], "records")
            self.assertEqual(json.loads(raw)["manifest"]["groups"], [])
            self.assertEqual(output.read_text(), "groups=[]\n")

    def test_wrong_candidate_or_run_cannot_read_the_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "review"
            write_bundles(audit_fixture(), root)
            for candidate, run_id in [("b" * 40, RUN_ID), (CANDIDATE, RUN_ID + 1)]:
                with self.subTest(candidate=candidate, run_id=run_id), self.assertRaisesRegex(ValueError, "identity differs"):
                    load_bundles(root, candidate, run_id)

    def test_tampered_missing_or_unlisted_files_are_rejected(self):
        for mode in ("tampered", "missing", "unlisted"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "review"
                manifest = write_bundles(audit_fixture(), root)
                image = root / manifest["groups"][0]["path"]
                if mode == "tampered":
                    image.write_bytes(image.read_bytes() + b" ")
                    error, message = ValueError, "SHA-256 or length differs"
                elif mode == "missing":
                    image.unlink()
                    error, message = FileNotFoundError, ""
                else:
                    (root / "unlisted.json").write_text("{}")
                    error, message = ValueError, "file set differs"
                with self.assertRaisesRegex(error, message):
                    load_bundles(root, CANDIDATE, RUN_ID)

    def test_group_order_path_and_original_seal_are_checked(self):
        for mode in ("path", "order", "seal"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "review"
                manifest = write_bundles(audit_fixture(), root, limit=43000)
                if mode == "path":
                    manifest["groups"][0]["path"] = "../outside.json"
                    message = "group order or path"
                elif mode == "order":
                    manifest["groups"].reverse()
                    message = "group order or path"
                else:
                    manifest["original_audit"]["sha256"] = "0" * 64
                    message = "original audit seal differs"
                (root / "manifest.json").write_bytes(canonical(manifest))
                with self.assertRaisesRegex(ValueError, message):
                    load_bundles(root, CANDIDATE, RUN_ID)

    def test_copy_set_hash_and_png_binding_cannot_change_silently(self):
        for mode in ("missing", "duplicate", "hash", "png", "pixels", "identity"):
            with self.subTest(mode=mode):
                audit = audit_fixture()
                if mode == "missing":
                    audit["media"].pop()
                elif mode == "duplicate":
                    audit["media"].append(copy.deepcopy(audit["media"][0]))
                elif mode == "hash":
                    audit["media"][0]["base64"] = base64.b64encode(b"changed").decode()
                elif mode == "png":
                    audit["media"][0]["source_png_sha256"] = "0" * 64
                elif mode == "pixels":
                    audit["visual"]["inspected"][0]["pixels"] = [1280, 720]
                else:
                    audit["visual"]["run_id"] += 1
                with self.assertRaises(ValueError):
                    validate_audit(audit)

    def test_existing_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "already exists"):
                write_bundles(audit_fixture(), Path(temp))


class ReviewEnvelopeTests(unittest.TestCase):
    def envelope(self):
        raw = canonical({"content": "x" * 20000})
        manifest = {"candidate_commit": CANDIDATE, "run_id": RUN_ID, "payload_limit": MAX_ENCODED_BYTES}
        return raw, manifest, list(envelope_lines("records", raw, manifest))

    def test_timestamped_crlf_terminal_log_round_trip(self):
        raw, manifest, lines = self.envelope()
        log = "\r\n".join("2026-10-08T23:00:00.000Z " + line for line in lines)
        metadata, restored = decode_envelope(log)
        self.assertEqual(restored, raw)
        self.assertEqual(metadata, {"label": "records", "candidate_commit": CANDIDATE,
            "run_id": RUN_ID, "manifest_sha256": sha256(canonical(manifest)), "payload_sha256": sha256(raw)})

    def test_missing_duplicate_reordered_and_changed_chunks_are_rejected(self):
        _, _, original = self.envelope()
        variants = [original[:-1], original + [original[-1]], original[:1] + original[2:],
                    original[:2] + [original[1]] + original[2:],
                    original[:1] + [original[2], original[1]] + original[3:]]
        changed = list(original)
        changed[1] = changed[1][:-1] + ("A" if changed[1][-1] != "A" else "B")
        variants.append(changed)
        for lines in variants:
            with self.subTest(lines=len(lines)), self.assertRaises(ValueError):
                decode_envelope("\n".join(lines))

    def test_invalid_limits_and_unbounded_log_are_rejected(self):
        for limit in (0, True, MAX_ENCODED_BYTES + 1):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                pack_media([], limit)
        _, _, lines = self.envelope()
        fields = lines[-1].split()
        fields[3] = str(MAX_ENCODED_BYTES + 1)
        lines[-1] = " ".join(fields)
        with self.assertRaisesRegex(ValueError, "payload limit"):
            decode_envelope("\n".join(lines))
        self.assertEqual(encoded_size(3), 4)
        self.assertEqual(encoded_size(4), 8)
