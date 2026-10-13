import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CreativeRevisionTests(unittest.TestCase):
    def test_native_story_keeps_positions_routes_and_recorded_words(self):
        run=subprocess.run(['node','scripts/vn-creative.mjs','docs/production/CREATIVE-BASELINE-v1.json','game/data/story.json'],cwd=ROOT,check=True,capture_output=True,text=True)
        report=json.loads(run.stdout)
        self.assertEqual(report['revisedParagraphs'],43)
        self.assertEqual(report['protectedVoices'],17)
        self.assertTrue(report['savePositionsPreserved'])
        self.assertTrue(report['routeContractPreserved'])
