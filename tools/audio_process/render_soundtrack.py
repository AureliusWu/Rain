"""Render project-owned score and sound cues from a versioned specification."""
import argparse
import json
import math
import random
import subprocess
import tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
from tools.asset_paths import project_file, sha256
from tools.audio_process.metadata import audio_metadata
from tools.prompt_registry import prompt_by_file
from tools.story_model import ROOT

SPEC = 'prompts/audio/soundtrack_v1.json'


def synthesize(recipe, rate=24000):
    count = round(recipe['duration_seconds'] * rate)
    t = np.arange(count, dtype='float64') / rate
    samples = np.zeros(count, dtype='float64')
    kind = recipe['kind']
    if kind == 'music':
        notes = recipe['notes']
        step = recipe['duration_seconds'] / len(notes)
        # Wrap bell tails around the loop boundary rather than cutting a note off.
        for index, note in enumerate(notes):
            local = (t - index * step) % recipe['duration_seconds']
            frequency = 440 * 2 ** ((note - 69) / 12)
            envelope = (1 - np.exp(-local * 90)) * np.exp(-local * 1.5)
            samples += envelope * (np.sin(2 * np.pi * frequency * local) + .15 * np.sin(4 * np.pi * frequency * local))
        samples *= recipe['amplitude']
    elif kind in {'rain', 'paper'}:
        rng = random.Random(recipe['seed'])
        noise = np.fromiter((rng.uniform(-1, 1) for _ in range(count)), dtype='float64')
        # A short low-pass kernel reduces hiss; wrap padding keeps rain periodic.
        kernel = np.ones(9) / 9
        filtered = np.convolve(np.pad(noise, (4, 4), mode='wrap'), kernel, mode='valid')
        if kind == 'rain':
            samples = filtered * recipe['amplitude'] * (1 + .12 * np.sin(2 * np.pi * t / recipe['duration_seconds']))
        else:
            envelope = np.sin(np.pi * t / recipe['duration_seconds']) ** 2
            samples = filtered * envelope * recipe['amplitude']
    elif kind == 'notification':
        for start, note in [(0, 79), (.18, 84)]:
            local = np.maximum(t - start, 0)
            frequency = 440 * 2 ** ((note - 69) / 12)
            envelope = (1 - np.exp(-local * 160)) * np.exp(-local * 14) * (t >= start)
            samples += recipe['amplitude'] * np.sin(2 * np.pi * frequency * local) * envelope
        samples *= np.minimum(1, (recipe['duration_seconds'] - t) / .04)
    else:
        raise ValueError(f'Unknown synthesis kind: {kind}')
    if not np.isfinite(samples).all() or float(np.max(np.abs(samples))) >= .9:
        raise ValueError('Invalid synthesis signal/headroom')
    return samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    prompt = prompt_by_file(ROOT, SPEC)
    recipes = json.loads((ROOT / SPEC).read_text(encoding='utf-8'))['assets']
    manifest_path = ROOT / 'game/data/asset_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    known = {a['id']: a for a in manifest['assets']}
    outputs = {a['file']: a['id'] for a in manifest['assets']}
    for recipe in recipes:
        project_file(ROOT, recipe['source_file'], 'assets_source', must_exist=False)
        project_file(ROOT, 'game/' + recipe['file'], 'game', must_exist=False)
        if outputs.get(recipe['file'], recipe['id']) != recipe['id']:
            raise ValueError('Output belongs to another asset')
        if recipe['id'] in known and known[recipe['id']].get('audio_recipe') != recipe:
            raise ValueError('Use a new version/ID for a changed soundtrack recipe')
        if recipe['id'] not in known and any((ROOT / p).exists() for p in [recipe['source_file'], 'game/' + recipe['file']]):
            raise ValueError('Refusing to overwrite an untracked audio file')
    if args.dry_run:
        print(f'Soundtrack dry-run: {len(recipes)} recipes; no files changed.')
        return
    # Render and decode every new cue in temporary storage before importing any.
    prepared = []
    with tempfile.TemporaryDirectory(prefix='galgame-audio-') as directory:
        for recipe in recipes:
            if recipe['id'] in known:
                asset = known[recipe['id']]
                for key, checksum in [('source_file', 'source_sha256'), ('file', 'sha256')]:
                    file = ROOT / (('game/' if key == 'file' else '') + asset[key])
                    if sha256(file.read_bytes()) != asset[checksum]:
                        raise ValueError('Existing soundtrack changed; do not overwrite silently')
                continue
            source = Path(directory) / (recipe['id'] + '.wav')
            output = source.with_suffix('.ogg')
            sf.write(source, synthesize(recipe), 24000, subtype='PCM_16')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(source), '-c:a', 'libvorbis', '-q:a', '4', str(output)], check=True)
            source_metadata, output_metadata = audio_metadata(source), audio_metadata(output)
            if source_metadata['frames'] != output_metadata['frames'] or output_metadata['peak'] >= .99:
                raise ValueError('Encoded audio failed quality check')
            entry = dict(id=recipe['id'], type='audio', file=recipe['file'], audio_role=recipe['role'],
                         source='Original score and procedural synthesis; tools/audio_process/render_soundtrack.py; no sampled recordings or music model',
                         license='Project MIT', version=1, approved=True, status='candidate_user_review',
                         approval_scope='Agent integration and signal checks; final listening review pending',
                         source_file=recipe['source_file'], source_sha256=sha256(source.read_bytes()),
                         sha256=sha256(output.read_bytes()), prompt=SPEC, prompt_id=prompt['id'],
                         prompt_sha256=prompt['sha256'], audio_recipe=recipe,
                         audio=output_metadata, source_audio=source_metadata)
            prepared.append((entry, source.read_bytes(), output.read_bytes()))
        for entry, source, output in prepared:
            for relative, content in [(entry['source_file'], source), ('game/' + entry['file'], output)]:
                file = ROOT / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(content)
            manifest['assets'].append(entry)
        if prepared:
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Soundtrack: {len(prepared)} new files imported; {len(recipes) - len(prepared)} existing recipes retained.')


if __name__ == '__main__':
    main()
