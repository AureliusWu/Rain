import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from tools.release_gate import validate_approval, validate_machine, validate_zip


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        sha = "a" * 40
        suite = {"cases": 31, "assertions": 359, "failed": 0, "xfailed": 0, "xpassed": 0, "skipped": 0, "not_run": 0,
                 "process": {"returncode": 0, "timed_out": False}}
        self.machine = {"status": "technical_and_visual_passed_with_human_limits", "version": "1.0.0",
                        "candidate_commit": sha, "run_id": 123, "lint": "passed", "python_tests": {"passed": 91},
                        "unresolved_machine_issues": [],
                        "suites": {k: copy.deepcopy(suite) for k in ("source", "standalone", "fresh_process")},
                        "artifacts": [{"name": f"windows-{sha}", "id": 456}],
                        "package": {"file": "BeforeTheRainStops-1.0.0-win.zip", "sha256": "b" * 64,
                                    "size_in_bytes": 999, "crc": "passed", "test_scripts_in_original_zip": False}}
        self.human = {"schema_version": 1, "status": "approved", "version": "1.0.0", "candidate_commit": sha,
                      "package_sha256": "b" * 64, "reviewer": "test fixture", "reviewed_at": "2026-10-06",
                      "unresolved_issues": [],
                      **{k: {"status": "passed", "evidence": "fixture evidence"} for k in
                         ("ordinary_windows", "display_dpi", "listening", "creative_and_freeze")},
                      "reading_time": {"status": "passed", "evidence": "fixture timing", "normal_minutes": 35, "true_minutes": 40}}

    def test_complete_record_selects_reviewed_commit_and_artifact(self):
        selection = validate_approval(self.machine, self.human, "1.0.0")
        self.assertEqual(selection["candidate"], self.machine["candidate_commit"])
        self.assertEqual(selection["artifact_id"], 456)

    def publication_fixture(self):
        from tools.audio_process.qwen_voice import MODEL_ID, REVISION, SPEAKER
        human = copy.deepcopy(self.human)
        human.update(status='pending',reviewer='',reviewed_at='')
        groups = ['ordinary_windows','display_dpi','listening','creative_and_freeze','reading_time']
        for group in groups: human[group]={'status':'pending','evidence':''}
        human['reading_time'].update(normal_minutes=None,true_minutes=None)
        voice = {'status':'signals_and_asr_passed','unresolved_machine_issues':[],'human_listening':False,
                 'producer_commit':'e'*40,'provider':{'model_id':MODEL_ID,'revision':REVISION,'speaker':SPEAKER},
                 'recordings':[{'voice_id':f'voice_{i}',
                     'asr':{'passed':True,'polarity_counts_match':True,'cer':0.0},
                     'audio':{'sample_rate':24000,'channels':1,'frames':24000,'peak':.7,'rms_dbfs':-22}}
                     for i in range(17)]}
        authorization={'schema_version':1,'status':'authorized_by_user','version':'1.0.0',
                       'candidate_commit':'a'*40,'package_sha256':'b'*64,
                       'instruction':'完成后发布正式版','condition':'voice_upgrade_completed',
                       'requested_at':'2026-10-06','pending_human_checks':groups,
                       'voice_generation_commit':'e'*40,'voice_generation_sha256':'f'*64}
        machine={**self.machine,'voice_upgrade':{'generation_sha256':'f'*64}}
        return machine,human,authorization,voice

    def test_user_requested_publication_preserves_pending_human_records(self):
        machine,human,authorization,voice=self.publication_fixture()
        original=copy.deepcopy(human)
        selected=validate_approval(machine,human,'1.0.0',authorization,voice)
        self.assertEqual(selected['approval_mode'],'user_requested_after_voice_upgrade')
        self.assertEqual(human,original)
        self.assertEqual(human['listening']['status'],'pending')

    def test_publication_cannot_authorize_other_bytes_or_unstated_instruction(self):
        machine,human,authorization,voice=self.publication_fixture()
        for key,value in [('candidate_commit','c'*40),('package_sha256','d'*64),('version','1.0.1'),
                          ('instruction','继续'),('condition','none'),('requested_at','')]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_approval(machine,human,'1.0.0',{**authorization,key:value},voice)

    def test_publication_must_disclose_pending_checks_and_never_claim_fake_listening(self):
        machine,human,authorization,voice=self.publication_fixture()
        for changes in ({'pending_human_checks':[]},{'voice_generation_sha256':'0'*64}):
            with self.assertRaises(ValueError): validate_approval(machine,human,'1.0.0',{**authorization,**changes},voice)
        human['listening']['evidence']='unperformed listening claim'
        with self.assertRaises(ValueError): validate_approval(machine,human,'1.0.0',authorization,voice)

    def test_publication_still_requires_complete_voice_and_machine_pass(self):
        machine,human,authorization,voice=self.publication_fixture()
        for changes in ({'status':'asr_review_required'},{'recordings':voice['recordings'][:-1]},
                        {'human_listening':True},{'unresolved_machine_issues':['bad line']}):
            with self.assertRaises(ValueError): validate_approval(machine,human,'1.0.0',authorization,{**voice,**changes})
        machine['suites']['standalone']['failed']=1
        with self.assertRaises(ValueError): validate_approval(machine,human,'1.0.0',authorization,voice)

    def test_publication_rejects_failed_transcription_or_speech_signals(self):
        machine,human,authorization,voice=self.publication_fixture()
        for group,key,value in [('asr','cer',.3),('asr','polarity_counts_match',False),
                                ('audio','peak',1.0),('audio','rms_dbfs',-60)]:
            changed=copy.deepcopy(voice);changed['recordings'][0][group][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_approval(machine,human,'1.0.0',authorization,changed)

    def test_voice_publication_requires_packaged_qwen_license(self):
        with tempfile.TemporaryDirectory() as temp:
            path,selection=self.fixture_zip(Path(temp))
            with self.assertRaisesRegex(ValueError,'Qwen license'):
                validate_zip(path,{**selection,'qwen_license_required':'true'})

    def test_pending_human_groups_cannot_be_replaced_by_machine_pass(self):
        for group in ("ordinary_windows", "display_dpi", "listening", "creative_and_freeze", "reading_time"):
            with self.subTest(group=group):
                human = copy.deepcopy(self.human)
                human[group]["status"] = "pending"
                with self.assertRaises(ValueError):
                    validate_approval(self.machine, human, "1.0.0")

    def test_approval_of_another_commit_or_zip_is_rejected(self):
        for key, value in (("candidate_commit", "c" * 40), ("package_sha256", "d" * 64), ("version", "1.0.1")):
            human = copy.deepcopy(self.human); human[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_approval(self.machine, human, "1.0.0")

    def test_bad_machine_process_or_incomplete_tests_are_rejected(self):
        for key, value in (("failed", 1), ("skipped", 1), ("not_run", 1), ("cases", 0)):
            machine = copy.deepcopy(self.machine); machine["suites"]["standalone"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_approval(machine, self.human, "1.0.0")
        self.machine["suites"]["fresh_process"]["process"]["timed_out"] = True
        with self.assertRaises(ValueError):
            validate_approval(self.machine, self.human, "1.0.0")

    def test_each_error_count_must_be_present_integer_zero(self):
        for scope in ("source", "standalone", "fresh_process"):
            for field in ("failed", "xfailed", "xpassed", "skipped", "not_run"):
                for value in (None, False, 0.0, -1, 1):
                    machine = copy.deepcopy(self.machine)
                    if value is None:
                        del machine["suites"][scope][field]
                    else:
                        machine["suites"][scope][field] = value
                    with self.subTest(scope=scope, field=field, value=value), self.assertRaises(ValueError):
                        validate_approval(machine, self.human, "1.0.0")

    def test_boolean_and_invalid_counts_ids_or_exit_codes_are_rejected(self):
        paths = [("suites", "standalone", "cases"), ("suites", "standalone", "assertions"),
                 ("python_tests", "passed"), ("run_id",), ("artifacts", 0, "id")]
        for path in paths:
            for value in (True, False, 0, -1, 31.0, "31"):
                machine = copy.deepcopy(self.machine)
                target = machine
                for part in path[:-1]:
                    target = target[part]
                target[path[-1]] = value
                with self.subTest(path=path, value=value), self.assertRaises(ValueError):
                    validate_machine(machine, "1.0.0")
        for value in (False, 0.0, "0", None, 1):
            machine = copy.deepcopy(self.machine)
            machine["suites"]["fresh_process"]["process"]["returncode"] = value
            with self.subTest(exit=value), self.assertRaises(ValueError):
                validate_machine(machine, "1.0.0")

    def test_unresolved_or_missing_machine_issues_block_publication(self):
        for value in (None, ["fixture unresolved issue"], ""):
            machine = copy.deepcopy(self.machine)
            if value is None:
                del machine["unresolved_machine_issues"]
            else:
                machine["unresolved_machine_issues"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_approval(machine, self.human, "1.0.0")

    def test_source_and_exe_counts_must_agree(self):
        for field in ("cases", "assertions"):
            machine = copy.deepcopy(self.machine)
            machine["suites"]["standalone"][field] -= 1
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "Source/EXE"):
                validate_machine(machine, "1.0.0")

    def test_malformed_records_are_blocked_with_validation_errors(self):
        for machine in (None, [], {**self.machine, "suites": None},
                        {**self.machine, "artifacts": [None]}, {**self.machine, "package": None}):
            with self.subTest(machine=machine), self.assertRaises(ValueError):
                validate_machine(machine, "1.0.0")
        for field in ("reviewer", "reviewed_at", "ordinary_windows", "reading_time"):
            human = copy.deepcopy(self.human)
            human[field] = None
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_approval(self.machine, human, "1.0.0")
        for field in ("ordinary_windows", "reading_time"):
            human = copy.deepcopy(self.human)
            human[field]["evidence"] = None
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_approval(self.machine, human, "1.0.0")

    def test_cli_blocks_malformed_record_without_outputs_or_traceback(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            machine, human, output = root / "machine.json", root / "human.json", root / "outputs.txt"
            machine.write_text("null", encoding="utf-8")
            human.write_text(json.dumps(self.human), encoding="utf-8")
            result = subprocess.run([sys.executable, "-m", "tools.release_gate", "--version", "1.0.0",
                                     "--machine", str(machine), "--human", str(human), "--github-output", str(output)],
                                    cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Release blocked: Machine acceptance must be a JSON object", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(output.exists())

    def test_missing_evidence_and_unresolved_issues_block_publication(self):
        self.human["listening"]["evidence"] = " "
        with self.assertRaises(ValueError):
            validate_approval(self.machine, self.human, "1.0.0")
        self.human["listening"]["evidence"] = "fixture"
        self.human["unresolved_issues"] = ["unfixed issue"]
        with self.assertRaises(ValueError):
            validate_approval(self.machine, self.human, "1.0.0")

    def test_estimate_nan_boolean_or_out_of_scope_timing_is_rejected(self):
        for value in (None, True, "35", float("nan"), 29.9, 60.1):
            human = copy.deepcopy(self.human); human["reading_time"]["normal_minutes"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_approval(self.machine, human, "1.0.0")

    def fixture_zip(self, directory, extra=None):
        path = directory / "BeforeTheRainStops-1.0.0-win.zip"
        root = "BeforeTheRainStops-1.0.0-win/"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(root + "BeforeTheRainStops.exe", b"test fixture, not a game")
            archive.writestr(root + "game/cache/build_info.json", json.dumps({"version": "1.0.0"}))
            for name in ("PLAYER_README.txt", "CREDITS.md", "LICENSE", "licenses/RENPY.txt",
                         "licenses/SourceHanSans-OFL.txt", "licenses/Kokoro-model-Apache-2.0.txt"):
                archive.writestr(root + name, "fixture")
            if extra:
                archive.writestr(root + extra, "unwanted")
        selection = validate_approval(self.machine, self.human, "1.0.0")
        selection.update(size=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        return path, selection

    def test_reviewed_bytes_accept_but_same_size_tampering_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            path, selection = self.fixture_zip(Path(temp))
            validate_zip(path, selection)
            data = bytearray(path.read_bytes()); data[45] ^= 1; path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "reviewed bytes"):
                validate_zip(path, selection)

    def test_injected_tests_models_and_unsafe_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            for extra in ("game/testcases.rpy", "game/saves/1.save", "assets_source/private.png", "game/model.onnx", "../outside"):
                path, selection = self.fixture_zip(Path(temp), extra)
                with self.subTest(extra=extra), self.assertRaises(ValueError):
                    validate_zip(path, selection)


if __name__ == "__main__":
    unittest.main()
