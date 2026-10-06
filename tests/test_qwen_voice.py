"""Reject misbound speech requests and unverifiable recording adoption."""
import copy
import json
import shutil
import tempfile
import unittest
import numpy as np
import soundfile as sf
from tools.asset_paths import sha256
from tools.audio_process.metadata import audio_metadata
from pathlib import Path
from tools.story_model import ROOT
from tools.audio_process.generate_qwen import validate_plan, character_error_rate, normalize_text, assess_transcript
from tools.audio_process.adopt_qwen import prepare
from tools.audio_process.qwen_voice import MODEL_ID, MODEL_NAME, REVISION, PROCESSING, provenance_matches, request_fingerprint


class QwenVoiceTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT/'prompts/voice/qwen_heroine_v1.json').read_text(encoding='utf-8'))
        # Exercise a new incoming request against this checkout. The production
        # request remains the immutable v1.0.0 generation receipt.
        self.plan['source_story_sha256'] = sha256((ROOT/'game/data/story.json').read_bytes())

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

    def test_short_or_semantic_word_errors_are_not_hidden_by_low_average_cer(self):
        for line_id,wrong in [('s03_honest_l005','他还不知道你写了什么，要不要看，也得让我自己决定。'),
                              ('s04_waiting_l020','举好不算消息。'),
                              ('s08_normal_l005','这张没有拍完。你回去以后，慢慢看。')]:
            row=next(r for r in self.plan['lines'] if r['line_id']==line_id)
            with self.subTest(line_id=line_id):
                self.assertFalse(assess_transcript(row,wrong,None)['passed'])
                self.assertTrue(assess_transcript(row,row['text'],None)['passed'])

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

    def verified_fixture_bundle(self,directory,request_root):
        # Synthetic sine fixture checks adoption validation only; never used as game speech.
        bundle=Path(directory)
        samples=.12*np.sin(2*np.pi*440*np.arange(24000)/24000)
        recordings=[]
        for row in self.plan['lines']:
            files={}
            for kind in ('wav','ogg'):
                file=bundle/(row['voice_id']+'.'+kind)
                sf.write(file,samples,24000,format='WAV' if kind=='wav' else 'OGG',
                         subtype='PCM_16' if kind=='wav' else 'VORBIS')
                files[kind]={'path':file.name,'sha256':sha256(file.read_bytes())}
            recordings.append({**row,'files':files,'duration_seconds':1.0,
                'source_audio':audio_metadata(bundle/files['wav']['path']),
                'audio':audio_metadata(bundle/files['ogg']['path']),
                'asr':{'passed':True,'polarity_counts_match':True,'critical_terms_match':True,'cer':0.0}})
        report={'status':'signals_and_asr_passed','unresolved_machine_issues':[],'human_listening':False,
                'request_sha256':sha256((request_root/'prompts/voice/qwen_heroine_v1.json').read_bytes()),
                'source_story_sha256':self.plan['source_story_sha256'],
                'source_voice_manifest_sha256':self.plan['source_voice_manifest_sha256'],
                'provider':{'model_id':MODEL_ID,'revision':REVISION,'wrapper':'qwen-tts-0.1.1',
                    'torch_version':'fixture','processing':PROCESSING,**{k:'a'*64 for k in
                    ('model_sha256','voice_bank_sha256','config_sha256','checkpoint_sha256')}},
                'recordings':recordings}
        (bundle/'generation.json').write_text(json.dumps(report),encoding='utf-8')
        return bundle,report

    def test_bundle_hash_and_escape_fail_without_writing_any_game_file(self):
        root=tempfile.TemporaryDirectory();self.addCleanup(root.cleanup)
        test_root=Path(root.name)
        for relative in ('game/data/story.json','prompts','game/data/voice_manifest.json','game/data/asset_manifest.json'):
            target=test_root/relative;target.parent.mkdir(parents=True,exist_ok=True)
            if (ROOT/relative).is_dir(): shutil.copytree(ROOT/relative,target)
            else: shutil.copy2(ROOT/relative,target)
        archived=json.loads((ROOT/'docs/review/VOICE_KOKORO_ARCHIVE.json').read_text(encoding='utf-8'))
        original=json.dumps(archived['voice_manifest'],ensure_ascii=False,indent=2)+'\n'
        (test_root/'game/data/voice_manifest.json').write_bytes(original.encode('utf-8'))
        self.assertEqual(sha256((test_root/'game/data/voice_manifest.json').read_bytes()),
                         self.plan['source_voice_manifest_sha256'])
        (test_root/'prompts/voice/qwen_heroine_v1.json').write_bytes(
            (json.dumps(self.plan,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
        registry_file = test_root/'prompts/registry.json'
        registry = json.loads(registry_file.read_text(encoding='utf-8'))
        for prompt in registry['prompts']:
            if prompt['file'] == 'prompts/voice/qwen_heroine_v1.json':
                prompt['sha256'] = sha256((test_root/prompt['file']).read_bytes())
        registry_file.write_text(json.dumps(registry,ensure_ascii=False),encoding='utf-8')
        with tempfile.TemporaryDirectory() as directory:
            bundle,report=self.verified_fixture_bundle(directory,test_root)
            first=bundle/report['recordings'][0]['files']['ogg']['path']
            first.write_bytes(b'OggS invalid fixture')
            with self.assertRaisesRegex(ValueError,'Bundle hash'): prepare(bundle,test_root)
            report['recordings'][0]['files']['ogg']['path']='../escaped.ogg'
            (bundle/'generation.json').write_text(json.dumps(report),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Unsafe bundle path'): prepare(bundle,test_root)


if __name__ == '__main__':
    unittest.main()
