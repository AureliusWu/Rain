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
        orphan = copy.deepcopy(self.story["nodes"][-1])
        orphan.update(id="orphan", ending="unused", lines=[{"id": "orphan_l001", "speaker": "n", "text": "另一条路。"}])
        self.story["nodes"].append(orphan)
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

    def test_early_hesitation_can_be_repaired(self):
        routes = enumerate_routes(self.story)["routes"]
        for choices in (["q01_care", "q02_defer", "q04_revisit", "q03_walk"],
                        ["q01_business", "q02_honest", "q04_revisit", "q03_walk"]):
            route = next(r for r in routes if r["choices"] == choices)
            self.assertEqual(route["ending"], "true")

    def test_leaving_always_respects_players_action(self):
        routes = enumerate_routes(self.story)["routes"]
        for route in routes:
            if route["choices"][-1] == "q03_leave":
                self.assertEqual(route["ending"], "normal")
                self.assertIn("s05_separate_path", route["path"])
                self.assertNotIn("s06_resolution", route["path"])
        high_state = next(r for r in routes if r["choices"] == ["q01_care", "q02_honest", "q04_revisit", "q03_leave"])
        self.assertGreaterEqual(high_state["state"]["affection"], 2)
        self.assertGreaterEqual(high_state["state"]["trust"], 2)

    def test_declared_facts_and_chapters_on_every_route(self):
        report = enumerate_routes(self.story)
        self.assertEqual(sum(r["ending"] == "true" for r in report["routes"]), 4)
        for route in report["routes"]:
            for chapter in self.story["chapters"]:
                self.assertIn(chapter["entry"], route["path"])
            if "q02_defer" in route["choices"] and "q04_concrete" in route["choices"]:
                self.assertFalse(route["state"]["truth_known"])

    def test_both_trust_branches_are_reachable(self):
        routes = enumerate_routes(self.story)["routes"]
        self.assertTrue(any("s04_open" in r["path"] for r in routes))
        self.assertTrue(any("s04_reserved" in r["path"] for r in routes))

    def test_global_choice_id_collision_fails(self):
        choices = [n["choices"] for n in self.story["nodes"] if "choices" in n]
        choices[1][0]["id"] = choices[0][0]["id"]
        self.assertTrue(any("duplicate choice ID" in e for e in enumerate_routes(self.story)["errors"]))

    def test_zero_effect_and_identical_consequence_fail(self):
        choices = next(n["choices"] for n in self.story["nodes"] if "choices" in n)
        choices[0]["effects"] = {"trust": 0}
        choices[1]["next"] = choices[0]["next"]
        errors = enumerate_routes(self.story)["errors"]
        self.assertTrue(any("zero state effect" in e for e in errors))
        self.assertTrue(any("distinct consequence" in e for e in errors))

    def test_early_unconditional_route_fails(self):
        node = next(n for n in self.story["nodes"] if "routes" in n)
        node["routes"][0].pop("when")
        self.assertTrue(any("fallback must follow" in e for e in enumerate_routes(self.story)["errors"]))

    def test_backwards_time_fails(self):
        self.story["nodes"][1]["time"] = "21:30"
        self.assertTrue(any("Backwards timeline" in e for e in enumerate_routes(self.story)["errors"]))

    def test_missing_chapter_and_draft_fail(self):
        node = self.story["nodes"][0]
        node["chapter"] = "ch99"
        node["lines"] = []
        errors = enumerate_routes(self.story)["errors"]
        self.assertTrue(any("unknown chapter" in e for e in errors))
        self.assertTrue(any("missing scene draft" in e for e in errors))

    def test_out_of_range_state_fails(self):
        choices = next(n["choices"] for n in self.story["nodes"] if "choices" in n)
        choices[0]["effects"]["trust"] = 99
        self.assertTrue(any("State outside bounds" in e for e in enumerate_routes(self.story)["errors"]))


if __name__ == "__main__":
    unittest.main()
