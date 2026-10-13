import copy
import unittest
from tools.audio_process.voice_request import prepare_request


class VoiceRequestTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(asset_id='voice_001', character='proposed_role', text='先看记录。', speaker='Serena',
                        instruct='普通话，自然口语。', seed=120001, line_ids=['line_a','line_b'])
        self.provider = dict(model_id='Qwen/example', revision='pinned_revision', dtype='float32',
                             processing='r128_-20', wrapper='fixed_version', speaker_bank={'Serena':3066,'Dylan':2878})
        self.source = {'line_a':'她说：先看记录。', 'line_b':'先看记录。雨又下了。'}

    def call(self, row=None, provider=None, source=None):
        return prepare_request(row or self.row, provider or self.provider, source or self.source)

    def test_multiple_bindings_share_one_recording_and_sources_are_not_mutated(self):
        before=copy.deepcopy((self.row,self.provider,self.source))
        result=self.call()
        self.assertEqual(len(result['request']['recording']['line_ids']),2)
        self.assertEqual((self.row,self.provider,self.source),before)
        result['request']['recording']['line_ids'].append('line_c')
        self.assertEqual(self.row['line_ids'],['line_a','line_b'])

    def test_fingerprint_is_stable_across_dict_key_order(self):
        self.assertEqual(self.call()['sha256'],self.call(dict(reversed(list(self.row.items()))))['sha256'])

    def test_every_recording_field_changes_cache_identity(self):
        original=self.call()['sha256']
        changes=dict(asset_id='voice_002',character='other_role',speaker='Dylan',instruct='低声。',seed=120002,line_ids=['line_a'])
        for key,value in changes.items():
            with self.subTest(key=key):
                self.assertNotEqual(self.call({**self.row,key:value})['sha256'],original)
        source={k:'请先看原记录。' for k in self.source}
        self.assertNotEqual(self.call({**self.row,'text':'先看原记录。'},source=source)['sha256'],original)

    def test_provider_and_new_sampler_fields_change_cache_identity(self):
        original=self.call()['sha256']
        for key,value in dict(dtype='bfloat16',revision='another_revision',processing='new_processing',temperature=.8).items():
            with self.subTest(key=key):
                self.assertNotEqual(self.call(provider={**self.provider,key:value})['sha256'],original)

    def test_invalid_seed_and_unsafe_ids_are_rejected(self):
        for value in [True,-1,2**32,'1',1.5]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                self.call({**self.row,'seed':value})
        for value in ['../voice','/voice','', '__proto__','name/voice']:
            with self.subTest(value=value),self.assertRaises(ValueError):
                self.call({**self.row,'asset_id':value})

    def test_missing_or_duplicate_text_bindings_are_rejected(self):
        for ids in [[],['line_a','line_a'],['missing'],[5]]:
            with self.subTest(ids=ids),self.assertRaises(ValueError):
                self.call({**self.row,'line_ids':ids})
        with self.assertRaises(ValueError):
            self.call(source={'line_a':'另一句话。','line_b':'先看记录。'})

    def test_unknown_speaker_and_invalid_provider_are_rejected(self):
        with self.assertRaises(ValueError):
            self.call({**self.row,'speaker':'unknown'})
        for field in ['model_id','revision','dtype','processing','wrapper','speaker_bank']:
            provider=copy.deepcopy(self.provider);del provider[field]
            with self.subTest(field=field),self.assertRaises(ValueError):
                self.call(provider=provider)


if __name__ == '__main__':
    unittest.main()
