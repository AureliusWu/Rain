"""Preflight, import or reproduce reviewed images without changing their identity."""
import argparse
import io
import json
import os
from pathlib import Path
import tempfile
from PIL import Image, ImageOps
from tools.asset_paths import ASSET_ID, project_file, sha256
from tools.image_process.metadata import image_metadata
from tools.prompt_registry import prompt_by_file, validate_registry
from tools.story_model import ROOT, ID

MANIFEST = 'game/data/asset_manifest.json'
METHODS = {'sprite': 'sprite_bottom_center_v1', 'background': 'fit_1280x720_v1',
           'cg': 'fit_1280x720_v1', 'ui': 'copy_png_v1'}
FOLDERS = {'sprite': 'characters', 'background': 'backgrounds', 'cg': 'cg', 'ui': 'gui'}
ALLOWED_METHODS = {kind: {method} for kind, method in METHODS.items()}
ALLOWED_METHODS['ui'].add('fit_1280x720_v1')  # Explicit full-screen menu background.


def render_image(source, method):
    with Image.open(source) as opened:
        opened.load()
        if method == 'copy_png_v1':
            if opened.format != 'PNG':
                raise ValueError('Native-size UI input must be PNG')
            return source.read_bytes(), image_metadata(opened)
        if method == 'sprite_bottom_center_v1':
            if 'A' not in opened.getbands():
                raise ValueError('Sprite must already have genuine alpha transparency')
            alpha = opened.getchannel('A')
            low, high = alpha.getextrema()
            corners = [(0, 0), (opened.width-1, 0), (0, opened.height-1), (opened.width-1, opened.height-1)]
            if low != 0 or high < 250 or any(alpha.getpixel(p) for p in corners):
                raise ValueError('Sprite must have transparent corners and visible character pixels')
            image = opened.convert('RGBA')
            image.thumbnail((540, 700), Image.Resampling.LANCZOS)
            result = Image.new('RGBA', (540, 700))
            result.alpha_composite(image, ((540-image.width)//2, 700-image.height))
        elif method == 'fit_1280x720_v1':
            result = ImageOps.fit(opened.convert('RGB'), (1280, 720), method=Image.Resampling.LANCZOS)
        else:
            raise ValueError(f'Unsupported image recipe: {method}')
        buffer = io.BytesIO()
        result.save(buffer, format='PNG')
        return buffer.getvalue(), image_metadata(result)


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.asset-import-', delete=False) as temp:
        temp.write(data)
        staged = Path(temp.name)
    try:
        os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)


def import_image(*, root=ROOT, source, asset_id, kind, output, version, prompt=None,
                 expression='normal', reference_source=None, prompt_components=None,
                 source_label=None, license_name=None, method=None, dry_run=False):
    if not ASSET_ID.fullmatch(asset_id) or kind not in METHODS or type(version) is not int or version < 1:
        raise ValueError('Invalid asset ID, type or version')
    source_path = project_file(root, source, 'assets_source')
    relative = 'game/' + output
    target = project_file(root, relative, 'game', must_exist=False)
    if not output.startswith(FOLDERS[kind] + '/') or target.suffix.lower() != '.png':
        raise ValueError('Output must be PNG in the matching game asset folder')
    manifest_path = project_file(root, MANIFEST, 'game')
    original_manifest = manifest_path.read_bytes()
    manifest = json.loads(original_manifest)
    assets = manifest['assets']
    if len({a['id'] for a in assets}) != len(assets) or len({a['file'] for a in assets}) != len(assets):
        raise ValueError('Manifest has duplicate IDs or output paths')
    existing = next((a for a in assets if a['id'] == asset_id), None)
    if any(a['file'] == output and a['id'] != asset_id for a in assets):
        raise ValueError('Output is owned by another asset ID')
    if existing and (existing['type'] != kind or version < existing['version']):
        raise ValueError('Cannot change an asset type or downgrade its version')
    if target.exists() and (existing is None or existing['file'] != output):
        raise ValueError('Refusing to overwrite an untracked output')
    source_label = source_label or (existing or {}).get('source')
    license_name = license_name or (existing or {}).get('license')
    if not source_label or not license_name:
        raise ValueError('New imports require explicit source and license')
    entry = dict(existing or {})
    entry.update(id=asset_id, type=kind, file=output, source=source_label, license=license_name,
                 source_file=source, source_sha256=sha256(source_path.read_bytes()), version=version,
                 approved=True, status='candidate_user_review',
                 approval_scope='Agent integration review; user final visual choice pending')
    if kind == 'sprite':
        if not ID.fullmatch(expression):
            raise ValueError('Invalid expression ID')
        entry.update(expression=expression, character='heroine')
    if prompt:
        errors = validate_registry(root)
        if errors:
            raise ValueError('\n'.join(errors))
        registered = prompt_by_file(root, prompt)
        entry.update(prompt=prompt, prompt_id=registered['id'], prompt_sha256=registered['sha256'])
    elif kind in {'sprite', 'background', 'cg'}:
        raise ValueError('AI story art requires a registered Prompt')
    for argument, file_key, hash_key, folder in [
        (reference_source, 'reference_source_file', 'reference_sha256', 'assets_source'),
        (prompt_components, 'prompt_components', 'prompt_components_sha256', 'prompts'),
    ]:
        if argument is not None:
            file = project_file(root, argument, folder)
            entry[file_key] = argument
            entry[hash_key] = sha256(file.read_bytes())
            if folder == 'prompts':
                entry['prompt_components_id'] = prompt_by_file(root, argument)['id']
    method = method or (existing or {}).get('image_recipe', {}).get('method', METHODS[kind])
    if method not in ALLOWED_METHODS[kind]:
        raise ValueError('Image recipe does not match the asset type')
    content, metadata = render_image(source_path, method)
    original_output = target.read_bytes() if target.is_file() else None
    old_pixels = None
    if original_output:
        with Image.open(io.BytesIO(original_output)) as opened:
            old_pixels = image_metadata(opened)['pixel_sha256']
        # Keep the exact published PNG when the display pixels match. Encoder
        # compression may differ across Pillow versions, even for identical art.
        if old_pixels == metadata['pixel_sha256']:
            content = original_output
    entry.update(sha256=sha256(content), image=metadata, image_recipe={'method': method})
    if existing and version == existing['version']:
        if (old_pixels != metadata['pixel_sha256'] or existing['file'] != output
                or existing.get('source_sha256') != entry['source_sha256']
                or existing.get('prompt_sha256') != entry.get('prompt_sha256')
                or any(existing.get(key) != entry.get(key) for key in
                       ('reference_source_file', 'reference_sha256', 'prompt_components', 'prompt_components_sha256'))):
            raise ValueError('Changed content or provenance requires a higher asset version')
    new_assets = [entry if a['id'] == asset_id else a for a in assets]
    if not existing:
        new_assets.append(entry)
    manifest['assets'] = new_assets
    new_manifest = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    changed = content != original_output or new_manifest != original_manifest
    report = {'id': asset_id, 'file': output, 'sha256': entry['sha256'], 'image': metadata,
              'changed': changed, 'dry_run': dry_run}
    if dry_run or not changed:
        return report
    if manifest_path.read_bytes() != original_manifest:
        raise ValueError('Manifest changed during import; retry against the current file')
    # Both files are staged in their own directories. On an ordinary I/O failure
    # after replacing the PNG, restore its original bytes before propagating it.
    atomic_write(target, content)
    try:
        atomic_write(manifest_path, new_manifest)
    except BaseException:
        if original_output is None:
            target.unlink(missing_ok=True)
        else:
            atomic_write(target, original_output)
        raise
    return report


def rebuild_image(asset_id, *, root=ROOT, dry_run=False):
    data = json.loads(project_file(root, MANIFEST, 'game').read_text(encoding='utf-8'))
    entry = next((a for a in data['assets'] if a['id'] == asset_id), None)
    if not entry or not entry.get('image_recipe'):
        raise ValueError(f'No saved image recipe: {asset_id}')
    if entry['image_recipe']['method'] not in ALLOWED_METHODS[entry['type']]:
        raise ValueError('Recipe does not match the asset type')
    return import_image(root=root, source=entry['source_file'], asset_id=entry['id'],
                        kind=entry['type'], output=entry['file'], version=entry['version'],
                        prompt=entry.get('prompt'), expression=entry.get('expression', 'normal'),
                        reference_source=entry.get('reference_source_file'),
                        prompt_components=entry.get('prompt_components'), dry_run=dry_run)


def verify_rebuilds(root=ROOT):
    data = json.loads(project_file(root, MANIFEST, 'game').read_text(encoding='utf-8'))
    errors, reproduced = [], []
    for entry in data['assets']:
        if not entry.get('image_recipe'):
            continue
        try:
            result = rebuild_image(entry['id'], root=root, dry_run=True)
            if result['changed']:
                errors.append(f"Saved image/metadata differs from recipe: {entry['id']}")
            reproduced.append(entry['id'])
        except (ValueError, OSError) as exc:
            errors.append(f"{entry['id']}: {exc}")
    return errors, reproduced


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Reproduce every saved recipe without writing files')
    parser.add_argument('--rebuild', help='Reimport an existing asset using its saved recipe')
    parser.add_argument('--dry-run', action='store_true')
    for flag in ['source', 'id', 'type', 'output', 'prompt', 'expression', 'reference-source', 'prompt-components', 'source-label', 'license', 'method']:
        parser.add_argument('--' + flag)
    parser.add_argument('--version', type=int, default=1)
    args = parser.parse_args()
    try:
        if args.check:
            errors, reproduced = verify_rebuilds()
            for error in errors:
                print('ERROR:', error)
            print(f'Image reproduction: {len(reproduced)} recipes, {len(errors)} errors; no files changed.')
            raise SystemExit(bool(errors))
        if args.rebuild:
            report = rebuild_image(args.rebuild, dry_run=args.dry_run)
        else:
            if not all([args.source, args.id, args.type, args.output]):
                parser.error('Supply --source, --id, --type and --output, or --rebuild / --check')
            report = import_image(source=args.source, asset_id=args.id, kind=args.type, output=args.output,
                                  prompt=args.prompt, version=args.version, expression=args.expression or 'normal',
                                  reference_source=args.reference_source, prompt_components=args.prompt_components,
                                  source_label=args.source_label, license_name=args.license, method=args.method, dry_run=args.dry_run)
        print(json.dumps(report, ensure_ascii=False))
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Import rejected: {exc}\n')


if __name__ == '__main__':
    main()
