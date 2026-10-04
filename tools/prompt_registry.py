"""Index versioned prompts; validate saved requests without generating content."""
import argparse
import json
import re
from pathlib import Path
from tools.asset_paths import project_file, sha256
from tools.story_model import ROOT, ID

REGISTRY = "prompts/registry.json"
VERSION = re.compile(r"_v([1-9][0-9]*)\.(md|json)$")


def render_registry(root=ROOT):
    entries = []
    for file in sorted((root / "prompts").rglob("*")):
        if not file.is_file() or file.name in {"registry.json", "README.md"}:
            continue
        match = VERSION.search(file.name)
        if not match:
            raise ValueError(f"Prompt filename needs _vN: {file.relative_to(root)}")
        relative = file.relative_to(root).as_posix()
        project_file(root, relative, "prompts")
        entry = {"id": "_".join(file.relative_to(root / "prompts").with_suffix("").parts),
                 "version": int(match[1]), "kind": file.relative_to(root / "prompts").parts[0],
                 "file": relative, "sha256": sha256(file.read_bytes())}
        # The saved exact requests declare their shared component file.
        if file.suffix == ".md":
            components = re.findall(r"Shared components: `([^`]+)`", file.read_text(encoding="utf-8"))
            if components:
                entry["components"] = ["_".join(Path(p).relative_to("prompts").with_suffix("").parts) for p in components]
        entries.append(entry)
    return {"schema_version": 1, "prompts": entries}


def validate_registry(root=ROOT, registry=None):
    errors = []
    try:
        registry = registry if registry is not None else json.loads(project_file(root, REGISTRY, "prompts").read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return [f"Prompt registry: {exc}"]
    if registry.get("schema_version") != 1 or not isinstance(registry.get("prompts"), list):
        return ["Unsupported Prompt registry schema"]
    ids, files = set(), set()
    for entry in registry["prompts"]:
        name = entry.get("id", "")
        if not ID.fullmatch(name) or name in ids:
            errors.append(f"Duplicate/invalid Prompt ID: {name}")
        ids.add(name)
        relative = entry.get("file", "")
        if relative in files:
            errors.append(f"Duplicate Prompt file: {relative}")
        files.add(relative)
        match = VERSION.search(relative)
        if not match or type(entry.get("version")) is not int or entry["version"] != int(match[1]):
            errors.append(f"Prompt version disagrees with filename: {name}")
        try:
            file = project_file(root, relative, "prompts")
            if sha256(file.read_bytes()) != entry.get("sha256"):
                errors.append(f"Prompt hash mismatch: {name}")
        except (ValueError, OSError) as exc:
            errors.append(f"{name}: {exc}")
    for entry in registry["prompts"]:
        for component in entry.get("components", []):
            if component not in ids or component == entry["id"]:
                errors.append(f"Missing/invalid Prompt component: {component}")
    try:
        if registry != render_registry(root):
            errors.append("Prompt registry differs from versioned files; review changes, then run --write")
    except (ValueError, OSError) as exc:
        errors.append(str(exc))
    return errors


def prompt_by_file(root, relative):
    project_file(root, relative, "prompts")
    data = json.loads(project_file(root, REGISTRY, "prompts").read_text(encoding="utf-8"))
    matches = [p for p in data["prompts"] if p["file"] == relative]
    if len(matches) != 1 or sha256((root / relative).read_bytes()) != matches[0]["sha256"]:
        raise ValueError(f"Prompt is unregistered or changed: {relative}")
    return matches[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true", help="Explicitly register reviewed current prompt files")
    action.add_argument("--check", action="store_true", help="Reject missing, changed or duplicate records")
    args = parser.parse_args()
    if args.write:
        data = render_registry()
        errors = validate_registry(ROOT, data)
        if errors:
            parser.exit(1, "Registry rejected: " + "\n".join(errors) + "\n")
        (ROOT / REGISTRY).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Registered {len(data['prompts'])} versioned Prompts.")
    else:
        errors = validate_registry()
        for error in errors:
            print("ERROR:", error)
        print(f"Prompt registry: {len(errors)} errors")
        raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
