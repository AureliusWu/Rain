import json
import unittest
from tools.asset_validator import validate_assets
from tools.story_model import ROOT, load_story


class AssetTests(unittest.TestCase):
    def test_all_assets_and_voice_bindings_are_valid(self):
        self.assertEqual(validate_assets(), [])

    def test_missing_background_reference_fails(self):
        story = load_story()
        story["nodes"][0]["background"] = "missing_art"
        self.assertTrue(any("missing background" in x for x in validate_assets(story=story)))

    def test_missing_voice_reference_fails(self):
        story = load_story()
        story["nodes"][0]["lines"][0]["voice"] = "missing_voice"
        self.assertTrue(any("missing voice" in x for x in validate_assets(story=story)))

    def test_character_asset_alpha(self):
        from PIL import Image
        assets = json.loads((ROOT / "game/data/asset_manifest.json").read_text())["assets"]
        for asset in assets:
            if asset["type"] == "sprite":
                with Image.open(ROOT / "game" / asset["file"]) as image:
                    self.assertIn("A", image.getbands())
                    low, high = image.getchannel("A").getextrema()
                    self.assertEqual(low, 0)
                    self.assertGreaterEqual(high, 250)


if __name__ == "__main__":
    unittest.main()
