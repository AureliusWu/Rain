"""Publish only immutable, successful v1.2.2 native and PWA CI artifacts."""
import argparse
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


def validate_source_changes(paths):
    unexpected=[p for p in paths if not (p.startswith('docs/') or p in SUPPORT
        or p in {'README.md','CHANGELOG.md','ROADMAP.md'})]
    require(not unexpected,'Accepted runtime changed: '+', '.join(unexpected))


def validate_source(commit,authorization):
    require(re.fullmatch('[0-9a-f]{40}',commit) is not None,'Invalid publication commit')
    require(authorization.get('schema')==1 and authorization.get('version')==VERSION
        and authorization.get('repository')==REPO and authorization.get('runtime_baseline')==BASELINE,
        'Publication authorization identity differs')
    require(authorization.get('publication_authorized') is True
        and authorization.get('user_instruction')=='完成发布版本更新闭环'
        and authorization.get('human_acceptance_claimed') is False
        and authorization.get('human_pending')==HUMAN_PENDING,'Publication authorization or pending scope differs')
    require((ROOT/'VERSION').read_text().strip()==VERSION,'VERSION differs')
    subprocess.run(['git','merge-base','--is-ancestor',BASELINE,commit],cwd=ROOT,check=True)
    paths=subprocess.check_output(['git','diff','--name-only',BASELINE,commit],cwd=ROOT,text=True).splitlines()
    validate_source_changes(paths)
    require(set(authorization.get('support_sha256',{}))==SUPPORT,'Publication support allowlist differs')
    for path,expected in authorization['support_sha256'].items():
        blob=subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)
        require(hashlib.sha256(blob).hexdigest()==expected,'Publication support hash differs: '+path)
    return paths


def artifact_for(artifacts,name,run_id,commit):
    matches=[a for a in artifacts if a.get('name')==name]
    require(len(matches)==1,'Exact CI artifact missing or duplicated: '+name)
    item=matches[0]
    require(item.get('expired') is False and type(item.get('id')) is int,'Artifact expired or invalid')
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


