"""Load real saves made by the exact published v1.0.0 EXE in the new EXE."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

from tools.compile_story import quote
from tools.compile_tests import checkpoint_assertions, render_persistence_tests
from tools.story_model import ROOT, enumerate_routes, load_story, scene_lines
from tools.build.verify_package import (collect_runtime_evidence, positive_timeout,
                                       run_native_tests, validate_suite_evidence)

BASELINE_VERSION = '1.0.0'
BASELINE_SHA256 = '0d09a78a482e2ff0d34e14f51d49c89d5cc0d36b91506d44c6a3bcdcc678d3f1'


def digest(file):
    with file.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def render_upgrade_writer(story):
    route = enumerate_routes(story)['routes'][0]
    dialogue = {line['id']: line for node in story['nodes'] for line in scene_lines(node)}
    choices = {choice['id']: choice for node in story['nodes'] for choice in node.get('choices', [])}
    setup = render_persistence_tests(story).split('testcase cross_process_load:')[0]
    setup = setup.replace('reports/persistence-screenshots', 'reports/upgrade-screenshots')
    setup = setup.replace('_test.timeout = 15.0', '_test.timeout = 45.0')
    lines = ['testcase create_v100_saves:', '    click id "menu_start"',
             f'    advance until {quote(dialogue["s01_arrival_l005"]["text"])}',
             '    assert eval config.version == "1.0.0"',
             '    assert eval renpy.music.get_playing(channel="voice") == config.sample_voice',
             '    screenshot "upgrade-v100-first-voice"',
             '    $ renpy.unlink_save("1-4")', '    click id "save_open"',
             '    pause until screen "save"', '    click id "slot_4"',
             '    assert eval renpy.can_load("1-4")', '    click id "game_return"']
    for identity in route['choices']:
        lines += ['    advance until screen "choice"', f'    click {quote(choices[identity]["text"])}']
    lines += [f'    advance until {quote(dialogue["s07_true_l006"]["text"])}',
              '    pause until eval renpy.music.get_playing(channel="ambient") is None']
    lines += checkpoint_assertions(story, route, 's07_true_l006', 4, 'nearby_cafe', 'smile',
                                   'audio/bgm/next_message_theme.ogg', None)
    lines += ['    screenshot "upgrade-v100-late-save"',
              '    $ renpy.unlink_save("1-2")', '    click id "save_open"',
              '    pause until screen "save"', '    click id "slot_2"',
              '    assert eval renpy.can_load("1-2")', '']
    return setup + '\n'.join(lines)


def render_upgrade_reader(story):
    dialogue = {line['id']: line for node in story['nodes'] for line in scene_lines(node)}
    voice_file = next(v['file'] for v in json.loads((ROOT/'game/data/voice_manifest.json').read_text(encoding='utf-8'))['voices']
                      if v['line_id'] == 's01_arrival_l005')
    lines = ['testcase v100_voice_save_in_new_version:', '    run MainMenu(confirm=False)',
             '    assert eval renpy.can_load("1-4")', '    click id "load_open"',
             '    pause until screen "load"', '    click id "slot_4"',
             '    if screen "confirm":', '        click id "confirm_yes"',
             f'    pause until {quote(dialogue["s01_arrival_l005"]["text"])}',
             f'    assert eval config.version == {story["version"]!r}',
             '    assert eval current_scene == "s01_arrival"',
             '    assert eval affection == 0 and trust == 0 and not truth_known',
             '    assert id "voice_replay"',
             '    move pos (0.5, 0.4)',
             '    move "重听语音" pos (0.5, 0.5)', '    pause 0.1',
             '    click "重听语音" pos (0.5, 0.5)',
             f'    assert eval renpy.music.get_playing(channel="voice") == {voice_file!r}',
             '    screenshot "upgrade-v101-voice-load"', '    move id "what"', '    advance',
             f'    assert {quote(dialogue["s01_arrival_l006"]["text"])}', '    assert not id "voice_replay"',
             f'    $ test_history_voice_index = next(i for i, h in enumerate(_history_list) if h.voice and h.voice.filename == {voice_file!r})',
             '    click id "history_open"',
             '    move pos (0.5, 0.4)',
             '    move "重播语音" pos (0.5, 0.5)', '    pause 0.1',
             '    click "重播语音" pos (0.5, 0.5)',
             f'    assert eval renpy.music.get_playing(channel="voice") == {voice_file!r}',
             '    click id "game_return"',
             '    assert eval renpy.music.get_playing(channel="voice") is None', '']
    return render_persistence_tests(story) + '\n\n' + '\n'.join(lines)


def extract_package(file, destination, version):
    with zipfile.ZipFile(file) as archive:
        if archive.testzip() is not None:
            raise ValueError('Upgrade package CRC failed')
        metadata = [n for n in archive.namelist() if n.endswith('/game/cache/build_info.json')]
        if len(metadata) != 1 or json.loads(archive.read(metadata[0]))['version'] != version:
            raise ValueError('Upgrade package version mismatch')
        archive.extractall(destination)
    executables = list(destination.rglob('BeforeTheRainStops.exe'))
    if len(executables) != 1:
        raise ValueError('Upgrade package EXE missing or ambiguous')
    return executables[0]


def execute(exe, source, saves, evidence, screenshot_directory, timeout):
    (exe.parent/'game/testcases.rpy').write_bytes(source.encode('utf-8'))
    (exe.parent/'game/testcases.rpyc').unlink(missing_ok=True)
    try:
        result = run_native_tests([str(exe), str(exe.parent), 'test', 'global', '--report-detailed',
                                  '--overwrite-screenshots', '--savedir', str(saves)],
                                 cwd=exe.parent, evidence=evidence, timeout=timeout)
    finally:
        screenshots = collect_runtime_evidence(exe, evidence, screenshot_directory)
    (evidence/'test-plan.rpy').write_bytes(source.encode('utf-8'))
    print(result.stdout, flush=True)
    print(result.stderr, flush=True)
    if result.returncode:
        raise ValueError(f'Upgrade process failed with exit {result.returncode}')
    return validate_suite_evidence(result.stdout, source, screenshots, evidence)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous-zip', required=True, type=Path)
    parser.add_argument('--current-zip', required=True, type=Path)
    parser.add_argument('--timeout', type=positive_timeout, default=300)
    args = parser.parse_args()
    before = {'previous': digest(args.previous_zip), 'current': digest(args.current_zip)}
    if before['previous'] != BASELINE_SHA256:
        raise SystemExit('Previous ZIP differs from the exact published v1.0.0')
    story = load_story()
    with tempfile.TemporaryDirectory(prefix='galgame-upgrade-') as temp:
        root = Path(temp)
        previous = extract_package(args.previous_zip, root/'previous', BASELINE_VERSION)
        current = extract_package(args.current_zip, root/'current', story['version'])
        writer = execute(previous, render_upgrade_writer(story), root/'saves', ROOT/'reports/upgrade/writer',
                         'reports/upgrade-screenshots', args.timeout)
        reader = execute(current, render_upgrade_reader(story), root/'saves', ROOT/'reports/upgrade/reader',
                         'reports/persistence-screenshots', args.timeout)
    if before != {'previous': digest(args.previous_zip), 'current': digest(args.current_zip)}:
        raise SystemExit('Original upgrade packages changed during testing')
    report = {'status': 'passed', 'previous_version': BASELINE_VERSION, 'current_version': story['version'],
              'package_sha256': before, 'writer': writer, 'reader': reader,
              'original_packages_unmodified': True, 'human_listening': False}
    (ROOT/'reports/upgrade/acceptance.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('Published v1.0.0 saves loaded successfully in the current Windows EXE.')


if __name__ == '__main__':
    main()
