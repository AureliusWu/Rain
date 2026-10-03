import copy
import unittest
from tools.story_model import load_story, enumerate_routes, apply_effects


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.story = load_story()

    def test_all_authored_endings_reachable(self):
        report = enumerate_routes(self.story)
        self.assertEqual(report["errors"], [])
        self.assertEqual({r["ending"] for r in report["routes"]}, {"normal", "true"})

    def test_choice_combinations_are_exhaustive(self):
        report = enumerate_routes(self.story)
        expected = self.story["expected_routes"]
        self.assertEqual(len(report["routes"]), expected)

    def test_missing_target_fails(self):
        self.story["nodes"][0]["next"] = "missing_label"
        self.assertTrue(any("missing target" in e for e in enumerate_routes(self.story)["errors"]))

    def test_loop_fails(self):
        self.story["nodes"][0]["next"] = self.story["entry"]
        self.assertTrue(any("Infinite loop" in e for e in enumerate_routes(self.story)["errors"]))

    def test_duplicate_id_fails(self):
        self.story["nodes"].append(copy.deepcopy(self.story["nodes"][0]))
        self.assertIn("Duplicate scene ID", enumerate_routes(self.story)["errors"])

    def test_unreachable_ending_fails(self):
        self.story["nodes"].append({"id": "orphan", "location": "station", "time": "night", "ending": "unused"})
        self.assertTrue(any("Unreachable ending" in e for e in enumerate_routes(self.story)["errors"]))

    def test_invalid_state_type_fails(self):
        choice = next(n["choices"][0] for n in self.story["nodes"] if "choices" in n)
        choice["effects"] = {"truth_known": 1}
        self.assertTrue(any("invalid effect" in e for e in enumerate_routes(self.story)["errors"]))

    def test_effects_preserve_previous_state(self):
        initial = {"affection": 0, "trust": 0, "truth_known": False}
        new = apply_effects({"trust": -1, "truth_known": True}, initial)
        self.assertEqual(new, {"affection": 0, "trust": -1, "truth_known": True})
        self.assertEqual(initial["trust"], 0)


if __name__ == "__main__":
    unittest.main()
