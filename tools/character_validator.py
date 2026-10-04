"""Check the fixed heroine expression set; facial identity still needs visual review."""
import argparse
import hashlib
import json
from PIL import Image, ImageChops
from tools.story_model import ROOT, load_story, scene_lines


REGISTRY = "prompts/character/heroine_expressions_v1.json"


def geometry(reference, candidate):
    """Compare opaque silhouettes, without repainting either image."""
    if reference.size != candidate.size:
        return {"size_matches": False, "silhouette_iou": 0.0, "bbox_delta": None}
    masks = [im.getchannel("A").point(lambda value: 255 if value > 128 else 0)
             for im in (reference, candidate)]
    boxes = [mask.getbbox() for mask in masks]
    intersection = ImageChops.multiply(*masks).histogram()[255]
    union = ImageChops.lighter(*masks).histogram()[255]
    return {
        "size_matches": True,
        "silhouette_iou": intersection / union if union else 0.0,
        "bbox_delta": max(abs(a-b) for a, b in zip(*boxes)) if all(boxes) else None,
    }


def validate_characters(root=ROOT, assets=None, story=None):
    registry = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    if assets is None:
        assets = json.loads((root / "game/data/asset_manifest.json").read_text(encoding="utf-8"))["assets"]
    story = story or load_story(root / "game/data/story.json")
    sprites = [a for a in assets if a["type"] == "sprite" and a.get("character") == "heroine"]
    by_expression = {a["expression"]: a for a in sprites}
    errors, metrics = [], {}
    expected = set(registry["expressions"])
    if set(by_expression) != expected or len(sprites) != len(expected):
        errors.append("Heroine expression set must contain exactly: " + ", ".join(sorted(expected)))
    referenced = {n.get("sprite") for n in story["nodes"]}
    referenced.update(line.get("expression") for n in story["nodes"] for line in scene_lines(n))
    for expression in sorted(expected - referenced):
        errors.append(f"Unused heroine expression: {expression}")
    target = root / registry["edit_target"]
    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != registry["edit_target_sha256"]:
        errors.append("Expression edit target is missing or changed")
    if "normal" not in by_expression:
        return errors, metrics
    with Image.open(root / "game" / by_expression["normal"]["file"]) as opened:
        baseline = opened.convert("RGBA")
    for expression, asset in by_expression.items():
        path = root / "game" / asset["file"]
        if not path.is_file():
            errors.append(f"Missing expression image: {expression}")
            continue
        with Image.open(path) as candidate:
            if candidate.size != tuple(registry["game_canvas"]) or "A" not in candidate.getbands():
                errors.append(f"Expression canvas/alpha differs: {expression}")
                continue
            low, high = candidate.getchannel("A").getextrema()
            corners = [(0, 0), (candidate.width-1, 0), (0, candidate.height-1), (candidate.width-1, candidate.height-1)]
            if low != 0 or high < 250 or any(candidate.getchannel("A").getpixel(p) for p in corners):
                errors.append(f"Expression has invalid transparency: {expression}")
            metric = geometry(baseline, candidate)
            metrics[expression] = metric
            if metric["silhouette_iou"] < registry["min_silhouette_iou"] or metric["bbox_delta"] is None or metric["bbox_delta"] > registry["max_bbox_delta"]:
                errors.append(f"Expression position/silhouette drift: {expression}")
        source = root / asset["source_file"]
        with Image.open(source) as image:
            if image.size != tuple(registry["source_canvas"]):
                errors.append(f"Expression source canvas differs: {expression}")
        if asset.get("prompt") != registry["expressions"][expression]["prompt"]:
            errors.append(f"Expression prompt differs from registry: {expression}")
        if expression != "normal" and (asset.get("reference_source_file") != registry["edit_target"] or asset.get("reference_sha256") != registry["edit_target_sha256"]):
            errors.append(f"Expression uses another baseline: {expression}")
    if len({a["sha256"] for a in sprites}) != len(sprites):
        errors.append("Duplicate expression image content")
    return errors, metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=str)
    args = parser.parse_args()
    errors, metrics = validate_characters()
    report = {"errors": errors, "geometry": metrics, "limitation": "Geometry checks do not prove facial identity or emotional meaning; visual review required."}
    if args.report:
        path = ROOT / args.report
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for error in errors:
        print("ERROR:", error)
    print(f"Character validation: {len(metrics)} expressions, {len(errors)} errors")
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
