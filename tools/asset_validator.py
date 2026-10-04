"""Check asset files, content hashes, prompt provenance, voice text and references."""
import hashlib
import json
from pathlib import PurePosixPath
from tools.story_model import ROOT, load_story, scene_lines


def validate_assets(root=ROOT, story=None):
    story = story or load_story(root / "game/data/story.json")
    manifest = json.loads((root / "game/data/asset_manifest.json").read_text(encoding="utf-8"))
    voices = json.loads((root / "game/data/voice_manifest.json").read_text(encoding="utf-8"))["voices"]
    errors = []
    assets = manifest["assets"]
    ids = [a["id"] for a in assets]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate asset ID")
    lookup = {a["id"]: a for a in assets}
    paths = {a["file"] for a in assets}
    for a in assets:
        path = PurePosixPath(a["file"])
        if path.is_absolute() or ".." in path.parts or "\\" in a["file"]:
            errors.append(f"Unsafe asset path: {a['id']}")
            continue
        file = root / "game" / a["file"]
        if not file.is_file():
            errors.append(f"Missing asset: {a['file']}")
        elif hashlib.sha256(file.read_bytes()).hexdigest() != a.get("sha256"):
            errors.append(f"Hash mismatch: {a['file']}")
        if not a.get("source") or not a.get("license") or not a.get("version"):
            errors.append(f"Missing asset provenance: {a['id']}")
        if a.get("prompt") and not (root / a["prompt"]).is_file():
            errors.append(f"Missing prompt: {a['id']}")
        elif a.get("prompt_sha256") and hashlib.sha256((root / a["prompt"]).read_bytes()).hexdigest() != a["prompt_sha256"]:
            errors.append(f"Prompt hash mismatch: {a['id']}")
        if a.get("source_file"):
            source = root / a["source_file"]
            if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != a.get("source_sha256"):
                errors.append(f"Source asset missing/changed: {a['id']}")
    sprite_expressions = {a["expression"] for a in assets if a["type"] == "sprite"}
    for n in story["nodes"]:
        for k in ("background", "bgm", "ambient"):
            if n.get(k) and n[k] not in lookup:
                errors.append(f"{n['id']}: missing {k} {n[k]}")
        for expression in [n.get("sprite")] + [line.get("expression") for line in scene_lines(n)]:
            if expression and expression not in sprite_expressions:
                errors.append(f"{n['id']}: missing sprite expression {expression}")
    voice_ids = [v["voice_id"] for v in voices]
    if len(voice_ids) != len(set(voice_ids)):
        errors.append("Duplicate voice ID")
    by_voice = {v["voice_id"]: v for v in voices}
    bound_voice_ids = set()
    for n in story["nodes"]:
        for line in scene_lines(n):
            if line.get("voice"):
                voice = by_voice.get(line["voice"])
                bound_voice_ids.add(line["voice"])
                if not voice or voice["file"] not in paths:
                    errors.append(f"{line['id']}: missing voice {line['voice']}")
                elif voice["text"] != line["text"] or voice["line_id"] != line["id"] or voice["character"] != line["speaker"]:
                    errors.append(f"{line['id']}: voice/text mismatch")
    for voice_id in set(voice_ids) - bound_voice_ids:
        errors.append(f"Unbound voice: {voice_id}")
    return errors


def main():
    errors = validate_assets()
    for error in errors:
        print("ERROR:", error)
    print(f"Asset validation: {len(errors)} errors")
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
