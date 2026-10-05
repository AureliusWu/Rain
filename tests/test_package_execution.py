import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tools.build.verify_package import run_native_tests, collect_runtime_evidence


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
