"""Reject misbound speech requests and unverifiable recording adoption."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.story_model import ROOT
from tools.audio_process.generate_qwen import validate_plan, character_error_rate, normalize_text
from tools.audio_process.adopt_qwen import prepare
from tools.audio_process.qwen_voice import MODEL_ID, MODEL_NAME, REVISION, PROCESSING, provenance_matches, request_fingerprint


class QwenVoiceTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT/'prompts/voice/qwen_heroine_v1.json').read_text(encoding='utf-8'))

    def test_request_matches_all_story_lines(self):
        validate_plan(self.plan)

    def test_wrong_dialogue_or_voice_is_rejected(self):
        for field,value in [('text','替换正文'),('line_id','s01_arrival_l001'),('voice_id','../unsafe')]:
            with self.subTest(field=field):
                plan=copy.deepcopy(self.plan);plan['lines'][0][field]=value
                with self.assertRaises(ValueError): validate_plan(plan)

    def test_missing_or_duplicate_line_is_rejected(self):
        for lines in (self.plan['lines'][:-1], [self.plan['lines'][0]]*17):
            plan={**self.plan,'lines':lines}
            with self.assertRaises(ValueError): validate_plan(plan)

    def test_stale_story_or_model_is_rejected(self):
        for field in ('revision','source_story_sha256'):
            with self.assertRaises(ValueError): validate_plan({**self.plan,field:'0'*64})

    def test_transcription_error_metric_detects_negation_change(self):
        expected=normalize_text('你没说的部分，我不会当作已经知道。')
        actual=normalize_text('你说的部分，我会当作已经知道。')
        self.assertGreater(character_error_rate(expected,actual),0)
        self.assertNotEqual(expected.count('不'),actual.count('不'))
        self.assertEqual(character_error_rate('中文','中文'),0)

    def test_request_fingerprint_changes_with_direction_and_model(self):
        voice={'instruct':'温柔','model_revision':REVISION,'voice':'Serena'}
        original=request_fingerprint(voice,'a'*64)
        for key,value in [('instruct','坚定'),('model_revision','b'*40),('text','新台词')]:
            self.assertNotEqual(original,request_fingerprint({**voice,key:value},'a'*64))

    def test_foreign_provider_cannot_approve_recording(self):
        hashes={k:'a'*64 for k in ('model_sha256','voice_bank_sha256','config_sha256','checkpoint_sha256')}
        provider={'model_id':MODEL_ID,'revision':REVISION,**hashes}
        voice={'model':MODEL_NAME,'model_revision':REVISION,'voice':'Serena','language':'Chinese',
               'wrapper':'qwen-tts-0.1.1','processing':PROCESSING,**hashes}
        self.assertTrue(provenance_matches(voice,provider))
        self.assertFalse(provenance_matches(voice,{**provider,'revision':'b'*40}))
        self.assertFalse(provenance_matches({**voice,'config_sha256':'b'*64},provider))

    def test_failed_bundle_is_rejected_before_any_asset_write(self):
        original=(ROOT/'game/data/voice_manifest.json').read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            bundle=Path(directory)
            (bundle/'generation.json').write_text(json.dumps({'status':'asr_review_required'}))
            with self.assertRaises(ValueError): prepare(bundle)
        self.assertEqual((ROOT/'game/data/voice_manifest.json').read_bytes(),original)


if __name__ == '__main__':
    unittest.main()
