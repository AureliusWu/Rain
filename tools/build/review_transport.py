"""Transport sealed native review evidence through bounded, independently checked logs.

This module uses only the standard library so the same artifact can be checked
and exported by small Linux jobs after the actual Windows audit has finished.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import sys

MAX_ENCODED_BYTES = 4 * 1024 * 1024
CHUNK_SIZE = 8000
MAX_GROUPS = 128
PREFIX = "REVIEW_EXPORT"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(data):
    return json.dumps(data, ensure_ascii=True, separators=(",", ":")).encode("ascii")


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded_size(raw_bytes):
    return 4 * ((raw_bytes + 2) // 3)


def key(item):
    return item["scope"], item["name"]


def validate_audit(audit):
    """Keep each inspection copy bound to its Windows PNG and review entry."""
    require(set(audit) == {"machine", "visual", "media"}, "Unexpected audit fields")
    machine, visual, media = audit["machine"], audit["visual"], audit["media"]
    candidate, run_id = machine["candidate_commit"], machine["run_id"]
    require(re.fullmatch(r"[0-9a-f]{40}", candidate), "Invalid candidate")
    require(type(run_id) is int and run_id > 0, "Invalid run ID")
    require(visual["candidate_commit"] == candidate and visual["run_id"] == run_id
            and visual["version"] == machine["version"], "Audit identity differs")
    screenshots = {key(item): item for item in machine["screenshots"]}
    require(len(screenshots) == len(machine["screenshots"]), "Duplicate native screenshot")
    inspected = {key(item): item for item in visual["inspected"]}
    require(len(inspected) == len(visual["inspected"]), "Duplicate visual entry")
    needed = {}
    for identity, item in inspected.items():
        original = screenshots.get(identity)
        require(original is not None and all(item[field] == original[field]
                for field in ("path", "pixels", "sha256")), "Visual PNG binding differs")
        require(item["status"] in ("reuse_candidate", "needs_direct_view"), "Unknown visual status")
        if item["status"] == "needs_direct_view":
            needed[identity] = item
    require(len({key(item) for item in media}) == len(media), "Duplicate inspection copy")
    require({key(item) for item in media} == set(needed), "Inspection copy set differs")
    for item in media:
        original = needed[key(item)]
        copy = original["inspection_copy"]
        require(item["source_png_sha256"] == original["sha256"] == copy["source_png_sha256"]
                and item["jpeg_sha256"] == copy["sha256"]
                and item["pixels"] == original["pixels"] == copy["pixels"], "Inspection copy binding differs")
        raw = base64.b64decode(item["base64"], validate=True)
        require(sha256(raw) == item["jpeg_sha256"], "Inspection copy SHA-256 differs")


def descriptor(path, raw):
    return {"path": path, "bytes": len(raw), "encoded_bytes": encoded_size(len(raw)), "sha256": sha256(raw)}


def pack_media(media, limit=MAX_ENCODED_BYTES):
    """Pack whole copies by serialized byte size, never by an assumed image count."""
    require(type(limit) is int and 0 < limit <= MAX_ENCODED_BYTES, "Invalid payload limit")
    groups, current = [], []
    for item in media:
        require(encoded_size(len(canonical([item]))) <= limit,
                "One inspection copy exceeds the payload limit; use a file transfer")
        if current and encoded_size(len(canonical(current + [item]))) > limit:
            groups.append(current)
            current = []
        current.append(item)
    if current:
        groups.append(current)
    require(len(groups) <= MAX_GROUPS, "Too many inspection groups")
    return groups


def write_bundles(audit, destination, *, limit=MAX_ENCODED_BYTES):
    validate_audit(audit)
    destination = Path(destination)
    require(not destination.exists(), "Review destination already exists; inspect before rerun")
    records = {"machine": audit["machine"], "visual": audit["visual"]}
    record_raw = canonical(records)
    files = {"records.json": record_raw}
    groups = []
    for index, media in enumerate(pack_media(audit["media"], limit)):
        path = f"groups/images-{index:04d}.json"
        raw = canonical(media)
        files[path] = raw
        item = descriptor(path, raw)
        item["label"] = f"images-{index:04d}"
        item["copies"] = [{field: image[field] for field in
                           ("scope", "name", "source_png_sha256", "jpeg_sha256", "pixels")}
                          for image in media]
        groups.append(item)
    original = canonical(audit)
    manifest = {"schema_version": 1, "candidate_commit": audit["machine"]["candidate_commit"],
                "run_id": audit["machine"]["run_id"], "version": audit["machine"]["version"],
                "payload_limit": limit, "original_audit": {"sha256": sha256(original), "bytes": len(original)},
                "records": descriptor("records.json", record_raw), "groups": groups}
    record_envelope = canonical({"manifest": manifest, "records": records})
    require(encoded_size(len(record_envelope)) <= limit, "Review records exceed the payload limit")
    files["manifest.json"] = canonical(manifest)
    destination.mkdir(parents=True)
    for path, raw in files.items():
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return manifest


def load_bundles(root, candidate, run_id):
    root = Path(root)
    raw_manifest = (root / "manifest.json").read_bytes()
    manifest = json.loads(raw_manifest)
    require(raw_manifest == canonical(manifest), "Manifest is not canonical")
    require(manifest["schema_version"] == 1 and manifest["candidate_commit"] == candidate
            and type(manifest["run_id"]) is int and manifest["run_id"] == run_id, "Transport identity differs")
    limit = manifest["payload_limit"]
    require(type(limit) is int and 0 < limit <= MAX_ENCODED_BYTES, "Invalid payload limit")
    require(manifest["records"]["path"] == "records.json", "Invalid record path")
    groups = manifest["groups"]
    require(len(groups) <= MAX_GROUPS, "Too many inspection groups")
    expected = {"manifest.json", "records.json"}
    payloads = {}
    for index, item in enumerate([manifest["records"], *groups]):
        if index:
            label = f"images-{index-1:04d}"
            require(item["label"] == label and item["path"] == f"groups/{label}.json", "Invalid group order or path")
            expected.add(item["path"])
        path = root / item["path"]
        require(not path.is_symlink(), "Symlink in review bundle")
        raw = path.read_bytes()
        require(all(item[field] == descriptor(item["path"], raw)[field]
                    for field in ("bytes", "encoded_bytes", "sha256")), "Bundle SHA-256 or length differs")
        require(encoded_size(len(raw)) <= limit, "Bundle exceeds the payload limit")
        data = json.loads(raw)
        require(raw == canonical(data), "Bundle is not canonical")
        payloads[item["path"]] = data
    require({path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()} == expected,
            "Review bundle file set differs")
    records = payloads["records.json"]
    media = []
    for item in groups:
        copies = payloads[item["path"]]
        require(item["copies"] == [{field: image[field] for field in
                ("scope", "name", "source_png_sha256", "jpeg_sha256", "pixels")} for image in copies],
                "Group copy identities differ")
        media.extend(copies)
    audit = {"machine": records["machine"], "visual": records["visual"], "media": media}
    validate_audit(audit)
    require(audit["machine"]["candidate_commit"] == candidate and audit["machine"]["run_id"] == run_id
            and audit["machine"]["version"] == manifest["version"], "Records identity differs")
    original = canonical(audit)
    require(manifest["original_audit"] == {"sha256": sha256(original), "bytes": len(original)},
            "Reassembled original audit seal differs")
    require(encoded_size(len(canonical({"manifest": manifest, "records": records}))) <= limit,
            "Review records exceed the payload limit")
    return manifest, records, payloads


def envelope_lines(label, raw, manifest):
    require(label == "records" or re.fullmatch(r"images-\d{4}", label), "Invalid envelope label")
    encoded = base64.b64encode(raw).decode("ascii")
    require(len(encoded) <= manifest["payload_limit"] <= MAX_ENCODED_BYTES, "Envelope exceeds the payload limit")
    yield f'{PREFIX}_BEGIN {label} {manifest["candidate_commit"]} {manifest["run_id"]} {sha256(canonical(manifest))}'
    for offset in range(0, len(encoded), CHUNK_SIZE):
        yield f"{PREFIX}_CHUNK {offset // CHUNK_SIZE:05d} {encoded[offset:offset + CHUNK_SIZE]}"
    yield f"{PREFIX}_END {sha256(raw)} {len(raw)} {len(encoded)} {(len(encoded) + CHUNK_SIZE - 1) // CHUNK_SIZE}"


def decode_envelope(log):
    """Reject incomplete, duplicated, reordered or tampered terminal-log envelopes."""
    log = log.replace("\r\n", "\n")
    begins = re.findall(rf"(?m)^.*?{PREFIX}_BEGIN (records|images-\d{{4}}) ([0-9a-f]{{40}}) (\d+) ([0-9a-f]{{64}})\s*$", log)
    ends = re.findall(rf"(?m)^.*?{PREFIX}_END ([0-9a-f]{{64}}) (\d+) (\d+) (\d+)\s*$", log)
    chunks = re.findall(rf"(?m)^.*?{PREFIX}_CHUNK (\d{{5}}) ([A-Za-z0-9+/=]+)\s*$", log)
    require(len(begins) == len(ends) == 1, "Missing or duplicate envelope boundary")
    seal, raw_size, encoded_length, count = ends[0]
    require(0 < int(encoded_length) <= MAX_ENCODED_BYTES, "Envelope exceeds the payload limit")
    require([int(index) for index, _ in chunks] == list(range(int(count)))
            and int(count) == (int(encoded_length) + CHUNK_SIZE - 1) // CHUNK_SIZE, "Envelope chunks differ")
    encoded = "".join(value for _, value in chunks)
    require(len(encoded) == int(encoded_length), "Encoded envelope length differs")
    require(all(len(value) == CHUNK_SIZE for _, value in chunks[:-1]), "Envelope chunk size differs")
    raw = base64.b64decode(encoded, validate=True)
    require(len(raw) == int(raw_size) and sha256(raw) == seal, "Envelope SHA-256 or length differs")
    label, candidate, run_id, manifest_sha = begins[0]
    return {"label": label, "candidate_commit": candidate, "run_id": int(run_id),
            "manifest_sha256": manifest_sha, "payload_sha256": seal}, raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--group", required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    manifest, records, payloads = load_bundles(args.root, args.candidate, args.run_id)
    if args.group == "records":
        raw = canonical({"manifest": manifest, "records": records})
    else:
        require(args.group in [item["label"] for item in manifest["groups"]], "Unknown inspection group")
        raw = canonical(payloads[f"groups/{args.group}.json"])
    for line in envelope_lines(args.group, raw, manifest):
        print(line, flush=True)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as stream:
            stream.write("groups=" + json.dumps([item["label"] for item in manifest["groups"]], separators=(",", ":")) + "\n")
    print("Original Windows audit seal and all inspection-copy bindings verified.", file=sys.stderr)


if __name__ == "__main__":
    main()
