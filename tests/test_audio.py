import copy
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import soundfile as sf
from tools.asset_paths import sha256
from tools.audio_process.metadata import audio_metadata
from tools.audio_process.generate_voice import cached_voice_is_current, request_fingerprint, prepare_samples, PROCESSING
from tools.audio_process.render_soundtrack import synthesize
from tools.audio_validator import validate_audio
from tools.story_model import ROOT, load_story, scene_lines


class AudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / 'assets_source/audio/cue.wav'
        self.output = self.root / 'game/audio/sfx/cue.ogg'
        self.source.parent.mkdir(parents=True)
        self.output.parent.mkdir(parents=True)
        samples = .1 * np.sin(2 * np.pi * 440 * np.arange(12000) / 24000)
        sf.write(self.source, samples, 24000, subtype='PCM_16')
        sf.write(self.output, samples, 24000, format='OGG', subtype='VORBIS')
        self.asset = dict(id='cue', type='audio', audio_role='sfx', file='audio/sfx/cue.ogg',
                          source_file='assets_source/audio/cue.wav', version=1,
                          sha256=sha256(self.output.read_bytes()), source_sha256=sha256(self.source.read_bytes()),
                          audio=audio_metadata(self.output), source_audio=audio_metadata(self.source))
        self.story = {'nodes': [{'id': 's01', 'lines': [{'id': 's01_l001', 'speaker': 'n', 'text': '纸袋响了。', 'sound': 'cue'}]}]}

    def check(self, assets=None, story=None):
        return validate_audio(self.root, assets or [self.asset], story or self.story)[0]

    def cached(self):
        voice = dict(voice_id='cue', line_id='s01_l001', text='你好。', character='h',
                     model='Kokoro-82M v1.1-zh ONNX int8', voice='zf_001', speed=.95,
                     version=1, processing=PROCESSING, prompt_id='voice_heroine_v2',
                     file=self.asset['file'], source_file=self.asset['source_file'])
        voice['text_sha256'] = sha256(voice['text'].encode())
        voice['generation_sha256'] = request_fingerprint(voice, 'reviewed-prompt-hash')
        asset = {**self.asset, 'type': 'voice'}
        return voice, asset

    def test_valid_wave_and_vorbis_are_fully_decoded(self):
        self.assertEqual(self.check(), [])
        self.assertEqual(self.asset['audio']['frames'], 12000)

    def test_current_project_audio_and_selected_voice_bindings(self):
        errors, measured = validate_audio()
        self.assertEqual(errors, [])
        self.assertEqual(len(measured), 24)
        voices = json.loads((ROOT / 'game/data/voice_manifest.json').read_text())['voices']
        self.assertEqual(len(voices), 17)
        bound = {line['voice'] for n in load_story()['nodes'] for line in scene_lines(n) if line.get('voice')}
        self.assertEqual(bound, {v['voice_id'] for v in voices})

    def test_ogg_header_with_matching_checksum_does_not_prove_audio(self):
        self.output.write_bytes(b'OggS' + b'\0' * 200)
        self.asset['sha256'] = sha256(self.output.read_bytes())
        self.assertTrue(any('Undecodable audio' in error for error in self.check()))

    def test_truncated_real_vorbis_is_rejected_even_with_updated_checksum(self):
        encoded = self.output.read_bytes()
        self.output.write_bytes(encoded[:len(encoded) // 2])
        self.asset['sha256'] = sha256(self.output.read_bytes())
        self.assertTrue(any('Undecodable audio' in error for error in self.check()))

    def test_silent_audio_is_rejected(self):
        sf.write(self.source, np.zeros(12000), 24000, subtype='PCM_16')
        self.assertTrue(any('Silent audio' in error for error in self.check()))

    def test_clipping_is_rejected(self):
        sf.write(self.source, np.full(12000, .9999), 24000, subtype='PCM_16')
        self.assertTrue(any('peak headroom' in error for error in self.check()))

    def test_non_finite_audio_is_rejected(self):
        samples = np.ones(12000) * .1
        samples[100] = np.nan
        sf.write(self.source, samples, 24000, subtype='FLOAT')
        self.assertTrue(any('Non-finite' in error for error in self.check()))

    def test_source_and_encoded_lengths_must_match(self):
        sf.write(self.source, .1 * np.sin(np.arange(14000)), 24000, subtype='PCM_16')
        self.asset['source_audio'] = audio_metadata(self.source)
        self.assertTrue(any('length mismatch' in error for error in self.check()))

    def test_missing_sound_and_wrong_music_role_are_rejected(self):
        story = copy.deepcopy(self.story)
        story['nodes'][0]['lines'][0]['sound'] = 'missing'
        story['nodes'][0]['bgm'] = 'cue'
        errors = self.check(story=story)
        self.assertTrue(any('missing/wrong sound' in error for error in errors))
        self.assertTrue(any('wrong audio role for bgm' in error for error in errors))

    def test_invalid_stop_cue_and_changed_metadata_are_rejected(self):
        self.story['nodes'][0]['lines'][0]['stop_ambient'] = 'yes'
        self.asset['audio']['channels'] = 2
        errors = self.check()
        self.assertTrue(any('must be boolean' in error for error in errors))
        self.assertTrue(any('metadata mismatch' in error for error in errors))

    def test_unchanged_voice_request_and_files_can_be_reused(self):
        voice, asset = self.cached()
        self.assertTrue(cached_voice_is_current(self.root, voice, asset, 'reviewed-prompt-hash'))

    def test_voice_cache_rejects_changed_speed_text_prompt_and_line(self):
        voice, asset = self.cached()
        for field, value in [('speed', 1), ('text', '再见。'), ('line_id', 'another_line')]:
            changed = {**voice, field: value}
            self.assertFalse(cached_voice_is_current(self.root, changed, asset, 'reviewed-prompt-hash'))
        self.assertFalse(cached_voice_is_current(self.root, voice, asset, 'changed-prompt-hash'))

    def test_voice_cache_rejects_changed_or_missing_source(self):
        voice, asset = self.cached()
        self.source.write_bytes(b'broken')
        self.assertFalse(cached_voice_is_current(self.root, voice, asset, 'reviewed-prompt-hash'))
        self.source.unlink()
        self.assertFalse(cached_voice_is_current(self.root, voice, asset, 'reviewed-prompt-hash'))

    def test_voice_preparation_limits_peaks_and_fades_edges(self):
        samples = np.ones(24000) * 1.4
        result = prepare_samples(samples, 24000)
        self.assertLessEqual(float(np.max(np.abs(result))), .89)
        self.assertEqual((result[0], result[-1]), (0, 0))
        self.assertEqual(samples[0], 1.4)

    def test_voice_preparation_rejects_empty_and_non_finite(self):
        for samples in [np.zeros(24000), np.array([]), np.full(24000, np.nan)]:
            with self.assertRaises(ValueError):
                prepare_samples(samples, 24000)

    def test_procedural_cues_are_repeatable_and_music_has_loop_headroom(self):
        recipes = json.loads((ROOT / 'prompts/audio/soundtrack_v1.json').read_text())['assets']
        for recipe in recipes:
            a, b = synthesize(recipe), synthesize(recipe)
            np.testing.assert_array_equal(a, b)
            self.assertEqual(len(a), round(recipe['duration_seconds'] * 24000))
            self.assertLess(float(np.max(np.abs(a))), .9)
            if recipe['kind'] == 'music':
                self.assertLess(abs(float(a[-1] - a[0])), .01)


if __name__ == '__main__':
    unittest.main()
