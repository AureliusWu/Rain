"""Check decoded assets, provenance, registered Prompts and text-bound voices."""
import argparse
from collections import Counter
import json
from pathlib import Path
import wave
from PIL import Image
from tools.asset_paths import ASSET_ID, project_file, sha256
from tools.image_process.metadata import image_metadata
from tools.prompt_registry import validate_registry, REGISTRY
from tools.story_model import ROOT, load_story, scene_lines

IMAGE_TYPES = {'background', 'sprite', 'cg', 'ui'}
EXTENSIONS = {**{kind: {'.png'} for kind in IMAGE_TYPES}, 'audio': {'.ogg'}, 'voice': {'.ogg'}, 'font': {'.ttf', '.otf'}}


def validate_assets(root=ROOT, story=None, manifest=None, voices=None):
    story = story if story is not None else load_story(root / 'game/data/story.json')
    manifest = manifest if manifest is not None else json.loads((root / 'game/data/asset_manifest.json').read_text(encoding='utf-8'))
    voices = voices if voices is not None else json.loads((root / 'game/data/voice_manifest.json').read_text(encoding='utf-8'))['voices']
    errors = validate_registry(root)
    if manifest.get('schema_version') != 1:
        errors.append('Unsupported asset manifest schema')
    assets = manifest['assets']
    ids = [a.get('id') for a in assets]
    if len(ids) != len(set(ids)):
        errors.append('Duplicate asset ID')
    files = [a.get('file') for a in assets]
    if len(files) != len(set(files)):
        errors.append('Duplicate asset output path')
    lookup = {a.get('id'): a for a in assets}
    by_file = {a.get('file'): a for a in assets}
    try:
        registry = json.loads(project_file(root, REGISTRY, 'prompts').read_text(encoding='utf-8'))
        prompts = {p['id']: p for p in registry['prompts']}
    except (ValueError, OSError):
        prompts = {}
    for asset in assets:
        name = asset.get('id', '')
        kind = asset.get('type')
        if not ASSET_ID.fullmatch(name) or kind not in EXTENSIONS:
            errors.append(f'Invalid asset ID/type: {name}')
        if not asset.get('source') or not asset.get('license') or type(asset.get('version')) is not int or asset['version'] < 1:
            errors.append(f'Missing asset provenance/version: {name}')
        if asset.get('approved') is not True:
            errors.append(f'Asset lacks integration review: {name}')
        try:
            file = project_file(root, 'game/' + asset.get('file', ''), 'game')
            if file.suffix.lower() not in EXTENSIONS.get(kind, set()):
                errors.append(f'Asset extension/type mismatch: {name}')
            content = file.read_bytes()
            if sha256(content) != asset.get('sha256'):
                errors.append(f"Hash mismatch: {asset['file']}")
            if kind in IMAGE_TYPES:
                try:
                    with Image.open(file) as image:
                        actual = image_metadata(image)
                        if image.format != 'PNG' or actual != asset.get('image'):
                            errors.append(f'Image metadata/format mismatch: {name}')
                        if kind in {'background', 'cg'} and image.size != (1280, 720):
                            errors.append(f'Background/CG canvas mismatch: {name}')
                        if kind == 'sprite' and (image.size != (540, 700) or 'A' not in image.getbands()):
                            errors.append(f'Sprite canvas/alpha mismatch: {name}')
                except (ValueError, OSError) as exc:
                    errors.append(f'Undecodable image: {name}: {exc}')
            if kind in {'audio', 'voice'} and not content.startswith(b'OggS'):
                errors.append(f'Invalid OGG header: {name}')
        except (ValueError, OSError) as exc:
            errors.append(f'Missing asset or unsafe asset path: {name}: {exc}')
        for key, checksum, area in [
            ('source_file', 'source_sha256', 'assets_source'),
            ('reference_source_file', 'reference_sha256', 'assets_source'),
            ('prompt', 'prompt_sha256', 'prompts'),
            ('prompt_components', 'prompt_components_sha256', 'prompts'),
        ]:
            if asset.get(key) or asset.get(checksum):
                try:
                    provenance = project_file(root, asset.get(key), area)
                    if sha256(provenance.read_bytes()) != asset.get(checksum):
                        errors.append(f'Provenance hash mismatch ({key}): {name}')
                except (ValueError, OSError) as exc:
                    errors.append(f'Invalid provenance ({key}): {name}: {exc}')
        for key, id_key, checksum in [('prompt', 'prompt_id', 'prompt_sha256'),
                                      ('prompt_components', 'prompt_components_id', 'prompt_components_sha256')]:
            if asset.get(key) or asset.get(id_key):
                registered = prompts.get(asset.get(id_key))
                if not registered or (registered['file'], registered['sha256']) != (asset.get(key), asset.get(checksum)):
                    errors.append(f'Prompt Registry binding mismatch: {name}/{key}')
        for reference in asset.get('reference_sources', []):
            try:
                file = project_file(root, reference.get('file'), 'assets_source')
                if sha256(file.read_bytes()) != reference.get('sha256'):
                    errors.append(f'Reference asset changed: {name}')
            except (ValueError, OSError) as exc:
                errors.append(f'Invalid reference source: {name}: {exc}')
        if asset.get('reused_from'):
            original = lookup.get(asset['reused_from'])
            if not original or original['sha256'] != asset['sha256']:
                errors.append(f'Reused asset differs from original: {name}')
    sprite_expressions = {a.get('expression') for a in assets if a['type'] == 'sprite'}
    for node in story['nodes']:
        for key, kinds in [('background', {'background', 'cg'}), ('bgm', {'audio'}), ('ambient', {'audio'})]:
            if node.get(key):
                asset = lookup.get(node[key])
                if not asset:
                    errors.append(f"{node['id']}: missing {key} {node[key]}")
                elif asset['type'] not in kinds:
                    errors.append(f"{node['id']}: wrong asset type for {key}")
        for expression in [node.get('sprite')] + [line.get('expression') for line in scene_lines(node)]:
            if expression and expression not in sprite_expressions:
                errors.append(f"{node['id']}: missing sprite expression {expression}")
    voice_ids = [v['voice_id'] for v in voices]
    if len(voice_ids) != len(set(voice_ids)):
        errors.append('Duplicate voice ID')
    by_voice = {v['voice_id']: v for v in voices}
    bound = set()
    for node in story['nodes']:
        for line in scene_lines(node):
            if not line.get('voice'):
                continue
            voice = by_voice.get(line['voice'])
            bound.add(line['voice'])
            asset = by_file.get((voice or {}).get('file'))
            if not voice or not asset:
                errors.append(f"{line['id']}: missing voice {line['voice']}")
            elif asset['type'] != 'voice':
                errors.append(f"{line['id']}: wrong asset type for voice")
            elif (voice['text'], voice['line_id'], voice['character']) != (line['text'], line['id'], line['speaker']):
                errors.append(f"{line['id']}: voice/text mismatch")
    for voice in voices:
        name = voice['voice_id']
        if sha256(voice['text'].encode('utf-8')) != voice.get('text_sha256'):
            errors.append(f'Voice text hash mismatch: {name}')
        asset = lookup.get(name)
        if not asset or (asset.get('file'), asset.get('prompt_id'), asset.get('source_file')) != (voice.get('file'), voice.get('prompt_id'), voice.get('source_file')):
            errors.append(f'Voice provenance binding mismatch: {name}')
        try:
            source = project_file(root, voice.get('source_file'), 'assets_source')
            with wave.open(str(source), 'rb') as audio:
                duration = audio.getnframes() / audio.getframerate()
                if (audio.getnframes() <= 0 or audio.getframerate() != voice.get('sample_rate')
                        or abs(duration - voice.get('duration_seconds', 0)) > .002):
                    errors.append(f'Voice WAV metadata mismatch: {name}')
        except (ValueError, OSError, wave.Error) as exc:
            errors.append(f'Invalid source voice: {name}: {exc}')
    for voice_id in set(voice_ids) - bound:
        errors.append(f'Unbound voice: {voice_id}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    errors = validate_assets()
    assets = json.loads((ROOT / 'game/data/asset_manifest.json').read_text(encoding='utf-8'))['assets']
    report = {'errors': errors, 'asset_count': len(assets), 'types': dict(Counter(a['type'] for a in assets)),
              'image_count': sum(a['type'] in IMAGE_TYPES for a in assets),
              'reproducible_images': sum(bool(a.get('image_recipe')) for a in assets)}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for error in errors:
        print('ERROR:', error)
    print(f"Asset validation: {len(errors)} errors; {len(assets)} assets, {report['image_count']} images")
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
