"""Generate selected text-bound key lines with the pinned Chinese Kokoro voice."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from tools.asset_paths import ASSET_ID, project_file, sha256
from tools.story_model import ROOT, load_story, scene_lines
from tools.prompt_registry import prompt_by_file
from tools.audio_process.metadata import audio_metadata, metadata_matches

# Precedes every import that can initialize the inference provider.
os.environ['ORT_DISABLE_TELEMETRY'] = '1'
MODEL_HASH = '11751c087b4bbeed031e2b687b11dda698bd27ba0509472f960b57f835a999f7'
VOICES_HASH = '14cb6186c99e4f6016871405f62046c5df863ae27465cbdc4ee08be7dd703acd'
CONFIG_HASH = 'bc333efa5ce4ceff433c8c8e5d027a1eca0166001e4e4a62bea2d26ff7a46890'
PROCESSING = 'edge_fades_15ms_peak_0.89_v1'


def request_fingerprint(voice, prompt_hash):
    request = {key: voice.get(key) for key in ['line_id', 'text', 'character', 'model', 'voice', 'speed', 'version', 'processing', 'prompt_id']}
    request.update(model_sha256=MODEL_HASH, voice_bank_sha256=VOICES_HASH,
                   config_sha256=CONFIG_HASH, frontend='misaki-0.9.4/ZHG2P-1.1',
                   wrapper='kokoro-onnx-0.6.1', prompt_sha256=prompt_hash)
    return sha256(json.dumps(request, ensure_ascii=False, sort_keys=True).encode('utf-8'))


def cached_voice_is_current(root, voice, asset, prompt_hash):
    if not asset or voice.get('generation_sha256') != request_fingerprint(voice, prompt_hash):
        return False
    if (asset.get('id'), asset.get('type'), asset.get('version')) != (voice['voice_id'], 'voice', voice['version']):
        return False
    if voice.get('text_sha256') != sha256(voice['text'].encode('utf-8')):
        return False
    if (asset.get('file'), asset.get('source_file')) != (voice['file'], voice.get('source_file')):
        return False
    try:
        for relative, area, checksum in [('game/' + voice['file'], 'game', asset.get('sha256')),
                                         (voice['source_file'], 'assets_source', asset.get('source_sha256'))]:
            if sha256(project_file(root, relative, area).read_bytes()) != checksum:
                return False
            metadata_key = 'audio' if area == 'game' else 'source_audio'
            if not metadata_matches(audio_metadata(root / relative), asset.get(metadata_key)):
                return False
    except (ValueError, OSError, RuntimeError):
        return False
    return True


def prepare_samples(samples, rate):
    import numpy as np
    samples = np.asarray(samples, dtype='float64').copy()
    if samples.ndim != 1 or len(samples) < rate * .1 or not np.isfinite(samples).all():
        raise ValueError('Invalid synthesized voice')
    peak = float(np.max(np.abs(samples)))
    if peak < 1e-5:
        raise ValueError('Silent synthesized voice')
    if peak > .89:
        samples *= .89 / peak
    edge = min(round(rate * .015), len(samples) // 4)
    samples[:edge] *= np.linspace(0, 1, edge)
    samples[-edge:] *= np.linspace(1, 0, edge)
    return samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--voices', required=True, type=Path)
    parser.add_argument('--config', required=True, type=Path)
    args = parser.parse_args()
    for path, expected in [(args.model, MODEL_HASH), (args.voices, VOICES_HASH), (args.config, CONFIG_HASH)]:
        if sha256(path.read_bytes()) != expected:
            raise SystemExit(f'Model/voice checksum mismatch: {path.name}')
    voice_path, asset_path = ROOT / 'game/data/voice_manifest.json', ROOT / 'game/data/asset_manifest.json'
    data = json.loads(voice_path.read_text(encoding='utf-8'))
    manifest = json.loads(asset_path.read_text(encoding='utf-8'))
    assets = {a['id']: a for a in manifest['assets']}
    files = {a['file']: a['id'] for a in manifest['assets']}
    lines = {line['id']: line for node in load_story()['nodes'] for line in scene_lines(node)}
    pending, ids = [], set()
    for voice in data['voices']:
        name = voice['voice_id']
        if not ASSET_ID.fullmatch(name) or name in ids or type(voice['version']) is not int or voice['version'] < 1:
            raise ValueError('Invalid/duplicate voice ID or version')
        ids.add(name)
        prompt = prompt_by_file(ROOT, voice['prompt'])
        line = lines.get(voice['line_id'], {})
        if (line.get('speaker'), line.get('text'), line.get('voice')) != (voice['character'], voice['text'], name):
            raise ValueError(f'Voice is not bound to exact authored dialogue: {name}')
        if voice['voice'] != 'zf_001' or voice['model'] != 'Kokoro-82M v1.1-zh ONNX int8' or voice['speed'] != .95:
            raise ValueError('This production stage preserves the reviewed voice and speed')
        if voice.get('prompt_id') != prompt['id']:
            raise ValueError('Voice Prompt ID mismatch')
        project_file(ROOT, 'game/' + voice['file'], 'game', must_exist=False)
        source_relative = f'assets_source/audio/voice/{name}.wav'
        project_file(ROOT, source_relative, 'assets_source', must_exist=False)
        if not voice['file'].startswith('audio/voice/') or not voice['file'].endswith('.ogg'):
            raise ValueError('Voice output must be a game/audio/voice OGG')
        if files.get(voice['file'], name) != name:
            raise ValueError('Output belongs to another asset')
        if cached_voice_is_current(ROOT, voice, assets.get(name), prompt['sha256']):
            continue
        if name in assets or (ROOT / ('game/' + voice['file'])).exists() or (ROOT / source_relative).exists():
            raise ValueError(f'Changed or corrupt cached voice: {name}; review a new version instead of overwriting it')
        if voice.get('processing') != PROCESSING:
            raise ValueError('New voices require the current processing profile')
        pending.append((voice, prompt, source_relative))
    if not pending:
        print(f'Voice generation: 0 changes; all {len(ids)} recordings and requests match. No model initialized.')
        return
    import onnxruntime as ort
    ort.disable_telemetry_events()
    from misaki import zh
    from kokoro_onnx import Kokoro
    import soundfile as sf
    g2p = zh.ZHG2P(version='1.1')
    engine = Kokoro(str(args.model), str(args.voices), vocab_config=str(args.config))
    prepared = []
    with tempfile.TemporaryDirectory(prefix='galgame-voices-') as directory:
        for voice, prompt, source_relative in pending:
            phonemes, _ = g2p(voice['text'])
            samples, rate = engine.create(phonemes, voice=voice['voice'], speed=voice['speed'], is_phonemes=True)
            if rate != 24000:
                raise ValueError('Unexpected synthesis sample rate')
            source = Path(directory) / (voice['voice_id'] + '.wav')
            output = source.with_suffix('.ogg')
            sf.write(source, prepare_samples(samples, rate), rate, subtype='PCM_16')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(source), '-c:a', 'libvorbis', '-q:a', '5', str(output)], check=True)
            source_audio, audio = audio_metadata(source), audio_metadata(output)
            if audio['peak'] >= .99 or not -30 <= audio['rms_dbfs'] <= -18 or audio['frames'] != source_audio['frames']:
                raise ValueError(f"Voice failed signal review: {voice['voice_id']}")
            voice.update(text_sha256=sha256(voice['text'].encode('utf-8')), sample_rate=rate,
                         duration_seconds=round(source_audio['duration_seconds'], 3), source_file=source_relative,
                         model_sha256=MODEL_HASH, voice_bank_sha256=VOICES_HASH, config_sha256=CONFIG_HASH,
                         generation_sha256=request_fingerprint(voice, prompt['sha256']))
            entry = dict(id=voice['voice_id'], type='voice', file=voice['file'], character='heroine',
                         source='Kokoro-82M v1.1-zh; ONNX export model-files-v1.1; zf_001; generated from project dialogue',
                         source_file=source_relative, source_sha256=sha256(source.read_bytes()),
                         license='Model Apache-2.0; authoring wrapper MIT; synthesized project dialogue; see CREDITS.md',
                         version=voice['version'], approved=True, status='candidate_user_review',
                         approval_scope='Agent integration and signal checks; user final voice choice pending',
                         prompt=voice['prompt'], prompt_id=prompt['id'], prompt_sha256=prompt['sha256'],
                         sha256=sha256(output.read_bytes()), audio=audio, source_audio=source_audio)
            prepared.append((entry, source.read_bytes(), output.read_bytes()))
            print(f"Prepared {voice['voice_id']}: {voice['duration_seconds']}s", flush=True)
        for entry, source, output in prepared:
            for relative, content in [(entry['source_file'], source), ('game/' + entry['file'], output)]:
                file = ROOT / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(content)
            manifest['assets'].append(entry)
        voice_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        asset_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Voice generation: {len(prepared)} new recordings; {len(ids) - len(prepared)} retained.')


if __name__ == '__main__':
    main()
