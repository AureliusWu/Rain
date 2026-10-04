"""Import a reviewed image without painting or changing its identity."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageOps
from tools.story_model import ROOT


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path, help="Source already stored under assets_source")
    p.add_argument("--id", required=True)
    p.add_argument("--type", choices=["background", "sprite", "cg", "ui"], required=True)
    p.add_argument("--output", required=True, help="Path relative to game")
    p.add_argument("--prompt", required=True, type=Path)
    p.add_argument("--version", type=int, default=1)
    p.add_argument("--expression", default="normal")
    p.add_argument("--reference-source", type=Path, help="Original edit target under assets_source")
    p.add_argument("--prompt-components", type=Path, help="Versioned shared components under prompts")
    args = p.parse_args()
    source = args.source.resolve()
    source_relative = source.relative_to(ROOT / "assets_source")
    prompt = args.prompt.resolve()
    prompt.relative_to(ROOT / "prompts")
    output = (ROOT / "game" / args.output).resolve()
    output.relative_to(ROOT / "game")
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        if args.type == "sprite":
            if "A" not in image.getbands() or image.getchannel("A").getextrema()[0] != 0:
                raise SystemExit("Sprite must already have genuine alpha transparency")
            image.thumbnail((540, 700), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (540, 700), (0, 0, 0, 0))
            canvas.alpha_composite(image, ((540-image.width)//2, 700-image.height))
            canvas.save(output)
        else:
            ImageOps.fit(image.convert("RGB"), (1280, 720), method=Image.Resampling.LANCZOS).save(output)
    entry = {
        "id": args.id, "type": args.type, "file": output.relative_to(ROOT / "game").as_posix(),
        "source": "Built-in imagegen; model identifier not exposed by tool",
        "source_file": "assets_source/" + source_relative.as_posix(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "prompt": prompt.relative_to(ROOT).as_posix(),
        "prompt_sha256": hashlib.sha256(prompt.read_bytes()).hexdigest(),
        "version": args.version, "approved": True, "approval_scope": "Agent integration review; user final visual choice pending",
        "status": "candidate_user_review", "license": "AI-generated output; no third-party reference art; see CREDITS.md",
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    if args.type == "sprite":
        entry["expression"] = args.expression
        entry["character"] = "heroine"
    for argument, file_key, hash_key, folder in [
        (args.reference_source, "reference_source_file", "reference_sha256", "assets_source"),
        (args.prompt_components, "prompt_components", "prompt_components_sha256", "prompts"),
    ]:
        if argument is not None:
            file = argument.resolve()
            file.relative_to(ROOT / folder)
            entry[file_key] = file.relative_to(ROOT).as_posix()
            entry[hash_key] = hashlib.sha256(file.read_bytes()).hexdigest()
    path = ROOT / "game/data/asset_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["assets"] = [a for a in manifest["assets"] if a["id"] != args.id] + [entry]
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {args.id}: {entry['file']}")


if __name__ == "__main__":
    main()