def require_absent(endpoint):
    result=subprocess.run(['gh','api',f'repos/{REPO}/{endpoint}'],capture_output=True,text=True)
    require(result.returncode!=0 and '(HTTP 404)' in result.stderr,'Existing or unverifiable '+endpoint)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit',required=True)
    parser.add_argument('--native-run',required=True,type=int)
    args=parser.parse_args()
    require(os.environ.get('GITHUB_REPOSITORY')==REPO,'Only the authorized repository may publish')
    require_current_main(args.commit)
    authorization=read(ROOT/AUTH)
    paths=validate_source(args.commit,authorization)
    native=api(f'actions/runs/{args.native_run}')
    validate_run(native,args.commit,'.github/workflows/game.yml')
    candidates=api(f'actions/workflows/web.yml/runs?head_sha={args.commit}&branch=main&event=push&per_page=100')['workflow_runs']
    require(bool(candidates),'No PWA workflow run for exact main commit')
    web=max(candidates,key=lambda r:(r['run_number'],r['run_attempt']))
    validate_run(web,args.commit,'.github/workflows/web.yml')
    native_artifacts=api(f'actions/runs/{native["id"]}/artifacts?per_page=100')['artifacts']
    web_artifacts=api(f'actions/runs/{web["id"]}/artifacts?per_page=100')['artifacts']
    identities={
        'windows':artifact_for(native_artifacts,'windows-'+args.commit,native['id'],args.commit),
        'review':artifact_for(native_artifacts,'review-'+args.commit,native['id'],args.commit),
        'web':artifact_for(web_artifacts,'Rain-Web-'+args.commit,web['id'],args.commit),
        'public':artifact_for(web_artifacts,f'Rain-Public-PWA-{args.commit}-{web["run_attempt"]}',web['id'],args.commit)}
    work=ROOT/'.runtime/publish-v122'
    require(not work.exists(),'Publication directory exists; inspect previous attempt')
    work.mkdir(parents=True)
    trees={name:download_artifact(item,work/name) for name,item in identities.items()}
    from tools.build.review_transport import load_bundles
    _,records,_=load_bundles(trees['review'],args.commit,native['id'])
    machine=records['machine']
    winzip=unique(trees['windows'],f'BeforeTheRainStops-{VERSION}-win.zip')
    webzip=unique(trees['web'],f'BeforeTheRainStops-{VERSION}-web.zip')
    validate_native(machine,args.commit,native['id'],winzip)
    build=read(unique(trees['web'],'web-build.json'))
    acceptance=read(trees['web']/'reports/pwa/acceptance.json')
    public=read(unique(trees['public'],'acceptance.json'))
    validate_web(build,acceptance,public,webzip)
    tag='v'+VERSION
    require_absent('git/ref/tags/'+tag)
    require_absent('releases/tags/'+tag)
    release=work/'release';release.mkdir()
    for package in (winzip,webzip):shutil.copy2(package,release/package.name)
    metadata={'schema':1,'project':'Rain','version':VERSION,'tag':tag,'publication_commit':args.commit,
        'runtime_baseline':BASELINE,'source_difference':paths,'source_identity':'identical player source; only checked publication support/metadata differs',
        'native_run':{'id':native['id'],'url':native['html_url']},'pwa_run':{'id':web['id'],'url':web['html_url']},
        'artifacts':{name:{key:item[key] for key in ('id','name','digest','size_in_bytes')} for name,item in identities.items()},
        'files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in (winzip,webzip)},
        'native_suites':machine['suites'],'native_screenshot_audit':178,'pwa_build':build,
        'pwa_acceptance':acceptance,'published_pwa':public,'publication_authorization':authorization,
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
    gh('api','--method','POST',f'repos/{REPO}/git/refs','-f','ref=refs/tags/'+tag,'-f','sha='+args.commit)
    require(api('git/ref/tags/'+tag)['object']['sha']==args.commit,'New tag identity differs')
    gh('release','create',tag,*map(str,files),'--repo',REPO,'--verify-tag','--draft',
        '--title','雨停之前 '+tag,'--notes-file',str(ROOT/'docs/RELEASE_NOTES_V122.md'))
    draft=api('releases/tags/'+tag)
    require(draft.get('draft') is True and draft.get('prerelease') is False,'Release must remain draft until readback')
    require({a['name'] for a in draft['assets']}==set(expected),'Draft asset set differs')
    readback=work/'draft-readback';readback.mkdir()
    gh('release','download',tag,'--repo',REPO,'--dir',str(readback))
    require({p.name:digest(p) for p in readback.iterdir()}==expected,'Draft download readback differs')
    require_current_main(args.commit)
    require(api('git/ref/tags/'+tag)['object']['sha']==args.commit,'Tag advanced before publication')
    gh('release','edit',tag,'--repo',REPO,'--draft=false','--latest')
    published=api('releases/tags/'+tag)
    require(published.get('draft') is False and published.get('prerelease') is False,'Release not publicly stable')
    require(api('git/ref/tags/'+tag)['object']['sha']==args.commit,'Published tag target differs')
    public_checks={}
    for asset in published['assets']:
        require(asset['name'] in expected,'Unexpected published asset')
        target=work/('public-'+asset['name'])
        with urllib.request.urlopen(asset['browser_download_url'],timeout=180) as response,target.open('wb') as stream:
            shutil.copyfileobj(response,stream)
        require(digest(target)==expected[asset['name']],'Public download readback differs: '+asset['name'])
        public_checks[asset['name']]={'sha256':digest(target),'bytes':target.stat().st_size,'url':asset['browser_download_url']}
    require(set(public_checks)==set(expected),'Public download asset set incomplete')
    evidence={'status':'published_and_public_bytes_verified','version':VERSION,'publication_commit':args.commit,
        'release':published['html_url'],'files':public_checks,'pwa_revision':build['revision'],
        'human_pending':HUMAN_PENDING,'human_acceptance_claimed':False}
    output=ROOT/'reports/v122-publication.json';output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(evidence,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
