import copy
import json
from pathlib import Path
import unittest
from tools.build.export_review import validate_plan_summary, validate_asset_inventory
from tools.build.verify_voice_smoke import prefix_plan


class ExportReviewCurrentPlanTests(unittest.TestCase):
    def setUp(self):
        self.plan=(Path(__file__).resolve().parents[1]/'game/testcases.rpy').read_text(encoding='utf-8')
        self.summary=dict(cases=39,assertions=521,screenshots_checked=91,
            failed=0,xfailed=0,xpassed=0,skipped=0,not_run=0)

    def test_history_regression_is_part_of_the_full_and_prefix_totals(self):
        self.assertIn('testcase history_search_and_original_voice:',self.plan)
        validate_plan_summary(self.summary,self.plan,'source')
        short={**self.summary,'cases':7,'assertions':149,'screenshots_checked':33}
        validate_plan_summary(short,prefix_plan(self.plan),'prefix')

    def test_old_totals_are_rejected_instead_of_marked_passed(self):
        for field,value in [('cases',36),('assertions',448),('screenshots_checked',82)]:
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate_plan_summary({**self.summary,field:value},self.plan,'source')

    def test_partial_or_noninteger_results_are_rejected(self):
        for field,value in [('failed',1),('skipped',1),('not_run',1),('xfailed',1),('xpassed',1),('failed',False),('cases',37.0)]:
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate_plan_summary({**self.summary,field:value},self.plan,'source')

    def test_current_manifest_audits_all_shipping_assets(self):
        root = Path(__file__).resolve().parents[1]
        assets = json.loads((root/'game/data/asset_manifest.json').read_text())['assets']
        self.assertEqual(validate_asset_inventory(assets), 388)

    def test_empty_or_duplicate_manifest_cannot_be_counted_as_audit_success(self):
        for assets in [[], [{'id': 'a', 'file': 'one.png'}] * 2,
                       [{'id': 'a', 'file': 'one.png'}, {'id': 'b', 'file': 'one.png'}]]:
            with self.subTest(assets=assets), self.assertRaises(ValueError):
                validate_asset_inventory(assets)


if __name__=='__main__':unittest.main()
