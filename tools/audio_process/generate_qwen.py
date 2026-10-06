"""Generate pinned Serena speech, normalize loudness and independently transcribe it."""
import argparse
import gc
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import time

for key in ('ORT_DISABLE_TELEMETRY','HF_HUB_DISABLE_TELEMETRY','DO_NOT_TRACK'):
    os.environ[key] = '1'

from tools.asset_paths import ASSET_ID, sha256
from tools.audio_process.metadata import audio_metadata
from tools.audio_process.qwen_voice import MODEL_ID, REVISION, SPEAKER, PROCESSING
from tools.story_model import ROOT, load_story, scene_lines


def require(condition,message):
    if not condition:
        raise ValueError(message)


def validate_plan(plan,root=ROOT):
    require(plan.get('schema_version') == 1 and plan.get('model_id') == MODEL_ID
            and plan.get('revision') == REVISION and plan.get('speaker') == SPEAKER,'Wrong pinned voice request')
    require(sha256((root/'game/data/story.json').read_bytes()) == plan['source_story_sha256'],'Stale story request')
    lines = {line['id']:line for n in load_story(root/'game/data/story.json')['nodes'] for line in scene_lines(n)}
    voices = json.loads((root/'game/data/voice_manifest.json').read_text(encoding='utf-8'))['voices']
    current = {v['voice_id']:v for v in voices}
    require(len(plan['lines']) == len(voices) == 17,'Expected all 17 selected lines')
    ids = set()
    for row in plan['lines']:
        name = row['voice_id']
        require(isinstance(name,str) and ASSET_ID.fullmatch(name) and name not in ids,'Unsafe/duplicate voice ID')
        ids.add(name)
        line,voice = lines.get(row['line_id'],{}),current.get(name,{})
        require((line.get('speaker'),line.get('text'),line.get('voice')) == ('h',row['text'],name),'Voice/text binding changed')
        require((voice.get('line_id'),voice.get('text')) == (row['line_id'],row['text']),'Manifest text changed')
        require(isinstance(row.get('instruct'),str) and bool(row['instruct'].strip())
                and type(row.get('seed')) is int,'Missing direction or seed')
    require(ids == set(current),'Incomplete selected voices')


def normalize_text(text,converter=None):
    text = converter.convert(text) if converter else text
    return ''.join(c for c in text if c.isalnum()).lower()


def character_error_rate(expected,actual):
    previous = list(range(len(actual)+1))
    for i,a in enumerate(expected,1):
        current = [i]
        for j,b in enumerate(actual,1):
            current.append(min(current[-1]+1,previous[j]+1,previous[j-1]+(a != b)))
        previous = current
    return previous[-1]/max(1,len(expected))


def postprocess(raw,output):
    base = ['ffmpeg','-nostdin','-hide_banner','-y','-i',str(raw)]
    result = subprocess.run(base+['-af','loudnorm=I=-20:TP=-2:LRA=6:print_format=json','-f','null','-'],
                            capture_output=True,text=True,check=True)
    match = re.search(r'\{\s*"input_i".*?\}',result.stderr,re.DOTALL)
    require(match is not None,'Missing loudness analysis')
    measured = json.loads(match.group())
    require(all(measured[k] not in ('-inf','inf','nan') for k in ('input_i','input_tp','input_lra','input_thresh')),'Invalid speech loudness')
    filters = ('loudnorm=I=-20:TP=-2:LRA=6:linear=true:'
               f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
               f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}")
    subprocess.run(base+['-af',filters,'-ar','24000','-ac','1','-c:a','pcm_s16le',str(output)],capture_output=True,check=True)
    return measured


def decode_for_asr(file):
    # faster-whisper accepts 16 kHz numpy samples directly. Avoid PyAV API drift.
    import numpy as np
    result = subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(file),'-ar','16000',
                             '-ac','1','-f','f32le','pipe:1'],capture_output=True,check=True)
    samples = np.frombuffer(result.stdout,dtype='<f4').copy()
    require(len(samples) > 0 and np.isfinite(samples).all(),'Invalid independent ASR input')
    return samples


