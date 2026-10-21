"""Promote exact v1.5.0 artifacts after both native and public PWA acceptance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import urllib.request
import zipfile

from tools import publish_v140 as transport
from tools.story_model import ROOT, load_story
from tools.compile_tests import render_persistence_tests
from tools.build.verify_upgrade import render_upgrade_writer, render_upgrade_reader
from tools.build.verify_voice_smoke import prefix_plan
from tools.build.verify_package import required_screenshots
from tools.build.review_transport import load_bundles
from tools.compile_extras import IMAGE_TITLES, MUSIC_TITLES

VERSION = '1.5.0'
REPO = 'AureliusWu/Rain'
HUMAN_PENDING = transport.HUMAN_PENDING
require, digest, read, api, gh = transport.require, transport.digest, transport.read, transport.api, transport.gh


def select_runs(runs, commit):
    selected = {}
    for path in ('.github/workflows/game.yml', '.github/workflows/web.yml'):
        matches = [run for run in runs if run.get('path') == path and run.get('head_sha') == commit
                   and run.get('event') == 'push' and run.get('head_branch') == 'main']
        if not matches:
            return None
        run = max(matches, key=lambda item: item['id'])
        if run.get('status') != 'completed' or run.get('conclusion') != 'success':
            return None
        transport.validate_run(run, commit, path)
        selected['native' if path.endswith('game.yml') else 'web'] = run
    return selected


def native_plans():
    story = load_story()
    plan = (ROOT/'game/testcases.rpy').read_text(encoding='utf-8')
    return {'source': plan, 'standalone': plan, 'fresh_process': render_persistence_tests(story),
            'upgrade_writer': render_upgrade_writer(story), 'upgrade_reader': render_upgrade_reader(story)}


def validate_native(machine, commit, run_id, package):
    require(machine.get('version') == VERSION and machine.get('candidate_commit') == commit
            and machine.get('run_id') == run_id and machine.get('status') == 'technical_passed_visual_pending',
            'Native identity/status differs')
    require(machine.get('human_acceptance_is_not_claimed') is True
            and machine.get('human_pending') == HUMAN_PENDING and machine.get('unresolved_machine_issues') == [],
            'Native limitations or unresolved issues differ')
    media = machine.get('full_dialogue', {})
    require(media.get('project') == 'Rain' and media.get('target') == media.get('accepted') == 306
            and media.get('complete') is True and media.get('status') == 'passed'
            and media.get('humanListening') is False, 'Complete dialogue acceptance missing from native evidence')
    plans = native_plans()
    shots = set()
    for scope, plan in plans.items():
        suite = machine['suites'][scope]
        expected = (len(re.findall(r'^testcase ', plan, re.M)), len(re.findall(r'^\s+assert ', plan, re.M)),
                    len(required_screenshots(plan)))
        require(all(type(suite.get(k)) is int for k in ('cases', 'assertions', 'screenshots_checked'))
                and tuple(suite.get(k) for k in ('cases', 'assertions', 'screenshots_checked')) == expected,
                'Current native plan is incomplete: '+scope)
        require(all(type(suite.get(k)) is int and suite[k] == 0
                    for k in ('failed', 'xfailed', 'xpassed', 'skipped', 'not_run')), 'Abnormal native result')
        require(suite['process'].get('returncode') == 0 and suite['process'].get('timed_out') is False,
                'Native process failed')
        shots.update((scope, name) for name in required_screenshots(plan))
    actual = {(shot['scope'], shot['name']) for shot in machine['screenshots']}
    require(actual == shots and machine['screenshots_count'] == len(shots) == len(machine['screenshots']),
            'Native screenshot audit differs')
    quick = machine['voice_smoke']
    prefix = prefix_plan(plans['source'])
    require(quick.get('status') == 'passed' and len(quick['iterations']) == 2, 'Voice smoke missing')
    from tools.build.export_review import validate_plan_summary
    for suite in quick['iterations']:
        validate_plan_summary(suite, prefix, 'voice smoke')
    assets = read(ROOT/'game/data/asset_manifest.json')['assets']
    accepted = machine['package']
    require(accepted.get('file') == package.name and accepted.get('sha256') == digest(package)
            and accepted.get('size_in_bytes') == package.stat().st_size and accepted.get('crc') == 'passed'
            and accepted.get('assets_checked') == len(assets) and accepted.get('test_scripts_in_original_zip') is False,
            'Native package differs from audited bytes')
    require(machine['extras']['images'] == len(IMAGE_TITLES)
            and machine['extras']['music_tracks'] == len(MUSIC_TITLES), 'Extras inventory differs')
    require(machine['upgrade']['status'] == 'passed'
            and machine['upgrade']['package_sha256']['current'] == digest(package), 'Old-save upgrade differs')
    with zipfile.ZipFile(package) as bundle:
        require(bundle.testzip() is None, 'Native ZIP CRC failed')
        prefix = f'BeforeTheRainStops-{VERSION}-win/game/'
        for asset in assets:
            require(hashlib.sha256(bundle.read(prefix+asset['file'])).hexdigest() == asset['sha256'],
                    'Packaged asset differs: '+asset['id'])


def validate_web(build, acceptance, public, package):
    require(build.get('status') == 'built' and build.get('version') == VERSION
            and build.get('engine') == 'RenPy 8.5.3 official WASM'
            and build.get('web_sdk_sha256') == '954db897e65f51ea63cb2fb7b203d02be0447f4e22069514020bbe6c6691fdfc'
            and build['official_runtime_validation']['game_zip_crc'] == 'passed'
            and build.get('web_zip_sha256') == digest(package), 'Official PWA bytes differ')
    require(acceptance.get('status') == 'passed' and acceptance.get('version') == VERSION
            and len(acceptance.get('checks', [])) == 16 and acceptance.get('errors') == []
            and acceptance.get('requests_outside_application') == [], 'PWA interaction acceptance incomplete')
    require(public.get('status') == 'passed' and public.get('version') == VERSION
            and public.get('revision') == build['revision'] and public.get('errors') == []
            and public.get('target') == 'https://aureliuswu.github.io/Rain/'
            and public.get('exact_tested_artifact') is True and public.get('human_physical_device') is False,
            'Public PWA does not match the tested revision')
    with zipfile.ZipFile(package) as bundle:
        require(bundle.testzip() is None, 'PWA ZIP CRC failed')


def verify_public_worker(build, package):
    with zipfile.ZipFile(package) as bundle:
        expected = bundle.read('service-worker.js')
    configs = re.findall(rb'^const BUILD = (.+);$', expected, re.M)
    require(len(configs) == 1, 'Worker build identity missing')
    config = json.loads(configs[0])
    require(config.get('version') == VERSION and config.get('revision') == build['revision'], 'Worker revision differs')
    request = urllib.request.Request('https://aureliuswu.github.io/Rain/service-worker.js',
                                     headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
    with urllib.request.urlopen(request, timeout=60) as response:
        actual = response.read(1_048_577)
    require(actual == expected, 'Current public worker differs from tested package')
    return hashlib.sha256(actual).hexdigest()


def readback(draft, destination, expected):
    transport.validate_draft(draft, 'v'+VERSION, expected)
    destination.mkdir()
    for asset in draft['assets']:
        target = destination/asset['name']
        with target.open('wb') as stream:
            subprocess.run(['gh', 'api', '-H', 'Accept: application/octet-stream',
                            f'repos/{REPO}/releases/assets/{asset["id"]}'], stdout=stream, check=True)
        require(digest(target) == expected[asset['name']]['sha256']
                and target.stat().st_size == expected[asset['name']]['bytes'], 'Draft bytes differ')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    commit = args.commit
    require(os.environ.get('GITHUB_REPOSITORY') == REPO and re.fullmatch('[0-9a-f]{40}', commit), 'Foreign publication')
    require((ROOT/'VERSION').read_text().strip() == load_story()['version'] == VERSION, 'Version differs')
    transport.require_current_main(commit)
    require(subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == commit, 'Checkout differs')
    runs = transport.complete_items(api(f'actions/runs?head_sha={commit}&event=push&per_page=100'), 'workflow_runs')
    selected = select_runs(runs, commit)
    if not selected:
        print('Both exact native and public PWA runs are not yet successful; no publication.')
        return
    from tools.production.validate_runtime import validate
    media = validate(ROOT, complete=True)
    native, web = selected['native'], selected['web']
    jobs = {key: transport.complete_items(api(f'actions/runs/{run["id"]}/attempts/{run["run_attempt"]}/jobs?per_page=100'), 'jobs')
            for key, run in selected.items()}
    artifacts = {key: transport.complete_items(api(f'actions/runs/{run["id"]}/artifacts?per_page=100'), 'artifacts')
                 for key, run in selected.items()}
    specs = {'windows': ('native', 'windows-'+commit, 'Test, build, and run Windows package', 'Upload standalone package'),
             'review': ('native', 'review-'+commit, 'Test, build, and run Windows package', 'Upload sealed bounded review bundles'),
             'web': ('web', 'Rain-Web-'+commit, 'web', 'Upload complete PWA and browser evidence'),
             'public': ('web', f'Rain-Public-PWA-{commit}-{web["run_attempt"]}', 'deploy', 'Upload published browser evidence')}
    identities = {}
    for key, (origin, name, job, step) in specs.items():
        run = selected[origin]
        upload = transport.upload_window(jobs[origin], run, job, step)
        identities[key] = transport.artifact_for(artifacts[origin], name, run['id'], commit, upload)
    work = ROOT/'.runtime/publish-v150'
    require(not work.exists(), 'Publication directory exists')
    work.mkdir(parents=True)
    trees = {key: transport.download_artifact(item, work/key) for key, item in identities.items()}
    _, records, _ = load_bundles(trees['review'], commit, native['id'])
    winzip = transport.unique(trees['windows'], f'BeforeTheRainStops-{VERSION}-win.zip')
    webzip = transport.unique(trees['web'], f'BeforeTheRainStops-{VERSION}-web.zip')
    validate_native(records['machine'], commit, native['id'], winzip)
    build = read(transport.unique(trees['web'], 'web-build.json'))
    acceptance = read(trees['web']/'reports/pwa/acceptance.json')
    public = read(transport.unique(trees['public'], 'acceptance.json'))
    validate_web(build, acceptance, public, webzip)
    worker = verify_public_worker(build, webzip)
    release = work/'release'; release.mkdir()
    for package in (winzip, webzip):
        shutil.copy2(package, release/package.name)
    metadata = {'schema': 1, 'project': 'Rain', 'version': VERSION, 'runtime_commit': commit, 'tag_commit': commit,
                'native_run': native['id'], 'native_attempt': native['run_attempt'], 'pwa_run': web['id'],
                'pwa_attempt': web['run_attempt'], 'artifacts': identities, 'native_suites': records['machine']['suites'],
                'media': media, 'pwa_build': build, 'pwa_acceptance': acceptance, 'public_pwa': public,
                'worker_sha256': worker, 'human_acceptance_claimed': False, 'human_pending': HUMAN_PENDING,
                'authorization': 'User explicitly authorized writes, pushes and continued publication in this session.'}
    (release/'RELEASE_METADATA.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n')
    files = sorted(release.iterdir())
    (release/'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in files))
    files = sorted(release.iterdir())
    expected = {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in files}
    tag = 'v'+VERSION
    transport.require_absent('git/ref/tags/'+tag)
    transport.require_absent('releases/tags/'+tag)
    transport.require_current_main(commit)
    gh('api', '--method', 'POST', f'repos/{REPO}/git/refs', '-f', 'ref=refs/tags/'+tag, '-f', 'sha='+commit)
    gh('release', 'create', tag, *map(str, files), '--repo', REPO, '--verify-tag', '--draft',
       '--title', '雨停之前 '+tag, '--notes-file', str(ROOT/'docs/RELEASE_NOTES_V150.md'))
    draft = transport.find_draft(api('releases?per_page=100'), tag)
    readback(draft, work/'draft-readback', expected)
    transport.require_current_main(commit)
    verify_public_worker(build, webzip)
    require(api('git/ref/tags/'+tag)['object']['sha'] == commit, 'Release tag advanced')
    gh('api', '--method', 'PATCH', f'repos/{REPO}/releases/{draft["id"]}', '-F', 'draft=false', '-f', 'make_latest=true')
    published = api(f'releases/{draft["id"]}')
    require(published.get('draft') is False and published.get('prerelease') is False, 'Release is not stable/public')
    require({a['name'] for a in published['assets']} == set(expected), 'Public asset set differs')
    for asset in published['assets']:
        with urllib.request.urlopen(asset['browser_download_url'], timeout=180) as response:
            data = response.read()
        require(len(data) == expected[asset['name']]['bytes']
                and hashlib.sha256(data).hexdigest() == expected[asset['name']]['sha256'], 'Public download differs')
    output = ROOT/'reports/v150-publication.json'; output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps({'status': 'published_and_public_bytes_verified', 'version': VERSION,
        'runtime_commit': commit, 'release': published['html_url'], 'files': expected,
        'human_acceptance_claimed': False, 'human_pending': HUMAN_PENDING}, ensure_ascii=False, indent=2)+'\n')
    print(output.read_text(), flush=True)


if __name__ == '__main__':
    main()
