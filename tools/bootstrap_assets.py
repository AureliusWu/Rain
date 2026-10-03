"""One-time v0.1 placeholders and stock Ren'Py GUI import; never overwrite art."""
import argparse
import hashlib
import json
import math
import random
import shutil
import struct
import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageDraw
from tools.story_model import ROOT


def write_wav(path, samples, rate=22050):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", required=True, type=Path)
    args = parser.parse_args()
    game = ROOT / "game"
    if (game / "data/asset_manifest.json").exists():
        raise SystemExit("Assets already initialized; use the import pipeline for new versions.")
    for folder in ["backgrounds", "characters", "cg", "audio/bgm", "audio/sfx", "audio/voice", "script", "data", "gui", "fonts", "tl/schinese"]:
        (game / folder).mkdir(parents=True, exist_ok=True)
    for folder in ["character", "cg", "background", "audio", "ui"]:
        (ROOT / "assets_source" / folder).mkdir(parents=True, exist_ok=True)
    for folder in ["character", "cg", "background", "script", "voice", "negative"]:
        (ROOT / "prompts" / folder).mkdir(parents=True, exist_ok=True)
    template = args.sdk / "the_question/game"
    shutil.copytree(template / "gui", game / "gui", dirs_exist_ok=True)
    shutil.copy2(template / "gui.rpy", game / "gui.rpy")
    shutil.copy2(template / "screens.rpy", game / "screens.rpy")
    for name in ["common.rpy", "screens.rpy"]:
        shutil.copy2(template / "tl/schinese" / name, game / "tl/schinese" / name)
    shutil.copy2(args.sdk / "sdk-fonts/SourceHanSansLite.ttf", game / "fonts/SourceHanSansLite.ttf")
    (ROOT / "licenses").mkdir(exist_ok=True)
    shutil.copy2(args.sdk / "LICENSE.txt", ROOT / "licenses/RENPY.txt")
    gui = (game / "gui.rpy").read_text(encoding="utf-8-sig")
    gui = gui.replace("DejaVuSans.ttf", "fonts/SourceHanSansLite.ttf")
    gui = gui.replace("#cc6600", "#91d4e0").replace("#e0a366", "#d1f3fa").replace("#ffaa22", "#c5edf3")
    gui = gui.replace("define gui.text_size = 22", "define gui.text_size = 27")
    gui = gui.replace("define gui.dialogue_xpos = 210", "define gui.dialogue_xpos = 170")
    (game / "gui.rpy").write_text(gui, encoding="utf-8")
    # Original, intentionally schematic engineering placeholders.
    background = Image.new("RGB", (1280, 720), "#182d43")
    draw = ImageDraw.Draw(background)
    draw.rectangle((0, 400, 1280, 720), fill="#263d50")
    draw.rectangle((0, 130, 1280, 150), fill="#a1c9d2")
    draw.rectangle((50, 150, 66, 525), fill="#9fb9c4")
    draw.rectangle((1000, 150, 1016, 525), fill="#9fb9c4")
    for x in range(30, 1280, 42):
        draw.line((x, 0, x - 60, 720), fill="#456275", width=2)
    source = ROOT / "assets_source/background/station_placeholder_v1.png"
    background.save(source)
    shutil.copy2(source, game / "backgrounds/station_placeholder.png")
    sprite = Image.new("RGBA", (540, 700), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)
    draw.rounded_rectangle((135, 20, 405, 380), 100, fill="#27384c")
    draw.ellipse((165, 58, 375, 295), fill="#f2d7c7")
    draw.polygon([(155, 330), (385, 330), (450, 700), (90, 700)], fill="#a7ccd4")
    draw.polygon([(205, 310), (335, 310), (285, 510), (255, 510)], fill="#eaeff1")
    for x in (230, 305):
        draw.ellipse((x - 10, 156, x + 10, 177), fill="#384d5b")
    draw.arc((240, 185, 295, 220), 10, 160, fill="#b6796c", width=3)
    source = ROOT / "assets_source/character/heroine_placeholder_v1.png"
    sprite.save(source)
    shutil.copy2(source, game / "characters/heroine_normal.png")
    # Project-owned UI primitives.
    box = Image.new("RGBA", (1280, 185), "#091826df")
    ImageDraw.Draw(box).line((50, 0, 1230, 0), fill="#91d4e0b0", width=2)
    box.save(game / "gui/textbox.png")
    background.save(game / "gui/main_menu.png")
    Image.new("RGBA", (1280, 720), "#102537f2").save(game / "gui/game_menu.png")
    icon = Image.new("RGBA", (256, 256), "#102b42")
    d = ImageDraw.Draw(icon)
    d.ellipse((72, 54, 186, 170), outline="#9ed9e3", width=10)
    d.line((130, 168, 95, 210), fill="#9ed9e3", width=10)
    icon.save(game / "gui/window_icon.png")
    # Sparse original pentatonic motif, no sampled or third-party recording.
    rate = 22050
    notes = [60, 64, 67, 71, 67, 64, 62, 59, 55, 59, 62, 67, 64, 62, 59, 55]
    duration = len(notes) * 1.5
    def music():
        for i in range(int(rate * duration)):
            t = i / rate
            note = notes[int(t / 1.5)]
            local = t % 1.5
            freq = 440 * 2 ** ((note - 69) / 12)
            env = min(1, local / .025) * math.exp(-local * 1.8)
            tail = min(1, (duration - t) / 1.5)
            yield .14 * env * tail * (math.sin(2 * math.pi * freq * t) + .25 * math.sin(4 * math.pi * freq * t))
    source = ROOT / "assets_source/audio/rain_theme_v1.wav"
    write_wav(source, music())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-c:a", "libvorbis", "-q:a", "4", str(game / "audio/bgm/rain_theme.ogg")], check=True)
    rng = random.Random(1707)
    source = ROOT / "assets_source/audio/rain_ambience_v1.wav"
    write_wav(source, (rng.uniform(-.14, .14) for _ in range(rate * 20)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-af", "lowpass=f=3000,highpass=f=160", "-c:a", "libvorbis", "-q:a", "3", str(game / "audio/sfx/rain_ambience.ogg")], check=True)
    entries = []
    for path in sorted(game.rglob("*")):
        if path.suffix.lower() not in {".png", ".ogg", ".ttf"}:
            continue
        relative = path.relative_to(game).as_posix()
        kind = "ui"
        source = "Ren'Py 8.5.3 stock GUI (MIT)"
        license_name = "MIT; licenses/RENPY.txt"
        if relative.startswith("characters/"):
            kind, source, license_name = "sprite", "Original procedural placeholder; tools/bootstrap_assets.py", "Project MIT"
        elif relative.startswith("backgrounds/"):
            kind, source, license_name = "background", "Original procedural placeholder; tools/bootstrap_assets.py", "Project MIT"
        elif relative.startswith("audio/"):
            kind, source, license_name = "audio", "Original procedural synthesis; tools/bootstrap_assets.py", "Project MIT"
        elif relative.startswith("fonts/"):
            kind, source, license_name = "font", "Ren'Py 8.5.3 sdk-fonts/SourceHanSansLite.ttf; Adobe Source Han Sans", "SIL Open Font License 1.1; licenses/SourceHanSans-OFL.txt"
        if relative in {"gui/textbox.png", "gui/main_menu.png", "gui/game_menu.png", "gui/window_icon.png"}:
            source, license_name = "Original procedural UI; tools/bootstrap_assets.py", "Project MIT"
        asset_id = relative.rsplit(".", 1)[0].replace("/", "_")
        special = {"characters/heroine_normal.png": "heroine_normal", "backgrounds/station_placeholder.png": "station", "audio/bgm/rain_theme.ogg": "rain_theme", "audio/sfx/rain_ambience.ogg": "rain_ambience"}
        entry = {"id": special.get(relative, asset_id), "type": kind, "file": relative, "source": source, "license": license_name, "version": 1, "approved": True, "status": "placeholder" if kind in {"sprite", "background"} else "development", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        if kind == "sprite":
            entry["expression"] = "normal"
        entries.append(entry)
    (game / "data/asset_manifest.json").write_text(json.dumps({"schema_version": 1, "assets": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (game / "data/voice_manifest.json").write_text('{"schema_version": 1, "voices": []}\n')
    print(f"Initialized {len(entries)} assets with hashes and provenance.")


if __name__ == "__main__":
    main()
