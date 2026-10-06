"""Pinned voice provenance without importing a speech runtime."""
import json
import re
from tools.asset_paths import sha256

MODEL_ID = 'Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice'
REVISION = '0c0e3051f131929182e2c023b9537f8b1c68adfe'
MODEL_NAME = 'Qwen3-TTS-12Hz-1.7B-CustomVoice'
SPEAKER = 'Serena'
PROVIDER_FILE = 'game/data/voice_provider_qwen.json'
PROCESSING = 'ebu_r128_minus20_lufs_truepeak_minus2_db_24k_pcm16_v1'


def request_fingerprint(voice, prompt_hash):
    keys = ['line_id','text','character','model','voice','language','version','instruct','seed',
            'processing','prompt_id','model_sha256','voice_bank_sha256','config_sha256',
            'checkpoint_sha256','model_revision','wrapper','torch_version','max_new_tokens']
    request = {key:voice.get(key) for key in keys}
    request['prompt_sha256'] = prompt_hash
    return sha256(json.dumps(request,ensure_ascii=False,sort_keys=True).encode('utf-8'))


def provenance_matches(voice, provider):
    return (isinstance(provider,dict) and provider.get('model_id') == MODEL_ID
            and provider.get('revision') == REVISION and voice.get('model') == MODEL_NAME
            and voice.get('voice') == SPEAKER and voice.get('language') == 'Chinese'
            and voice.get('model_revision') == REVISION and voice.get('wrapper') == 'qwen-tts-0.1.1'
            and voice.get('processing') == PROCESSING
            and all(voice.get(k) == provider.get(k) and isinstance(voice.get(k),str)
                    and re.fullmatch('[0-9a-f]{64}',voice[k]) for k in
                    ('model_sha256','voice_bank_sha256','config_sha256','checkpoint_sha256')))
