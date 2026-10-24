"""The music release must promote the current, complete native/PWA artifacts."""
import copy
import re
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools import publish_v170 as publication
from tools.build.verify_package import required_screenshots
from tools.build.verify_voice_smoke import prefix_plan


class MusicPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.package = Path(cls.temp.name) / 'BeforeTheRainStops-1.7.0-win.zip'
        cls.prefix = 'BeforeTheRainStops-1.7.0-win/game/'
        assets = publication.read(publication.ROOT / 'game/data/asset_manifest.json')['assets']
        with zipfile.ZipFile(cls.package, 'w') as bundle:
            for asset in assets:
                bundle.write(publication.ROOT / 'game' / asset['file'], cls.prefix + asset['file'])
        cls.sha = 'a' * 40
        plans = publication.native_plans()

        def suite(plan):
            return dict(cases=len(re.findall(r'^testcase ', plan, re.M)),
                        assertions=len(re.findall(r'^\s+assert ', plan, re.M)),
                        screenshots_checked=len(required_screenshots(plan)), failed=0,
                        xfailed=0, xpassed=0, skipped=0, not_run=0,
                        process=dict(returncode=0, timed_out=False))

        shots = [dict(scope=scope, name=name) for scope, plan in plans.items()
                 for name in required_screenshots(plan)]
        cls.machine = dict(version='1.7.0', candidate_commit=cls.sha, run_id=123,
            status='technical_passed_visual_pending', human_acceptance_is_not_claimed=True,
            full_dialogue=dict(project='Rain', target=306, accepted=306, complete=True,
                               status='passed', humanListening=False),
            human_pending=publication.HUMAN_PENDING, unresolved_machine_issues=[],
            suites={scope: suite(plan) for scope, plan in plans.items()}, screenshots=shots,
            screenshots_count=len(shots),
            voice_smoke=dict(status='passed', iterations=[suite(prefix_plan(plans['source']))] * 2),
            extras=dict(images=12, music_tracks=6),
            upgrade=dict(status='passed', package_sha256=dict(current=publication.digest(cls.package))),
            package=dict(file=cls.package.name, sha256=publication.digest(cls.package),
                         size_in_bytes=cls.package.stat().st_size, crc='passed',
                         assets_checked=len(assets), test_scripts_in_original_zip=False))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_accepts_complete_current_music_release(self):
        publication.validate_native(self.machine, self.sha, 123, self.package)

    def test_rejects_stale_version_inventory_and_incomplete_runtime_tests(self):
        changes = [('version', '1.6.0'), ('candidate_commit', 'b' * 40), ('run_id', 122)]
        for field, value in changes:
            with self.subTest(field=field), self.assertRaises(ValueError):
                publication.validate_native({**self.machine, field: value}, self.sha, 123, self.package)
        for kind in ('music', 'case', 'skip', 'dialogue'):
            machine = copy.deepcopy(self.machine)
            if kind == 'music': machine['extras']['music_tracks'] = 4
            if kind == 'case': machine['suites']['source']['cases'] -= 1
            if kind == 'skip': machine['suites']['standalone']['skipped'] = 1
            if kind == 'dialogue': machine['full_dialogue']['accepted'] -= 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                publication.validate_native(machine, self.sha, 123, self.package)

    def test_rejects_changed_music_even_when_outer_package_digest_was_updated(self):
        with tempfile.TemporaryDirectory() as temp:
            tampered = Path(temp) / self.package.name
            with zipfile.ZipFile(self.package) as original, zipfile.ZipFile(tampered, 'w') as output:
                for name in original.namelist():
                    data = original.read(name)
                    if name == self.prefix + 'audio/bgm/rain-platform.ogg': data = b'changed score'
                    output.writestr(name, data)
            machine = copy.deepcopy(self.machine)
            machine['package'].update(sha256=publication.digest(tampered), size_in_bytes=tampered.stat().st_size)
            machine['upgrade']['package_sha256']['current'] = publication.digest(tampered)
            with self.assertRaisesRegex(ValueError, 'Packaged asset differs'):
                publication.validate_native(machine, self.sha, 123, tampered)

    def test_waits_for_both_exact_successful_main_builds(self):
        runs = [dict(id=index, path=path, head_sha=self.sha, head_branch='main', event='push',
                     status='completed', conclusion='success', run_attempt=1,
                     repository=dict(full_name='AureliusWu/Rain')) for index, path in enumerate(
                     ('.github/workflows/game.yml', '.github/workflows/web.yml'), 1)]
        self.assertEqual(set(publication.select_runs(runs, self.sha)), {'native', 'web'})
        for field, value in [('head_sha', 'b' * 40), ('conclusion', 'failure'), ('event', 'pull_request')]:
            changed = copy.deepcopy(runs)
            changed[1][field] = value
            with self.subTest(field=field): self.assertIsNone(publication.select_runs(changed, self.sha))

    def test_previous_publication_workflow_is_frozen_to_the_published_commit(self):
        workflow = (publication.ROOT / '.github/workflows/release-v160.yml').read_text()
        frozen = 'b820f868e4fe10a9d74d2a35769696a0b1550ef6'
        condition = next(line.strip() for line in workflow.splitlines() if line.strip().startswith('if:'))
        self.assertIn("github.sha == '" + frozen + "'", condition)
        self.assertIn("github.event.workflow_run.head_sha == '" + frozen + "'", condition)

    def test_web_requires_current_version_help_and_exact_public_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / 'web.zip'
            with zipfile.ZipFile(package, 'w') as bundle: bundle.writestr('index.html', '<html></html>')
            build = dict(status='built', version='1.7.0', revision='music',
                engine='RenPy 8.5.3 official WASM',
                web_sdk_sha256='954db897e65f51ea63cb2fb7b203d02be0447f4e22069514020bbe6c6691fdfc',
                official_runtime_validation=dict(game_zip_crc='passed'), web_zip_sha256=publication.digest(package))
            checks = ['desktop help opens from title and reading menus and preserves native reading state',
                      'touch help at 412x915, 568x320 and 844x390 opens from title and reading menus without advancing']
            acceptance = dict(status='passed', version='1.7.0', checks=checks + ['baseline-' + str(i) for i in range(16)],
                              errors=[], requests_outside_application=[])
            public = dict(status='passed', version='1.7.0', revision='music', errors=[],
                          target='https://aureliuswu.github.io/Rain/', exact_tested_artifact=True,
                          human_physical_device=False)
            publication.validate_web(build, acceptance, public, package)
            for field, value in [('version', '1.6.0'), ('checks', ['old-check'] * 18), ('errors', ['runtime error'])]:
                with self.subTest(field=field), self.assertRaises(ValueError):
                    publication.validate_web(build, {**acceptance, field: value}, public, package)
            with self.assertRaises(ValueError):
                publication.validate_web(build, acceptance, {**public, 'revision': 'old'}, package)


if __name__ == '__main__':
    unittest.main()
