"""Validate decoded audio, source metadata, signal levels and authored cues."""
import argparse
import json
from pathlib import Path
from tools.asset_paths import project_file
from tools.audio_process.metadata import audio_metadata, metadata_matches
from tools.story_model import ROOT, load_story, scene_lines


def validate_audio(root=ROOT, assets=None, story=None):
    if assets is None:
        assets = json.loads((root / 'game/data/asset_manifest.json').read_text(encoding='utf-8'))['assets']
    story = story if story is not None else load_story(root / 'game/data/story.json')
    by_id = {a['id']: a for a in assets}
    errors, measured = [], {}
    for asset in assets:
        if asset['type'] not in {'audio', 'voice'}:
            continue
        name = asset['id']
        for area, file_key, metadata_key in [('game', 'file', 'audio'), ('assets_source', 'source_file', 'source_audio')]:
            try:
                relative = 'game/' + asset['file'] if area == 'game' else asset.get(file_key)
                file = project_file(root, relative, area)
                actual = audio_metadata(file)
                expected_format = ('OGG', 'VORBIS') if area == 'game' else ('WAV', 'PCM_16')
                if (actual['format'], actual['subtype']) != expected_format:
                    errors.append(f'Audio format mismatch: {name}/{area}')
                if not metadata_matches(actual, asset.get(metadata_key)):
                    errors.append(f'Audio metadata mismatch: {name}/{area}')
                if actual['sample_rate'] not in {22050, 24000, 44100, 48000} or actual['channels'] not in {1, 2}:
                    errors.append(f'Unsupported audio rate/channels: {name}/{area}')
                if actual['peak'] >= .99:
                    errors.append(f'Audio lacks peak headroom: {name}/{area}')
                if actual['rms_dbfs'] < -55:
                    errors.append(f'Audio is too quiet: {name}/{area}')
                if area == 'game':
                    measured[name] = actual
            except (ValueError, OSError, RuntimeError) as exc:
                errors.append(f'Undecodable audio: {name}/{area}: {exc}')
        game, source = asset.get('audio', {}), asset.get('source_audio', {})
        if game and source and (game.get('sample_rate'), game.get('channels'), game.get('frames')) != (source.get('sample_rate'), source.get('channels'), source.get('frames')):
            errors.append(f'Source/game audio length mismatch: {name}')
        if asset['type'] == 'voice' and game and not -30 <= game.get('rms_dbfs', -100) <= -18:
            errors.append(f'Voice signal level outside review range: {name}')
    for node in story['nodes']:
        for key, role in [('bgm', 'bgm'), ('ambient', 'ambient')]:
            if node.get(key):
                asset = by_id.get(node[key], {})
                if asset.get('type') != 'audio' or asset.get('audio_role') != role:
                    errors.append(f"{node['id']}: wrong audio role for {key}")
        for line in scene_lines(node):
            if line.get('sound'):
                asset = by_id.get(line['sound'], {})
                if asset.get('type') != 'audio' or asset.get('audio_role') != 'sfx':
                    errors.append(f"{line['id']}: missing/wrong sound cue {line['sound']}")
            if 'stop_ambient' in line and type(line['stop_ambient']) is not bool:
                errors.append(f"{line['id']}: stop_ambient must be boolean")
    return errors, measured


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    errors, measured = validate_audio()
    report = {'errors': errors, 'decoded_game_audio': len(measured), 'signals': measured,
              'limits': 'Peak < .99; RMS is unweighted signal level, not LUFS or a listening review.'}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for error in errors:
        print('ERROR:', error)
    print(f'Audio validation: {len(measured)} decoded game files, {len(errors)} errors')
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
