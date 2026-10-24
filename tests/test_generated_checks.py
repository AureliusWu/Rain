"""Exercise real generator CLI failure codes in an isolated authoring fixture."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from tools.story_model import ROOT
from tools.story_model import load_story
from tools.compile_tests import render_tests


class GeneratedCheckTests(unittest.TestCase):
    def test_choice_save_expects_the_latest_authored_scene_music(self):
        story = load_story()
        next(n for n in story['nodes'] if n['id'] == 's01_platform')['bgm'] = 'unspoken_theme'
        generated = render_tests(story)
        save_test = generated.split('testcase save_load_and_restart:')[1].split('testcase ')[0]
        self.assertIn("renpy.music.get_playing(channel=\"music\") == 'audio/bgm/unspoken_theme.ogg'", save_test)

    def test_choice_save_expects_line_music_when_it_overrides_the_scene(self):
        story = load_story()
        node = next(n for n in story['nodes'] if n['id'] == 's01_platform')
        node['lines'][-1]['bgm'] = 'next_message_theme'
        generated = render_tests(story)
        save_test = generated.split('testcase save_load_and_restart:')[1].split('testcase ')[0]
        self.assertIn("renpy.music.get_playing(channel=\"music\") == 'audio/bgm/next_message_theme.ogg'", save_test)

    def check_stale(self, module, relative_path):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'tools').mkdir()
            for name in ['__init__.py', 'story_model.py', 'compile_story.py', 'compile_tests.py', 'compile_extras.py', 'extras_tests.py']:
                shutil.copy2(ROOT / 'tools' / name, root / 'tools' / name)
            shutil.copytree(ROOT / 'game/python-packages', root / 'game/python-packages')
            (root / 'game/data').mkdir(parents=True)
            for name in ['story.json', 'asset_manifest.json', 'voice_manifest.json', 'full_voice_manifest.json']:
                shutil.copy2(ROOT / 'game/data' / name, root / 'game/data' / name)
            command = [sys.executable, '-m', module]
            generated = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=10)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            current = subprocess.run(command + ['--check'], cwd=root, capture_output=True, text=True, timeout=10)
            self.assertEqual(current.returncode, 0, current.stderr)
            path = root / relative_path
            path.write_text(path.read_text(encoding='utf-8') + '\n# stale hand edit\n', encoding='utf-8')
            stale = subprocess.run(command + ['--check'], cwd=root, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn('Stale generated', stale.stderr)
            path.unlink()
            missing = subprocess.run(command + ['--check'], cwd=root, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn('Stale generated', missing.stderr)

    def test_story_script_staleness_and_missing_output_fail_cli(self):
        self.check_stale('tools.compile_story', 'game/script/story_generated.rpy')

    def test_interaction_test_staleness_and_missing_output_fail_cli(self):
        self.check_stale('tools.compile_tests', 'game/testcases.rpy')

    def test_extras_binding_staleness_and_missing_output_fail_cli(self):
        self.check_stale('tools.compile_extras', 'game/script/extras_generated.rpy')
