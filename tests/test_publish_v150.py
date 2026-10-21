import copy
import re
import tempfile
from pathlib import Path
import unittest
import zipfile

from tools import publish_v150 as publication
from tools.build.verify_voice_smoke import prefix_plan
from tools.build.verify_package import required_screenshots


class CurrentPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.package = Path(cls.temp.name)/'BeforeTheRainStops-1.5.0-win.zip'
        assets = publication.read(publication.ROOT/'game/data/asset_manifest.json')['assets']
        with zipfile.ZipFile(cls.package, 'w') as bundle:
            for asset in assets:
                bundle.write(publication.ROOT/'game'/asset['file'], 'BeforeTheRainStops-1.5.0-win/game/'+asset['file'])
        cls.sha = 'a'*40
        plans = publication.native_plans()
        def suite(plan):
            return dict(cases=len(re.findall(r'^testcase ', plan, re.M)),
                assertions=len(re.findall(r'^\s+assert ', plan, re.M)), screenshots_checked=len(required_screenshots(plan)),
                failed=0, xfailed=0, xpassed=0, skipped=0, not_run=0, process=dict(returncode=0, timed_out=False))
        shots = [dict(scope=scope, name=name) for scope, plan in plans.items() for name in required_screenshots(plan)]
        cls.machine = dict(version='1.5.0', candidate_commit=cls.sha, run_id=123,
            status='technical_passed_visual_pending', human_acceptance_is_not_claimed=True,
            full_dialogue=dict(project='Rain',target=306,accepted=306,complete=True,status='passed',humanListening=False),
            human_pending=publication.HUMAN_PENDING, unresolved_machine_issues=[],
            suites={scope: suite(plan) for scope, plan in plans.items()}, screenshots=shots, screenshots_count=len(shots),
            voice_smoke=dict(status='passed', iterations=[suite(prefix_plan(plans['source']))]*2),
            extras=dict(images=12, music_tracks=4), upgrade=dict(status='passed', package_sha256=dict(current=publication.digest(cls.package))),
            package=dict(file=cls.package.name, sha256=publication.digest(cls.package), size_in_bytes=cls.package.stat().st_size,
                         crc='passed', assets_checked=len(assets), test_scripts_in_original_zip=False))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_accepts_the_complete_current_native_plan_and_all_packaged_assets(self):
        publication.validate_native(self.machine, self.sha, 123, self.package)

    def test_rejects_stale_inventory_and_omitted_native_cases(self):
        for kind in ('assets', 'cases', 'screenshots', 'skipped', 'human', 'dialogue'):
            machine = copy.deepcopy(self.machine)
            if kind == 'assets': machine['package']['assets_checked'] = 87
            if kind == 'cases': machine['suites']['source']['cases'] -= 1
            if kind == 'screenshots': machine['screenshots'].pop()
            if kind == 'skipped': machine['suites']['standalone']['skipped'] = 1
            if kind == 'human': machine['human_acceptance_is_not_claimed'] = False
            if kind == 'dialogue': machine['full_dialogue']['accepted'] = 305
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                publication.validate_native(machine, self.sha, 123, self.package)

    def test_waits_for_both_exact_main_runs(self):
        runs = [dict(id=index, path=path, head_sha=self.sha, head_branch='main', event='push',
                     status='completed', conclusion='success', run_attempt=1,
                     repository=dict(full_name='AureliusWu/Rain')) for index, path in enumerate(
                     ('.github/workflows/game.yml', '.github/workflows/web.yml'), 1)]
        self.assertEqual(set(publication.select_runs(runs, self.sha)), {'native', 'web'})
        for field, value in [('head_sha', 'b'*40), ('conclusion', 'failure'), ('event', 'pull_request')]:
            changed = copy.deepcopy(runs); changed[1][field] = value
            with self.subTest(field=field): self.assertIsNone(publication.select_runs(changed, self.sha))


if __name__ == '__main__':
    unittest.main()
