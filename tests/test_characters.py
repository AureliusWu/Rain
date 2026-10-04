import json
import unittest
from PIL import Image
from tools.character_validator import geometry, validate_characters
from tools.story_model import ROOT, load_story


class CharacterTests(unittest.TestCase):
    def test_all_seven_expressions_are_aligned_and_used(self):
        errors, metrics = validate_characters()
        self.assertEqual(errors, [])
        self.assertEqual(len(metrics), 7)

    def test_missing_expression_is_rejected(self):
        assets = json.loads((ROOT / "game/data/asset_manifest.json").read_text(encoding="utf-8"))["assets"]
        assets = [a for a in assets if a.get("expression") != "happy"]
        errors, _ = validate_characters(assets=assets)
        self.assertTrue(any("expression set" in error for error in errors))

    def test_removed_story_expression_cue_is_rejected(self):
        story = load_story()
        for node in story["nodes"]:
            for line in node.get("lines", []):
                if line.get("expression") == "angry":
                    line.pop("expression")
        errors, _ = validate_characters(story=story)
        self.assertIn("Unused heroine expression: angry", errors)

    def test_shifted_sprite_is_detected(self):
        original = Image.new("RGBA", (120, 120))
        original.paste((255, 255, 255, 255), (20, 10, 80, 100))
        shifted = Image.new("RGBA", (120, 120))
        shifted.paste(original, (20, 0))
        result = geometry(original, shifted)
        self.assertEqual(result["bbox_delta"], 20)
        self.assertLess(result["silhouette_iou"], 0.97)


if __name__ == "__main__":
    unittest.main()
