"""Verify the whole recording bundle before replacing any active asset."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
from tools.asset_paths import project_file, sha256
from tools.audio_process.generate_qwen import validate_plan, require
from tools.audio_process.metadata import audio_metadata, metadata_matches
from tools.audio_process.qwen_voice import MODEL_NAME, PROVIDER_FILE, request_fingerprint, provenance_matches
from tools.prompt_registry import prompt_by_file
from tools.story_model import ROOT


def prepare(bundle,root=ROOT):
    request = root/'prompts/voice/qwen_heroine_v1.json'
    plan = json.loads(request.read_text(encoding='utf-8'))
    validate_plan(plan,root)
    report = json.loads((bundle/'generation.json').read_text(encoding='utf-8'))
    require(report.get('status') == 'signals_and_asr_passed' and report.get('unresolved_machine_issues') == []
            and report.get('human_listening') is False,'Generation is not verified')
    require(report.get('request_sha256') == sha256(request.read_bytes())
            and report.get('source_story_sha256') == plan['source_story_sha256']
            and report.get('source_voice_manifest_sha256') == plan['source_voice_manifest_sha256']
            == sha256((root/'game/data/voice_manifest.json').read_bytes()),'Stale generation bundle')
    provider,records = report['provider'],report['recordings']
    require(len(records) == 17 and len({r['voice_id'] for r in records}) == 17,'Incomplete recording set')
    by_record = {r['voice_id']:r for r in records}
    prompt = prompt_by_file(root,'prompts/voice/qwen_heroine_v1.json')
    original = json.loads((root/'game/data/voice_manifest.json').read_text(encoding='utf-8'))
    manifest = json.loads((root/'game/data/asset_manifest.json').read_text(encoding='utf-8'))
    voices,outputs,archive_assets = [],{},[]
    by_asset = {a['id']:a for a in manifest['assets']}
    for old in original['voices']:
        record = by_record[old['voice_id']]
        direction = next(r for r in plan['lines'] if r['voice_id'] == old['voice_id'])
        require(all(record[k] == direction[k] for k in ('voice_id','line_id','text','instruct','seed')),'Request binding mismatch')
        asr = record['asr']
        require(asr.get('passed') is True and asr.get('polarity_counts_match') is True
                and asr.get('critical_terms_match') is True
                and type(asr.get('cer')) in (int,float) and 0 <= asr['cer'] <= .2,'Failed independent transcription')
        verified = {}
        for kind in ('wav','ogg'):
            file = (bundle/record['files'][kind]['path']).resolve()
            require(file.is_relative_to(bundle.resolve()) and file.suffix == '.'+kind,'Unsafe bundle path')
            data = file.read_bytes()
            require(sha256(data) == record['files'][kind]['sha256'],'Bundle hash mismatch')
            metadata = audio_metadata(file)
            require(metadata_matches(metadata,record['source_audio' if kind=='wav' else 'audio']),'Audio metadata mismatch')
            require(metadata['sample_rate'] == 24000 and metadata['channels'] == 1
                    and metadata['peak'] < .99 and -30 <= metadata['rms_dbfs'] <= -18,'Invalid speech signal')
            verified[kind] = data
        require(record['source_audio']['frames'] == record['audio']['frames'],'WAV/OGG frame mismatch')
        asset = by_asset[old['voice_id']]
        old_game = project_file(root,'game/'+old['file'],'game')
        require(sha256(old_game.read_bytes()) == asset['sha256'],'Original speech changed')
        archive = 'assets_source/audio/voice/kokoro_archive/'+old['voice_id']+'.ogg'
        source = 'assets_source/audio/voice/'+old['voice_id']+'_qwen_v2.wav'
        require(not (root/archive).exists() and not (root/source).exists(),'Adoption already started; inspect before retry')
        outputs[archive] = old_game.read_bytes()
        archive_assets.append({**copy.deepcopy(asset),'archive_file':archive})
        outputs[source],outputs['game/'+old['file']] = verified['wav'],verified['ogg']
        voice = {k:old[k] for k in ('voice_id','line_id','character','text','file','text_sha256')}
        voice.update({'engine':'qwen3_tts','model':MODEL_NAME,'voice':'Serena','language':'Chinese',
                      'version':2,'prompt':prompt['file'],'prompt_id':prompt['id'],'source_file':source,
                      'instruct':record['instruct'],'seed':record['seed'],'sample_rate':24000,
                      'duration_seconds':record['duration_seconds'],'model_revision':provider['revision'],
                      'max_new_tokens':384,'emotion_control':'model natural-language instruction',
                      **{k:provider[k] for k in ('model_sha256','voice_bank_sha256','config_sha256',
                                                'checkpoint_sha256','wrapper','torch_version','processing')}})
        require(provenance_matches(voice,provider),'Wrong provider provenance')
        voice['generation_sha256'] = request_fingerprint(voice,prompt['sha256'])
        voices.append(voice)
        asset.update({'source':'Qwen3-TTS 1.7B CustomVoice; Serena; synthesized project dialogue',
                      'source_file':source,'source_sha256':record['files']['wav']['sha256'],
                      'sha256':record['files']['ogg']['sha256'],'version':2,'approved':True,
                      'status':'production_user_requested_voice_upgrade',
                      'approval_scope':'Engineering integration; user requested publication; human listening pending',
                      'license':'Qwen model and wrapper Apache-2.0; synthesized project dialogue; see CREDITS.md',
                      'prompt':prompt['file'],'prompt_id':prompt['id'],'prompt_sha256':prompt['sha256'],
                      'audio':record['audio'],'source_audio':record['source_audio']})
    def put(path,data): outputs[path] = (json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    put('game/data/voice_manifest.json',{**original,'voices':voices})
    put('game/data/asset_manifest.json',manifest)
    put(PROVIDER_FILE,provider)
    put('docs/review/VOICE_KOKORO_ARCHIVE.json',{'status':'historical_superseded_by_qwen',
        'voice_manifest':original,'assets':archive_assets,'human_listening_claimed':False})
    put('docs/evidence/voice-qwen-generation.json',report)
    return outputs


def adopt(bundle,root=ROOT):
    for relative,content in prepare(bundle,root).items():
        target = root/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(content)
    for relative in ('game/options.rpy','PLAYER_README.txt'):
        file = root/relative
        file.write_text(file.read_text(encoding='utf-8').replace('Kokoro-82M v1.1-zh / zf_001','Qwen3-TTS 1.7B / Serena'),encoding='utf-8')
    credits = root/'CREDITS.md'
    text = credits.read_text(encoding='utf-8').replace('- 关键语音：Kokoro','- 历史候选关键语音：Kokoro')
    text += ('\n- v1.0 语音升级：17 句关键台词全部改用免费开源 Qwen3-TTS-12Hz-1.7B-CustomVoice / Serena / Chinese。'
             '官方预设音色，无现实人物参考或克隆。模型和 qwen-tts 0.1.1 代码采用 Apache-2.0，'
             '见 licenses/Qwen3-TTS-Apache-2.0.txt；'
             'https://github.com/QwenLM/Qwen3-TTS ，https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice 。'
             '固定模型提交、逐句指令、源 WAV、响度处理和独立 ASR 记录保留；旧版录音归档，'
             '玩家包不含模型或生成依赖。自动文字和信号检查不代表真人试听。\n')
    credits.write_text(text,encoding='utf-8')
    for module in ('tools.compile_story','tools.compile_tests'):
        subprocess.run([sys.executable,'-m',module],cwd=root,check=True)
    print('Adopted 17 Qwen recordings; archived all previous OGG files and preserved dialogue IDs.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    adopt(parser.parse_args().bundle)


if __name__ == '__main__': main()
