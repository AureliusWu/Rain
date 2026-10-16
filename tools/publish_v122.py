"""Publish only immutable, successful v1.2.2 native and PWA CI artifacts."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import urllib.error
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
REPO='AureliusWu/Rain'
VERSION='1.2.2'
BASELINE='2beeb1776767c281eafb9adbba7df8ae367fe24d'
AUTH='docs/review/V122_PUBLICATION_AUTHORIZATION.json'
SUPPORT={'.github/workflows/release-v122.yml','tools/publish_v122.py',
    'tools/build/export_review.py','tests/test_publish_v122.py','tests/test_export_review.py'}
PUBLICATION_SUPPORT={'.github/workflows/release-v122.yml','tools/publish_v122.py','tests/test_publish_v122.py'}
HUMAN_PENDING=['ordinary_windows','display_dpi','listening','creative_and_freeze','reading_time']


def require(condition,message):
    if not condition:raise ValueError(message)


def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def gh(*args):return subprocess.check_output(['gh',*args],cwd=ROOT)


def api(endpoint):return json.loads(gh('api',f'repos/{REPO}/{endpoint}'))


def require_current_main(commit):
    require(api('git/ref/heads/main')['object']['sha']==commit,'Main advanced; inspect before publishing')


def validate_run(run,commit,path):
    require(run.get('head_sha')==commit and run.get('head_branch')=='main'
        and run.get('event')=='push' and run.get('path')==path
        and run.get('status')=='completed' and run.get('conclusion')=='success',
        'Required exact main CI run is not successful: '+path)
    require(run.get('repository',{}).get('full_name')==REPO,'CI repository differs')
    require(type(run.get('id')) is int and run['id']>0,'Invalid CI run ID')
    require(type(run.get('run_attempt')) is int and run['run_attempt']>0,'Invalid CI attempt')


def validate_source_changes(paths,support=SUPPORT):
    unexpected=[p for p in paths if not (p.startswith('docs/') or p in support
        or p in {'README.md','CHANGELOG.md','ROADMAP.md'})]
    require(not unexpected,'Accepted runtime changed: '+', '.join(unexpected))


def validate_source(commit,runtime_commit,authorization):
    require(re.fullmatch('[0-9a-f]{40}',commit) is not None,'Invalid publication commit')
    require(re.fullmatch('[0-9a-f]{40}',runtime_commit) is not None,'Invalid tested runtime commit')
    require(authorization.get('schema')==1 and authorization.get('version')==VERSION
        and authorization.get('repository')==REPO and authorization.get('runtime_baseline')==BASELINE,
        'Publication authorization identity differs')
    require(authorization.get('publication_authorized') is True
        and authorization.get('user_instruction')=='完成发布版本更新闭环'
        and authorization.get('human_acceptance_claimed') is False
        and authorization.get('human_pending')==HUMAN_PENDING,'Publication authorization or pending scope differs')
    require(authorization.get('runtime_validation',{}).get('commit')==runtime_commit,
        'Tested runtime authorization differs')
    require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==commit,
        'Checkout differs from publication commit')
    require(not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).strip(),
        'Tracked publication checkout changed')
    require((ROOT/'VERSION').read_text().strip()==VERSION,'VERSION differs')
    subprocess.run(['git','merge-base','--is-ancestor',BASELINE,runtime_commit],cwd=ROOT,check=True)
    subprocess.run(['git','merge-base','--is-ancestor',runtime_commit,commit],cwd=ROOT,check=True)
    runtime_paths=subprocess.check_output(['git','diff','--name-only',BASELINE,runtime_commit],cwd=ROOT,text=True).splitlines()
    publication_paths=subprocess.check_output(['git','diff','--name-only',runtime_commit,commit],cwd=ROOT,text=True).splitlines()
    validate_source_changes(runtime_paths)
    validate_source_changes(publication_paths,PUBLICATION_SUPPORT)
    require(set(authorization.get('support_sha256',{}))==SUPPORT,'Publication support allowlist differs')
    runtime_support=authorization['runtime_validation'].get('support_sha256',{})
    require(set(runtime_support)==SUPPORT,'Tested runtime support allowlist differs')
    for source,hashes in ((commit,authorization['support_sha256']),(runtime_commit,runtime_support)):
        for path,expected in hashes.items():
            blob=subprocess.check_output(['git','show',source+':'+path],cwd=ROOT)
            require(hashlib.sha256(blob).hexdigest()==expected,'Checked support hash differs: '+path)
    return {'runtime_baseline_difference':runtime_paths,'publication_difference':publication_paths}


def validate_evidence_runs(native,origin,web,runtime_commit,authorization):
    binding=authorization['runtime_validation']
    require(all(type(value) is int and value>0 for value in (binding['native_run']['id'],
        binding['native_run']['artifact_attempt'],binding['pwa_run']['id'],binding['pwa_run']['attempt'])),
        'Invalid authorized evidence IDs/attempts')
    for run,path in ((native,'.github/workflows/game.yml'),(origin,'.github/workflows/game.yml'),
            (web,'.github/workflows/web.yml')):validate_run(run,runtime_commit,path)
    require(native['id']==origin['id']==binding['native_run']['id']
        and origin['run_attempt']==binding['native_run']['artifact_attempt']
        and native['run_attempt']>=origin['run_attempt'],'Native evidence origin differs')
    require(web['id']==binding['pwa_run']['id'] and web['run_attempt']==binding['pwa_run']['attempt'],
        'PWA evidence origin differs')


def complete_items(response,key):
    items=response.get(key)
    require(isinstance(items,list) and type(response.get('total_count')) is int
        and response['total_count']==len(items),'Incomplete CI '+key+' response')
    return items


def timestamp(value):
    require(isinstance(value,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',value) is not None,
        'Invalid CI timestamp')
    return datetime.fromisoformat(value.replace('Z','+00:00'))


def upload_window(jobs,run,job_name,step_name):
    matches=[job for job in jobs if job.get('name')==job_name]
    require(len(matches)==1,'Missing or duplicated upload job: '+job_name)
    job=matches[0]
    require(type(job.get('id')) is int and job['id']>0 and job.get('run_id')==run['id']
        and job.get('run_attempt')==run['run_attempt'] and job.get('head_sha')==run['head_sha']
        and job.get('status')=='completed' and job.get('conclusion')=='success','Upload job identity/status differs')
    steps=[step for step in job.get('steps',[]) if step.get('name')==step_name]
    require(len(steps)==1,'Missing or duplicated upload step: '+step_name)
    step=steps[0]
    require(step.get('status')=='completed' and step.get('conclusion')=='success'
        and type(step.get('number')) is int and step['number']>0,'Upload step did not succeed')
    require(timestamp(job.get('started_at'))<=timestamp(step.get('started_at'))
        <=timestamp(step.get('completed_at'))<=timestamp(job.get('completed_at')),'Upload step time outside successful job')
    return {'run_id':run['id'],'run_attempt':run['run_attempt'],'job_id':job['id'],'job_name':job_name,
        'step_number':step['number'],'step_name':step_name,
        'started_at':step['started_at'],'completed_at':step['completed_at']}


def artifact_for(artifacts,name,run_id,commit,upload):
    require(upload.get('run_id')==run_id,'Artifact upload run differs')
    start,end=timestamp(upload.get('started_at')),timestamp(upload.get('completed_at'))
    require(start<=end,'Reversed artifact upload window')
    matches=[a for a in artifacts if a.get('name')==name
        and start<=timestamp(a.get('created_at'))<=end]
    require(len(matches)==1,'Exact CI artifact missing or duplicated: '+name)
    item=matches[0]
    require(item.get('expired') is False and type(item.get('id')) is int and item['id']>0,'Artifact expired or invalid')
    require(isinstance(item.get('digest'),str)
        and re.fullmatch('sha256:[0-9a-f]{64}',item['digest']) is not None,'Artifact digest unavailable')
    workflow=item.get('workflow_run',{})
    require(workflow.get('id')==run_id and workflow.get('head_sha')==commit,'Artifact identity differs')
    return item


def extract_checked(archive,destination):
    with zipfile.ZipFile(archive) as bundle:
        names=bundle.namelist()
        require(len(names)==len(set(names)),'Duplicate artifact paths')
        require(all(n and not n.startswith(('/','\\')) and '\\' not in n and ':' not in n
            and '\x00' not in n and '..' not in n.split('/')
            for n in [*names,*(i.orig_filename for i in bundle.infolist())]),'Unsafe artifact paths')
        require(all((i.external_attr>>16)&0o170000!=0o120000 for i in bundle.infolist()),'Artifact symlink')
        require(sum(i.file_size for i in bundle.infolist())<1_600_000_000,'Artifact expansion exceeds bound')
        require(bundle.testzip() is None,'Artifact CRC failed')
        bundle.extractall(destination)


def download_artifact(item,destination):
    archive=destination.with_suffix('.artifact.zip')
    with archive.open('wb') as stream:
        subprocess.run(['gh','api',f'repos/{REPO}/actions/artifacts/{item["id"]}/zip'],stdout=stream,check=True)
    require('sha256:'+digest(archive)==item['digest'],'Downloaded CI artifact digest differs')
    destination.mkdir()
    extract_checked(archive,destination)
    return destination


def unique(root,name):
    matches=list(root.rglob(name))
    require(len(matches)==1,'Missing or ambiguous evidence: '+name)
    return matches[0]


def validate_native(machine,commit,run_id,package):
    require(machine.get('version')==VERSION and machine.get('candidate_commit')==commit
        and machine.get('run_id')==run_id and machine.get('status')=='technical_passed_visual_pending',
        'Native audit identity/status differs')
    require(machine.get('human_acceptance_is_not_claimed') is True
        and machine.get('human_pending')==HUMAN_PENDING
        and machine.get('unresolved_machine_issues')==[],'Native limitations or unresolved issues differ')
    expected={'source':(37,477,84),'standalone':(37,477,84),'fresh_process':(1,16,3),
        'upgrade_writer':(1,14,3),'upgrade_reader':(2,26,4)}
    for scope,totals in expected.items():
        suite=machine['suites'][scope]
        require(all(type(suite.get(k)) is int for k in ('cases','assertions','screenshots_checked'))
            and tuple(suite.get(k) for k in ('cases','assertions','screenshots_checked'))==totals,
            'v1.2.2 native suite incomplete: '+scope)
        require(all(type(suite.get(k)) is int and suite[k]==0
            for k in ('failed','xfailed','xpassed','skipped','not_run')),'Native abnormal results: '+scope)
        require(type(suite['process'].get('returncode')) is int and suite['process']['returncode']==0
            and suite['process'].get('timed_out') is False,
            'Native process failed: '+scope)
    require(machine.get('screenshots_count')==178 and len(machine.get('screenshots',[]))==178,
        'Native screenshot audit incomplete')
    quick=machine['voice_smoke']
    require(quick.get('status')=='passed' and len(quick.get('iterations',[]))==2,'Voice prefix incomplete')
    for suite in quick['iterations']:
        require(all(type(suite.get(k)) is int for k in ('cases','assertions','screenshots_checked'))
            and tuple(suite.get(k) for k in ('cases','assertions','screenshots_checked'))==(7,132,31)
            and all(type(suite.get(k)) is int and suite[k]==0
            for k in ('failed','xfailed','xpassed','skipped','not_run')),'Voice prefix differs')
    accepted=machine['package']
    require(accepted['file']==package.name and accepted['sha256']==digest(package)
        and accepted['size_in_bytes']==package.stat().st_size and accepted.get('crc')=='passed'
        and accepted.get('assets_checked')==85 and accepted.get('test_scripts_in_original_zip') is False,
        'Native package differs from accepted bytes')
    require(machine['upgrade'].get('status')=='passed'
        and machine['upgrade']['package_sha256']['current']==accepted['sha256'],
        'Real previous-version save upgrade differs')
    with zipfile.ZipFile(package) as bundle:require(bundle.testzip() is None,'Native ZIP CRC failed')


def validate_web(build,acceptance,public,package):
    require(build.get('status')=='built' and build.get('version')==VERSION
        and build.get('engine')=='RenPy 8.5.3 official WASM'
        and build.get('web_zip_sha256')==digest(package),'PWA build/package differs')
    require(build.get('web_sdk_sha256')=='954db897e65f51ea63cb2fb7b203d02be0447f4e22069514020bbe6c6691fdfc'
        and build['official_runtime_validation'].get('game_zip_crc')=='passed','Official WASM identity differs')
    require(acceptance.get('status')=='passed' and acceptance.get('version')==VERSION
        and len(acceptance.get('checks',[]))==14 and acceptance.get('errors')==[]
        and acceptance.get('requests_outside_application')==[],'Actual 14-case PWA acceptance incomplete')
    require(public.get('status')=='passed' and public.get('version')==VERSION
        and public.get('revision')==build['revision'] and public.get('errors')==[]
        and public.get('target')=='https://aureliuswu.github.io/Rain/'
        and public.get('exact_tested_artifact') is True and public.get('human_physical_device') is False,
        'Published PWA does not match the exact tested revision')
    with zipfile.ZipFile(package) as bundle:require(bundle.testzip() is None,'PWA ZIP CRC failed')


def verify_public_worker(build,package):
    with zipfile.ZipFile(package) as bundle:expected=bundle.read('service-worker.js')
    configs=re.findall(rb'^const BUILD = (.+);$',expected,re.MULTILINE)
    require(len(configs)==1,'Packaged worker build config missing or ambiguous')
    config=json.loads(configs[0])
    require(config.get('version')==VERSION and config.get('revision')==build.get('revision'),
        'Packaged worker revision differs')
    url='https://aureliuswu.github.io/Rain/service-worker.js'
    request=urllib.request.Request(url,headers={'Cache-Control':'no-cache','Pragma':'no-cache'})
    with urllib.request.urlopen(request,timeout=60) as response:actual=response.read(1_048_577)
    require(len(actual)<=1_048_576 and actual==expected,'Current public worker differs from tested PWA bytes')
    return {'url':url,'revision':build['revision'],'sha256':hashlib.sha256(actual).hexdigest(),
        'bytes':len(actual),'status':'exact_tested_bytes_verified'}


def require_absent(endpoint):
    result=subprocess.run(['gh','api',f'repos/{REPO}/{endpoint}'],capture_output=True,text=True)
    require(result.returncode!=0 and '(HTTP 404)' in result.stderr,'Existing or unverifiable '+endpoint)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit',required=True)
    parser.add_argument('--runtime-commit',required=True)
    parser.add_argument('--native-run',required=True,type=int)
    args=parser.parse_args()
    require(os.environ.get('GITHUB_REPOSITORY')==REPO,'Only the authorized repository may publish')
    require_current_main(args.commit)
    authorization=read(ROOT/AUTH)
    source=validate_source(args.commit,args.runtime_commit,authorization)
    binding=authorization['runtime_validation']
    native=api(f'actions/runs/{args.native_run}')
    origin=api(f'actions/runs/{native["id"]}/attempts/{binding["native_run"]["artifact_attempt"]}')
    web=api(f'actions/runs/{binding["pwa_run"]["id"]}')
    validate_evidence_runs(native,origin,web,args.runtime_commit,authorization)
    native_jobs=complete_items(api(f'actions/runs/{origin["id"]}/attempts/{origin["run_attempt"]}/jobs?per_page=100'),'jobs')
    web_jobs=complete_items(api(f'actions/runs/{web["id"]}/attempts/{web["run_attempt"]}/jobs?per_page=100'),'jobs')
    native_artifacts=complete_items(api(f'actions/runs/{native["id"]}/artifacts?per_page=100'),'artifacts')
    web_artifacts=complete_items(api(f'actions/runs/{web["id"]}/artifacts?per_page=100'),'artifacts')
    uploads={
        'windows':upload_window(native_jobs,origin,'Test, build, and run Windows package','Upload standalone package'),
        'review':upload_window(native_jobs,origin,'Test, build, and run Windows package','Upload sealed bounded review bundles'),
        'web':upload_window(web_jobs,web,'web','Upload complete PWA and browser evidence'),
        'public':upload_window(web_jobs,web,'deploy','Upload published browser evidence')}
    identities={
        'windows':artifact_for(native_artifacts,'windows-'+args.runtime_commit,native['id'],args.runtime_commit,uploads['windows']),
        'review':artifact_for(native_artifacts,'review-'+args.runtime_commit,native['id'],args.runtime_commit,uploads['review']),
        'web':artifact_for(web_artifacts,'Rain-Web-'+args.runtime_commit,web['id'],args.runtime_commit,uploads['web']),
        'public':artifact_for(web_artifacts,f'Rain-Public-PWA-{args.runtime_commit}-{web["run_attempt"]}',web['id'],args.runtime_commit,uploads['public'])}
    work=ROOT/'.runtime/publish-v122'
    require(not work.exists(),'Publication directory exists; inspect previous attempt')
    work.mkdir(parents=True)
    trees={name:download_artifact(item,work/name) for name,item in identities.items()}
    from tools.build.review_transport import load_bundles
    _,records,_=load_bundles(trees['review'],args.runtime_commit,native['id'])
    machine=records['machine']
    winzip=unique(trees['windows'],f'BeforeTheRainStops-{VERSION}-win.zip')
    webzip=unique(trees['web'],f'BeforeTheRainStops-{VERSION}-web.zip')
    validate_native(machine,args.runtime_commit,native['id'],winzip)
    build=read(unique(trees['web'],'web-build.json'))
    acceptance=read(trees['web']/'reports/pwa/acceptance.json')
    public=read(unique(trees['public'],'acceptance.json'))
    validate_web(build,acceptance,public,webzip)
    live_worker=verify_public_worker(build,webzip)
    tag='v'+VERSION
    require_absent('git/ref/tags/'+tag)
    require_absent('releases/tags/'+tag)
    release=work/'release';release.mkdir()
    for package in (winzip,webzip):shutil.copy2(package,release/package.name)
    metadata={'schema':1,'project':'Rain','version':VERSION,'tag':tag,'publication_commit':args.commit,
        'runtime_commit':args.runtime_commit,'tag_commit':args.runtime_commit,
        'runtime_baseline':BASELINE,'source_difference':source,'source_identity':'identical player source; only checked publication support/metadata differs',
        'native_run':{'id':native['id'],'url':native['html_url'],'completed_attempt':native['run_attempt'],
            'artifact_attempt':origin['run_attempt']},'pwa_run':{'id':web['id'],'url':web['html_url'],'attempt':web['run_attempt']},
        'artifacts':{name:{key:item[key] for key in ('id','name','digest','size_in_bytes')} for name,item in identities.items()},
        'artifact_upload_steps':uploads,
        'files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in (winzip,webzip)},
        'native_suites':machine['suites'],'native_screenshot_audit':178,'pwa_build':build,
        'pwa_acceptance':acceptance,'published_pwa':public,'current_public_worker':live_worker,'publication_authorization':authorization,
        'human_acceptance_claimed':False,'human_pending':HUMAN_PENDING,
        'visual_review':'178 original PNGs decoded/hashed by native audit; sealed inspection-copy bindings verified; no new direct visual or human acceptance claimed',
        'release_readback':'This build metadata precedes publication; final readback evidence is exported by the publication workflow.'}
    (release/'RELEASE_METADATA.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    files=sorted(release.iterdir())
    sums={p.name:digest(p) for p in files}
    (release/'SHA256SUMS.txt').write_text(''.join(f'{sums[p.name]}  {p.name}\n' for p in files),encoding='utf-8')
    files=sorted(release.iterdir())
    expected={p.name:digest(p) for p in files}
    require_current_main(args.commit)
    gh('api','--method','POST',f'repos/{REPO}/git/refs','-f','ref=refs/tags/'+tag,'-f','sha='+args.runtime_commit)
    require(api('git/ref/tags/'+tag)['object']['sha']==args.runtime_commit,'New tag identity differs')
    gh('release','create',tag,*map(str,files),'--repo',REPO,'--verify-tag','--draft',
        '--title','雨停之前 '+tag,'--notes-file',str(ROOT/'docs/RELEASE_NOTES_V122.md'))
    draft=api('releases/tags/'+tag)
    require(draft.get('draft') is True and draft.get('prerelease') is False,'Release must remain draft until readback')
    require({a['name'] for a in draft['assets']}==set(expected),'Draft asset set differs')
    readback=work/'draft-readback';readback.mkdir()
    gh('release','download',tag,'--repo',REPO,'--dir',str(readback))
    require({p.name:digest(p) for p in readback.iterdir()}==expected,'Draft download readback differs')
    require_current_main(args.commit)
    require(api('git/ref/tags/'+tag)['object']['sha']==args.runtime_commit,'Tag advanced before publication')
    verify_public_worker(build,webzip)
    gh('release','edit',tag,'--repo',REPO,'--draft=false','--latest')
    published=api('releases/tags/'+tag)
    require(published.get('draft') is False and published.get('prerelease') is False,'Release not publicly stable')
    require(api('git/ref/tags/'+tag)['object']['sha']==args.runtime_commit,'Published tag target differs')
    public_checks={}
    for asset in published['assets']:
        require(asset['name'] in expected,'Unexpected published asset')
        target=work/('public-'+asset['name'])
        with urllib.request.urlopen(asset['browser_download_url'],timeout=180) as response,target.open('wb') as stream:
            shutil.copyfileobj(response,stream)
        require(digest(target)==expected[asset['name']],'Public download readback differs: '+asset['name'])
        public_checks[asset['name']]={'sha256':digest(target),'bytes':target.stat().st_size,'url':asset['browser_download_url']}
    require(set(public_checks)==set(expected),'Public download asset set incomplete')
    final_worker=verify_public_worker(build,webzip)
    evidence={'status':'published_and_public_bytes_verified','version':VERSION,'publication_commit':args.commit,
        'runtime_commit':args.runtime_commit,'tag_commit':args.runtime_commit,
        'release':published['html_url'],'files':public_checks,'pwa_revision':build['revision'],
        'current_public_worker':final_worker,
        'human_pending':HUMAN_PENDING,'human_acceptance_claimed':False}
    output=ROOT/'reports/v122-publication.json';output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(evidence,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
