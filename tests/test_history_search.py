import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

MODULE = Path(__file__).resolve().parents[1] / "game/python-packages/replay_search.py"
spec = importlib.util.spec_from_file_location("replay_search", MODULE)
search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search)


class ReadHistorySearchTests(unittest.TestCase):
    def setUp(self):
        self.voice = SimpleNamespace(who="许澄", what="三号接收口 Ｄ３", voice="original-voice")
        self.history = [SimpleNamespace(who=None, what="钥匙响了。"), self.voice, self.voice]

    def test_normalization_and_speaker_intersection(self):
        self.assertEqual(search.filter_history(self.history, " d3\n三号 ", "许澄"), [(1, self.voice), (2, self.voice)])
        self.assertEqual(search.filter_history(self.history, "d3", "旁白"), [])
        self.assertEqual(search.history_speakers(self.history), ["旁白", "许澄"])

    def test_original_indices_voice_and_repeated_visits_survive_filtering(self):
        found = search.filter_history(self.history, "三号")
        self.assertIs(found[0][1], self.voice)
        self.assertEqual([index for index, entry in found], [1, 2])
        self.assertEqual(self.history[1].voice, "original-voice")

    def test_unread_text_is_absent_and_native_tags_are_removed_before_matching(self):
        self.assertEqual(search.filter_history(self.history[:1], "三号"), [])
        tagged = SimpleNamespace(who="许澄", what="{color=red}旧信{/color}")
        plain = lambda value: value.replace("{color=red}", "").replace("{/color}", "")
        self.assertEqual(search.filter_history([tagged], "color", plain=plain), [])
        self.assertEqual(search.filter_history([tagged], "旧信", plain=plain), [(0, tagged)])
