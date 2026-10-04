"""Create the small, project-owned blue GUI primitives used by the slice."""
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image, ImageDraw
from tools.story_model import ROOT


def main():
    manifest_path = ROOT / "game/data/asset_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_file = {a["file"]: a for a in manifest["assets"]}

    def save(relative, image):
        source = ROOT / "assets_source/ui/v2" / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        image.save(source)
        target = ROOT / "game/gui" / relative
        shutil.copy2(source, target)
        entry = by_file["gui/" + relative]
        entry.update(source="Original procedural GUI; tools/image_process/create_ui.py", license="Project MIT", version=2, status="candidate_user_review", source_file=source.relative_to(ROOT).as_posix(), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), sha256=hashlib.sha256(target.read_bytes()).hexdigest())

    for name in ["main_menu", "game_menu"]:
        image = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 277, 719), fill="#071622c9")
        draw.line((278, 0 if name == "main_menu" else 120, 278, 690), fill="#7ebbc8", width=2)
        save("overlay/" + name + ".png", image)

    for family in ["slider", "scrollbar"]:
        for orientation in ["horizontal", "vertical"]:
            for state in ["idle", "hover"]:
                for part in ["bar", "thumb"]:
                    relative = f"{family}/{orientation}_{state}_{part}.png"
                    with Image.open(ROOT / "game/gui" / relative) as original:
                        size = original.size
                    color = ("#284b5d" if state == "idle" else "#37697b") if part == "bar" else ("#91d4e0" if state == "idle" else "#d1f3fa")
                    save(relative, Image.new("RGBA", size, color))
    for name in ["radio", "check"]:
        image = Image.new("RGBA", (25, 36), (0, 0, 0, 0))
        ImageDraw.Draw(image).rounded_rectangle((3, 5, 8, 30), radius=2, fill="#91d4e0")
        save(f"button/{name}_selected_foreground.png", image)

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Created 20 GUI primitives with source assets and hashes.")


if __name__ == "__main__":
    main()
