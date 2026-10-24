import copy
import re
import tempfile
from pathlib import Path
import unittest
import zipfile

from tools import publish_v160 as publication
from tools.build.verify_voice_smoke import prefix_plan
from tools.build.verify_package import required_screenshots


class CurrentPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.package = Path(cls.temp.name)/'BeforeTheRainStops-1.6.0-win.zip'
        assets = publication.read(publication.ROOT/'game/data/asset_manifest.json')['assets']
        with zipfile.ZipFile(cls.package, 'w') as bundle:
            for asset in assets:
                bundle.write(publication.ROOT/'game'/asset['file'], 'BeforeTheRainStops-1.6.0-win/game/'+asset['file'])
        cls.sha = 'a'*40
        plans = publication.native_plans()
        def suite(plan):
            return dict(cases=len(re.findall(r'^testcase ', plan, re.M)),
                assertions=len(re.findall(r'^\s+assert ', plan, re.M)), screenshots_checked=len(required_screenshots(plan)),
                failed=0, xfailed=0, xpassed=0, skipped=0, not_run=0, process=dict(returncode=0, timed_out=False))
        shots = [dict(scope=scope, name=name) for scope, plan in plans.items() for name in required_screenshots(plan)]
        cls.machine = dict(version='1.6.0', candidate_commit=cls.sha, run_id=123,
            status='technical_passed_visual_pending', human_acceptance_is_not_claimed=True,
            full_dialogue=dict(project='Rain',target=306,accepted=306,complete=True,status='passed',humanListening=False),
            human_pending=publication.HUMAN_PENDING, unresolved_machine_issues=[],
            suites={scope: suite(plan) for scope, plan in plans.items()}, screenshots=shots, screenshots_count=len(shots),
            voice_smoke=dict(status='passed', iterations=[suite(prefix_plan(plans['source']))]*2),
            extras=dict(images=12, music_tracks=6), upgrade=dict(status='passed', package_sha256=dict(current=publication.digest(cls.package))),
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


    def test_help_regression_is_in_the_complete_native_plan(self):
        for scope in ('source', 'standalone'):
            self.assertIn('testcase help_menu_pauses_and_restores:', publication.native_plans()[scope])

    def test_historical_v150_workflow_is_bound_to_its_original_commit(self):
        workflow = (publication.ROOT/'.github/workflows/release-v150.yml').read_text()
        frozen = 'e4856b5a5f44803e1c1b263534702f5d7d8c80dc'
        condition = next(line.strip() for line in workflow.splitlines() if line.strip().startswith('if:'))
        self.assertIn("github.sha == '"+frozen+"'", condition)
        self.assertIn("github.event.workflow_run.head_sha == '"+frozen+"'", condition)

    def test_web_acceptance_requires_current_help_checks_and_exact_version(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)/'web.zip'
            with zipfile.ZipFile(package, 'w') as bundle:
                bundle.writestr('index.html', '<html></html>')
            build = dict(status='built', version='1.6.0', revision='current',
                engine='RenPy 8.5.3 official WASM',
                web_sdk_sha256='954db897e65f51ea63cb2fb7b203d02be0447f4e22069514020bbe6c6691fdfc',
                official_runtime_validation=dict(game_zip_crc='passed'), web_zip_sha256=publication.digest(package))
            checks = ['desktop help opens from title and reading menus and preserves native reading state',
                'touch help at 412x915, 568x320 and 844x390 opens from title and reading menus without advancing']
            acceptance = dict(status='passed', version='1.6.0', checks=checks+['baseline-'+str(i) for i in range(16)],
                errors=[], requests_outside_application=[])
            public = dict(status='passed', version='1.6.0', revision='current', errors=[],
                target='https://aureliuswu.github.io/Rain/', exact_tested_artifact=True, human_physical_device=False)
            publication.validate_web(build, acceptance, public, package)
            for field, value in [('version', '1.5.0'), ('checks', ['old-check']*18), ('errors', ['runtime error'])]:
                with self.subTest(field=field), self.assertRaises(ValueError):
                    publication.validate_web(build, {**acceptance,field:value}, public, package)


if __name__ == '__main__':
    unittest.main()
