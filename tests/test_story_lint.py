import unittest
from tools.story_model import load_story
from tools.story_lint import lint


class StoryLintTests(unittest.TestCase):
    def test_runtime_version_mismatch_is_rejected(self):
        story = load_story()
        story["version"] = "0.0.0"
        self.assertIn("Story / VERSION / config.version mismatch", lint(story)[0])

    def test_scene_prompt_change_requires_new_hash(self):
        story = load_story()
        story["nodes"][0]["draft_prompt_sha256"] = "0" * 64
        self.assertTrue(any("stale Scene Prompt" in e for e in lint(story)[0]))