def validate_reuse(bundle,plan,provider,records):
    require(provider.get('model_id') == MODEL_ID and provider.get('revision') == REVISION
            and provider.get('speaker') == SPEAKER,'Wrong saved provider')
    require(len(records) == len(plan['lines']) == 17,'Incomplete saved recordings')
    for record,row in zip(records,plan['lines']):
        require(all(record[k] == row[k] for k in ('voice_id','line_id','text','instruct','seed')),'Saved request changed')
        for kind in ('raw','wav','ogg'):
            file=(bundle/record['files'][kind]['path']).resolve()
            require(file.is_relative_to(bundle.resolve()),'Unsafe saved recording path')
            require(sha256(file.read_bytes()) == record['files'][kind]['sha256'],'Saved recording hash mismatch')
        require(audio_metadata(bundle/record['files']['wav']['path']) == record['source_audio']
                and audio_metadata(bundle/record['files']['ogg']['path']) == record['audio'],'Saved metadata mismatch')


def finish(args,plan,provider,recordings):
    import numpy as np
    import soundfile as sf
    from huggingface_hub import HfApi, snapshot_download
    from faster_whisper import WhisperModel
    from opencc import OpenCC
    converter = OpenCC('t2s')
    asr_info = HfApi().model_info('Systran/faster-whisper-small')
    asr_path = snapshot_download('Systran/faster-whisper-small',revision=asr_info.sha)
    asr = WhisperModel(asr_path,device='cpu',compute_type='int8',cpu_threads=4)
    errors = []
    for row in recordings:
        segments,_ = asr.transcribe(decode_for_asr(args.output/row['files']['wav']['path']),language='zh',beam_size=5,
                                   condition_on_previous_text=False,initial_prompt='以下为简体中文口语录音。',vad_filter=False)
        transcript = ''.join(s.text for s in segments)
        expected,actual = normalize_text(row['text'],converter),normalize_text(transcript,converter)
        cer = character_error_rate(expected,actual)
        polarity = all(expected.count(c) == actual.count(c) for c in ('不','没'))
        row['asr'] = {'transcript':transcript,'normalized_text':actual,'cer':round(cer,6),
                      'polarity_counts_match':polarity,'passed':bool(actual) and cer <= .2 and polarity}
        if not row['asr']['passed']: errors.append(row['voice_id'])
        print(f"ASR {row['voice_id']}: CER={cer:.3f}; {transcript}",flush=True)
    write_json('generation.json',{'schema_version':1,'status':'signals_and_asr_passed' if not errors else 'asr_review_required',
               'producer_commit':os.environ.get('ORIGINAL_GENERATION_COMMIT',os.environ.get('GITHUB_SHA')),
               'producer_run':os.environ.get('ORIGINAL_GENERATION_RUN',os.environ.get('GITHUB_RUN_ID')),
               'verification_commit':os.environ.get('GITHUB_SHA'),'verification_run':os.environ.get('GITHUB_RUN_ID'),
               'request_sha256':sha256(args.request.read_bytes()),'source_voice_manifest_sha256':plan['source_voice_manifest_sha256'],
               'source_story_sha256':plan['source_story_sha256'],'recordings':recordings,'provider':provider,
               'asr_model':'Systran/faster-whisper-small','asr_revision':asr_info.sha,'asr_max_cer':.2,
               'unresolved_machine_issues':errors,'human_listening':False,
               'limits':'ASR and signal checks do not establish human listening or final creative approval.'})
    require(not errors,'ASR needs review: '+', '.join(errors))
    comparison,index,cursor = [],[],0.0
    current = {v['voice_id']:v for v in json.loads((ROOT/'game/data/voice_manifest.json').read_text())['voices']}
    for name in [recordings[i]['voice_id'] for i in (0,6,15)]:
        for label,file in [('Kokoro',ROOT/current[name]['source_file']),('Qwen3-TTS Serena',args.output/'wav'/(name+'.wav'))]:
            samples,rate = sf.read(file,dtype='float32')
            require(rate == 24000,'Comparison sample rate mismatch')
            index.append({'voice_id':name,'engine':label,'start_seconds':round(cursor,3),'end_seconds':round(cursor+len(samples)/rate,3)})
            comparison.extend([samples,np.zeros(rate,dtype=np.float32)]);cursor += len(samples)/rate+1
    sf.write(args.output/'VOICE_COMPARISON.wav',np.concatenate(comparison),24000,subtype='PCM_16')
    write_json('VOICE_COMPARISON.json',index)



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',type=Path,default=ROOT/'prompts/voice/qwen_heroine_v1.json')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--reuse',action='store_true',help='Verify preserved recordings without running TTS again')
    args = parser.parse_args()
    plan = json.loads(args.request.read_text(encoding='utf-8'))
    validate_plan(plan)
    if args.reuse:
        provider=json.loads((args.output/'provider.json').read_text(encoding='utf-8'))
        recordings=json.loads((args.output/'partial.json').read_text(encoding='utf-8'))
        require(sha256((ROOT/'game/data/voice_manifest.json').read_bytes()) == plan['source_voice_manifest_sha256'],'Saved voice source changed')
        validate_reuse(args.output,plan,provider,recordings)
        finish(args,plan,provider,recordings)
        return
    require(not args.output.exists(),'Output already exists; inspect outcome before retry')
    for folder in ('raw','wav','ogg'): (args.output/folder).mkdir(parents=True)
    import numpy as np
    import soundfile as sf
    import torch
    import onnxruntime as ort
    ort.disable_telemetry_events()
    from huggingface_hub import HfApi, snapshot_download
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    require(HfApi().model_info(MODEL_ID,revision=REVISION).sha == REVISION,'Model revision mismatch')
    snapshot = Path(snapshot_download(MODEL_ID,revision=REVISION,
                    allow_patterns=['*.json','*.txt','*.safetensors','speech_tokenizer/*']))
    files = [{'path':p.relative_to(snapshot).as_posix(),'sha256':sha256(p.read_bytes()),'bytes':p.stat().st_size}
             for p in sorted(snapshot.rglob('*')) if p.is_file()]
    config = json.loads((snapshot/'config.json').read_text())
    provider = {'schema_version':1,'model_id':MODEL_ID,'revision':REVISION,'speaker':SPEAKER,'license':'Apache-2.0',
                'model_sha256':sha256((snapshot/'model.safetensors').read_bytes()),
                'voice_bank_sha256':sha256(json.dumps(config['talker_config']['spk_id'],sort_keys=True).encode()),
                'config_sha256':sha256((snapshot/'config.json').read_bytes()),
                'checkpoint_sha256':sha256(json.dumps(files,sort_keys=True).encode()),'snapshot_files':files,
                'wrapper':'qwen-tts-0.1.1','torch_version':importlib.metadata.version('torch'),
                'processing':PROCESSING,'cpu_threads':4,'dtype':'float32'}
    def write_json(name,data):
        (args.output/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    write_json('provider.json',provider)
    engine = Qwen3TTSModel.from_pretrained(str(snapshot),device_map='cpu',dtype=torch.float32,
                                         attn_implementation='eager',low_cpu_mem_usage=True)
    recordings = []
    for row in plan['lines']:
        started = time.monotonic()
        torch.manual_seed(row['seed']); np.random.seed(row['seed'])
        with torch.inference_mode():
            wavs,rate = engine.generate_custom_voice(text=row['text'],language='Chinese',speaker=SPEAKER,
                                                      instruct=row['instruct'],max_new_tokens=384)
        require(rate == 24000 and len(wavs) == 1,'Unexpected model sample output')
        samples = np.asarray(wavs[0],dtype=np.float32).reshape(-1)
        require(np.isfinite(samples).all() and .5 <= len(samples)/rate <= max(8,len(row['text'])*.8),'Invalid/runaway speech')
        raw,wav,ogg = [args.output/folder/(row['voice_id']+ext) for folder,ext in [('raw','.wav'),('wav','.wav'),('ogg','.ogg')]]
        sf.write(raw,samples,rate,subtype='PCM_16')
        loudness = postprocess(raw,wav)
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','5',str(ogg)],check=True)
        source_audio,audio = audio_metadata(wav),audio_metadata(ogg)
        require(audio['frames'] == source_audio['frames'] and audio['peak'] < .99
                and -30 <= audio['rms_dbfs'] <= -18,'Speech fails signal/frame checks')
        recordings.append({**row,'language':'Chinese','speaker':SPEAKER,'sample_rate':rate,
                           'duration_seconds':round(source_audio['duration_seconds'],3),
                           'generation_seconds':round(time.monotonic()-started,3),'loudness_input':loudness,
                           'source_audio':source_audio,'audio':audio,
                           'files':{k:{'path':p.relative_to(args.output).as_posix(),'sha256':sha256(p.read_bytes())}
                                    for k,p in [('raw',raw),('wav',wav),('ogg',ogg)]}})
        write_json('partial.json',recordings)
        print(f"Generated {row['voice_id']}: {recordings[-1]['duration_seconds']}s; {recordings[-1]['generation_seconds']}s CPU",flush=True)
    del engine,wavs
    gc.collect()
    finish(args,plan,provider,recordings)

if __name__ == '__main__':
    main()
