import importlib.util
from pathlib import Path
import sys
import textwrap
from types import SimpleNamespace
import unittest
from unittest.mock import patch

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


class NativeHistoryPanelTests(unittest.TestCase):
    def setUp(self):
        self.scope = {"history_query": "出门", "history_speaker": "许澄", "history_session": "current-panel"}
        self.screen = SimpleNamespace(scope=self.scope)
        self.stops, self.restarts = [], []
        renpy = SimpleNamespace(
            get_screen=lambda name: self.screen,
            set_screen_variable=lambda name, value, **kwargs: self.scope.__setitem__(name, value),
            restart_interaction=lambda: self.restarts.append(True),
            music=SimpleNamespace(stop=lambda **kwargs: self.stops.append(kwargs)),
        )
        source = MODULE.parents[1].joinpath("history_search.rpy").read_text(encoding="utf-8")
        block = textwrap.dedent(source.split("init python:\n", 1)[1].split("\nstyle ", 1)[0])
        self.runtime = {"renpy": renpy, "InputValue": object}
        with patch.dict(sys.modules, {"replay_search": search}):
            exec(compile(block, "game/history_search.rpy", "exec"), self.runtime)

    def test_clear_action_returns_none_and_preserves_current_panel(self):
        self.assertIsNone(self.runtime["rain_clear_history_filters"]("current-panel"), "A non-None Function result closes the Ren'Py menu")
        self.assertEqual(self.scope, {"history_query": "", "history_speaker": "", "history_session": "current-panel"})
        self.assertEqual(self.stops, [{"channel": "voice"}])

    def test_late_clear_cannot_change_the_reopened_panel(self):
        before = dict(self.scope)
        self.assertIsNone(self.runtime["rain_clear_history_filters"]("closed-panel"))
        self.assertEqual(self.scope, before)
        self.assertEqual((self.stops, self.restarts), ([], []))

    def test_query_rejects_nontext_or_closed_panel_and_caps_unicode(self):
        update = self.runtime["rain_set_history_query"]
        self.assertFalse(update(None, "current-panel"))
        self.assertTrue(update("界" * 90, "current-panel"))
        self.assertEqual(self.scope["history_query"], "界" * 80)
        self.screen = None
        self.assertFalse(update("迟到", "current-panel"))

    def test_native_input_value_cannot_write_into_a_new_panel(self):
        value = self.runtime["RainHistoryInputValue"]("current-panel")
        self.assertEqual(value.get_text(), "出门")
        self.scope["history_session"] = "reopened-panel"
        value.set_text("迟到")
        self.assertEqual(value.get_text(), "")
        self.assertEqual(self.scope["history_query"], "出门")
