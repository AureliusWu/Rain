import copy
import json
import unittest
from tools.story_model import ROOT, load_story
from tools.compile_extras import render_extras

class ExtrasBindingTests(unittest.TestCase):
    def setUp(self):
        self.story = load_story()
        self.assets = json.loads((ROOT/'game/data/asset_manifest.json').read_text())['assets']

    def test_generated_bindings_are_current(self):
        self.assertEqual((ROOT/'game/script/extras_generated.rpy').read_text(), render_extras(self.story, self.assets))

    def test_missing_asset_refuses_generation(self):
        with self.assertRaises(KeyError):
            render_extras(self.story, [a for a in self.assets if a['id'] != 'unsent_letter'])

    def test_unused_content_refuses_unlock_binding(self):
        story = copy.deepcopy(self.story)
        for node in story['nodes']:
            if node.get('background') == 'unsent_letter': del node['background']
        with self.assertRaises(ValueError): render_extras(story, self.assets)

    def test_sound_effect_cannot_be_a_music_entry(self):
        assets = copy.deepcopy(self.assets)
        next(a for a in assets if a['id']=='rain_theme')['audio_role'] = 'sfx'
        with self.assertRaises(ValueError): render_extras(self.story, assets)

if __name__ == '__main__': unittest.main()
