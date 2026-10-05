import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image
from tools.build.verify_package import run_native_tests, collect_runtime_evidence, validate_native_report, validate_screenshots


class NativeProcessEvidenceTests(unittest.TestCase):
    def test_success_records_real_output_and_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); evidence=root/'reports'
            result=run_native_tests([sys.executable, '-c', 'print("native suite complete")'],
                                    cwd=root, evidence=evidence, timeout=5)
            report=json.loads((evidence/'process.json').read_text())
            self.assertEqual(result.returncode, 0)
            self.assertFalse(report['timed_out'])
            self.assertIn('native suite complete', (evidence/'stdout.txt').read_text())

    def test_timeout_preserves_output_and_partial_ui_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); evidence=root/'evidence'; shots=root/'reports/screenshots'; shots.mkdir(parents=True)
            (shots/'partial.png').write_bytes(b'partial screenshot evidence')
            (root/'log.txt').write_text('engine started')
            with self.assertRaises(subprocess.TimeoutExpired):
                run_native_tests([sys.executable, '-u', '-c', 'import time; print("started", flush=True); time.sleep(5)'],
                                 cwd=root, evidence=evidence, timeout=1)
            collect_runtime_evidence(root/'game.exe', evidence)
            report=json.loads((evidence/'process.json').read_text())
            self.assertTrue(report['timed_out'])
            self.assertIsNone(report['returncode'])
            self.assertIn('started', (evidence/'stdout.txt').read_text())
            self.assertEqual((evidence/'log.txt').read_text(), 'engine started')
            self.assertTrue((evidence/'screenshots/partial.png').exists())

    def test_failed_process_retains_stderr_and_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); evidence=root/'reports'
            result=run_native_tests([sys.executable, '-c', 'import sys; print("native failure", file=sys.stderr); sys.exit(7)'],
                                    cwd=root, evidence=evidence, timeout=5)
            self.assertEqual(result.returncode, 7)
            self.assertEqual(json.loads((evidence/'process.json').read_text())['returncode'], 7)
            self.assertIn('native failure', (evidence/'stderr.txt').read_text())


class NativeAcceptanceTests(unittest.TestCase):
    source = 'testcase route_01:\n    assert eval last_ending == "true"\n'
    report = '''[rpytest] PASSED route_01 - (1.0 s)
[rpytest] Test cases : 1 | 1 passed | 0 xfailed | 0 failed | 0 xpassed | 0 skipped | 0 not run
[rpytest] Assertions : 1 | 1 passed | 0 xfailed | 0 failed | 0 xpassed |
[rpytest] Status: PASSED
'''

    def test_native_summary_requires_every_expected_case_and_assertion(self):
        result = validate_native_report(self.report, self.source)
        self.assertEqual((result['cases'], result['assertions']), (1, 1))
        for report in [self.report.replace('1 | 1 passed', '0 | 0 passed'),
                       self.report.replace('0 skipped', '1 skipped'),
                       self.report.replace('0 not run', '1 not run'),
                       self.report.replace('PASSED route_01', 'PASSED another_case'),
                       self.report.replace('Status: PASSED', 'Status: FAILED'), '']:
            with self.subTest(report=report), self.assertRaises(ValueError):
                validate_native_report(report, self.source)

    def test_missing_screenshot_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, 'Missing UI evidence: late-load'):
                validate_screenshots(Path(temp), ['late-load'])

    def test_present_but_truncated_screenshot_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            file = root / 'late-load.png'
            Image.new('RGB', (128, 128), '#112233').save(file)
            validate_screenshots(root, ['late-load'])
            data = file.read_bytes()
            file.write_bytes(data[:len(data)//2])
            with self.assertRaisesRegex(ValueError, 'Undecodable UI evidence: late-load'):
                validate_screenshots(root, ['late-load'])

    def test_native_evidence_rejects_720p_or_wrong_scaled_window(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            Image.new('RGB', (1920, 1080)).save(root / 'main-menu.png')
            Image.new('RGB', (1280, 720)).save(root / 'scaled-settings.png')
            validate_screenshots(root, ['main-menu', 'scaled-settings'], native_1080=True)
            Image.new('RGB', (1280, 720)).save(root / 'main-menu.png')
            with self.assertRaisesRegex(ValueError, 'Wrong physical UI size: main-menu'):
                validate_screenshots(root, ['main-menu'], native_1080=True)
            Image.new('RGB', (1920, 1080)).save(root / 'scaled-settings.png')
            with self.assertRaisesRegex(ValueError, 'Wrong physical UI size: scaled-settings'):
                validate_screenshots(root, ['scaled-settings'], native_1080=True)

    def test_incomplete_native_report_returns_nonzero_from_cli(self):
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            report = Path(temp) / 'source-tests.txt'
            report.write_text('[rpytest] Status: PASSED\n')
            result = subprocess.run([sys.executable, '-m', 'tools.build.verify_package', '--report', str(report)],
                                    cwd=project, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('summary is missing or incomplete', result.stderr)
