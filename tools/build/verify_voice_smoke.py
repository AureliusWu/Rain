"""Exercise the actual four-case voice prefix together before long regression."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

from tools.story_model import ROOT
from tools.build.verify_package import (collect_runtime_evidence, positive_timeout,
                                       run_native_tests, validate_suite_evidence)

PREFIX_CASES = ('native_1080_and_scaled_window', 'current_voice_replay_and_restore',
                'history_voice_replay', 'auto_waits_for_replayed_voice')


def prefix_plan(source):
    blocks = re.split(r'(?=^testcase [a-zA-Z0-9_]+:)', source, flags=re.MULTILINE)
    names = re.findall(r'^testcase ([a-zA-Z0-9_]+):', source, re.MULTILINE)
    if tuple(names[:4]) != PREFIX_CASES:
        raise ValueError('Voice smoke prefix differs from the real global test order')
    return ''.join(blocks[:5])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', required=True, type=Path)
    parser.add_argument('--iterations', type=positive_timeout, default=2)
    parser.add_argument('--timeout', type=positive_timeout, default=180)
    args = parser.parse_args()
    sdk = args.sdk.resolve()
    interpreter = sdk/'lib/py3-windows-x86_64/python.exe'
    if not interpreter.is_file():
        raise SystemExit('Windows SDK interpreter missing')
    source = (ROOT/'game/testcases.rpy').read_text(encoding='utf-8')
    prefix = prefix_plan(source)
    results = []
    with tempfile.TemporaryDirectory(prefix='galgame-voice-smoke-') as temp:
        project = Path(temp)/'project'
        # Keep the game byte-for-byte. Only the test plan is narrowed in this copy.
        shutil.copytree(ROOT/'game', project/'game', ignore=shutil.ignore_patterns('saves'))
        (project/'game/testcases.rpy').write_bytes(prefix.encode('utf-8'))
        (project/'game/testcases.rpyc').unlink(missing_ok=True)
        for iteration in range(1, args.iterations+1):
            evidence = ROOT/'reports/voice-smoke'/f'{iteration:02d}'
            command = [str(interpreter), str(sdk/'renpy.py'), str(project), 'test', 'global',
                       '--report-detailed', '--overwrite-screenshots',
                       '--savedir', str(Path(temp)/f'saves-{iteration}')]
            try:
                result = run_native_tests(command, cwd=project, evidence=evidence, timeout=args.timeout)
            finally:
                screenshots = collect_runtime_evidence(project/'BeforeTheRainStops.exe', evidence)
                (evidence/'test-plan.rpy').write_bytes(prefix.encode('utf-8'))
                stdout = (evidence/'stdout.txt').read_text(encoding='utf-8')
                stderr = (evidence/'stderr.txt').read_text(encoding='utf-8')
                (ROOT/'reports'/f'source-voice-smoke-prefix-{iteration}.txt').write_text(stdout+'\n'+stderr, encoding='utf-8')
                print(stdout, flush=True)
                print(stderr, flush=True)
            if result.returncode:
                raise ValueError(f'Voice prefix {iteration} failed with exit {result.returncode}')
            results.append(validate_suite_evidence(result.stdout, prefix, screenshots, evidence))
    report = {'status':'passed', 'iterations':results, 'cases':list(PREFIX_CASES),
              'prefix_plan_sha256':hashlib.sha256(prefix.encode('utf-8')).hexdigest(),
              'original_project_is_unmodified':True,
              'scope':'Actual full-suite prefix, copied game with only the temporary test plan narrowed'}
    (ROOT/'reports/voice-smoke-acceptance.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Voice prefix passed {len(results)} times with {results[0]["cases"]} cases / {results[0]["assertions"]} assertions each.')


if __name__ == '__main__':
    main()
