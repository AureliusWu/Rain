import copy
import json
import unittest
from tools.story_model import ROOT, load_story
from tools.compile_story import render_story
from tools.compile_extras import render_extras
from tools.asset_validator import validate_assets
from tools.audio_validator import validate_audio


class SceneMediaTests(unittest.TestCase):
    def setUp(self):
        self.story = load_story()
        self.assets = json.loads((ROOT / 'game/data/asset_manifest.json').read_text())['assets']
        self.voices = json.loads((ROOT / 'game/data/voice_manifest.json').read_text())['voices']

    def test_photo_event_starts_at_the_photo_and_restores_the_cafe(self):
        script, _ = render_story(self.story, self.assets, self.voices)
        section = script.split('label s07_true:')[1]
        photo = section.index('scene expression "cg/cafe-photo.png"')
        self.assertLess(section.index('rain_line_id = "s07_true_l010"'), photo)
        self.assertLess(photo, section.index('rain_line_id = "s07_true_l011"'))
        restored = section.index('scene expression "backgrounds/nearby_cafe.png"', photo)
        self.assertLess(restored, section.index('rain_line_id = "v07_s07_true_l011"'))
        self.assertIn('show heroine smile', section[restored:])
        self.assertIn('play music "audio/bgm/cafe-photo.ogg"', section[photo:])

    def test_line_event_assets_are_in_the_native_unlock_catalog(self):
        generated = render_extras(self.story, self.assets)
        self.assertIn('cg/cafe-photo.png', generated)
        self.assertIn('audio/bgm/cafe-photo.ogg', generated)

    def test_missing_line_art_and_wrong_music_role_are_rejected(self):
        story = copy.deepcopy(self.story)
        line = next(n for n in story['nodes'] if n['id'] == 's07_true')['lines'][0]
        line['background'] = 'missing-event-image'
        line['bgm'] = 'paper_rustle'
        self.assertTrue(any('line background' in error for error in validate_assets(story=story)))
        errors, _ = validate_audio(assets=self.assets, story=story)
        self.assertTrue(any('line music' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
