"""Generate only changed, text-bound key lines with a pinned Chinese Kokoro voice."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from tools.story_model import ROOT
from tools.prompt_registry import prompt_by_file

# Must precede every import that can initialize ONNX Runtime. The API alone
# cannot suppress the provider's initialization event on non-Windows systems.
os.environ["ORT_DISABLE_TELEMETRY"] = "1"

MODEL_HASH = "11751c087b4bbeed031e2b687b11dda698bd27ba0509472f960b57f835a999f7"
VOICES_HASH = "14cb6186c99e4f6016871405f62046c5df863ae27465cbdc4ee08be7dd703acd"
CONFIG_HASH = "bc333efa5ce4ceff433c8c8e5d027a1eca0166001e4e4a62bea2d26ff7a46890"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--voices", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    for path, expected in [(args.model, MODEL_HASH), (args.voices, VOICES_HASH), (args.config, CONFIG_HASH)]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit(f"Model/voice checksum mismatch: {path.name}")
    import onnxruntime as ort
    ort.disable_telemetry_events()
    from misaki import zh
    from kokoro_onnx import Kokoro
    import soundfile as sf
    g2p = zh.ZHG2P(version="1.1")
    engine = Kokoro(str(args.model), str(args.voices), vocab_config=str(args.config))
    voice_path = ROOT / "game/data/voice_manifest.json"
    data = json.loads(voice_path.read_text(encoding="utf-8"))
    asset_path = ROOT / "game/data/asset_manifest.json"
    manifest = json.loads(asset_path.read_text(encoding="utf-8"))
    for voice in data["voices"]:
        output = ROOT / "game" / voice["file"]
        text_hash = hashlib.sha256(voice["text"].encode()).hexdigest()
        if output.exists() and voice.get("text_sha256") == text_hash:
            continue
        phonemes, _ = g2p(voice["text"])
        samples, rate = engine.create(phonemes, voice=voice["voice"], speed=voice["speed"], is_phonemes=True)
        source = ROOT / "assets_source/audio/voice" / (voice["voice_id"] + ".wav")
        source.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(source), samples, rate, subtype="PCM_16")
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-af", "afade=t=in:d=0.015", "-c:a", "libvorbis", "-q:a", "5", str(output)], check=True)
        voice.update(text_sha256=text_hash, sample_rate=rate, duration_seconds=round(len(samples)/rate, 3), source_file=source.relative_to(ROOT).as_posix(), model_sha256=MODEL_HASH, voice_bank_sha256=VOICES_HASH)
        prompt = ROOT / voice["prompt"]
        prompt_id = prompt_by_file(ROOT, voice["prompt"])["id"]
        voice["prompt_id"] = prompt_id
        entry = {"id": voice["voice_id"], "type": "voice", "file": voice["file"], "character": "heroine", "source": "Kokoro-82M v1.1-zh; ONNX export model-files-v1.1; zf_001; generated from project dialogue", "source_file": source.relative_to(ROOT).as_posix(), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "license": "Model Apache-2.0; authoring wrapper MIT; synthesized project dialogue; see CREDITS.md", "version": voice["version"], "approved": True, "status": "candidate_user_review", "prompt": voice["prompt"], "prompt_sha256": hashlib.sha256(prompt.read_bytes()).hexdigest(), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
        entry.update(prompt_id=prompt_id, approval_scope="Agent integration review; user final voice choice pending")
        manifest["assets"] = [a for a in manifest["assets"] if a["id"] != entry["id"]] + [entry]
        print(f"Generated {voice['voice_id']}: {voice['duration_seconds']}s", flush=True)
    voice_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    asset_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
