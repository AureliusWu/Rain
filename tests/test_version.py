"""Prevent a new native build from carrying an old player or browser version."""
import json
import re
import unittest
from tools.story_model import ROOT, load_story


class PlatformVersionTests(unittest.TestCase):
    def test_current_platform_metadata_matches_native_version(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertEqual(load_story()["version"], version)
        options = (ROOT / "game/options.rpy").read_text(encoding="utf-8")
        self.assertEqual(re.search(r'define config.version = "([^"]+)"', options)[1], version)
        player = (ROOT / "PLAYER_README.txt").read_text(encoding="utf-8")
        self.assertEqual(re.search(r"^版本：(.*)$", player, re.MULTILINE)[1], version)
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(package["version"], version)
        self.assertEqual(lock["version"], version)
        self.assertEqual(lock["packages"][""]["version"], version)
