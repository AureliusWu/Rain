"""Stage published bytecode in Ren'Py's official old-game compatibility folder."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile
from tools.story_model import ROOT
from tools.build.verify_upgrade import BASELINE_SHA256, BASELINE_VERSION, digest


def stage(previous, project=ROOT):
    if digest(previous) != BASELINE_SHA256:
        raise ValueError('Refusing compatibility bytecode from a different release ZIP')
    prefix = f'BeforeTheRainStops-{BASELINE_VERSION}-win/game/'
    outputs = {}
    with zipfile.ZipFile(previous) as archive:
        if archive.testzip() is not None:
            raise ValueError('Baseline release CRC failed')
        for name in archive.namelist():
            if not name.startswith(prefix) or not name.endswith('.rpyc'):
                continue
            relative = PurePosixPath(name.removeprefix(prefix))
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe baseline script path')
            if not (project/'game'/relative.with_suffix('.rpy')).is_file():
                continue
            outputs[str(relative)] = archive.read(name)
    if not {'script/story_generated.rpyc', 'screens.rpyc', 'options.rpyc'} <= outputs.keys():
        raise ValueError('Published gameplay bytecode is incomplete')
    # Reject any conflicting local baseline before writing the first file.
    for name, data in outputs.items():
        target = project/'old-game'/name
        if not target.resolve().is_relative_to(project.resolve()):
            raise ValueError('Compatibility target leaves the project')
        if target.exists() and (not target.is_file() or target.read_bytes() != data):
            raise ValueError(f'Existing compatibility baseline differs: {name}')
    files = []
    for name, data in sorted(outputs.items()):
        target = project/'old-game'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files.append({'path':'old-game/'+name,'sha256':hashlib.sha256(data).hexdigest()})
    return {'previous_version':BASELINE_VERSION,'package_sha256':BASELINE_SHA256,
            'method':'RenPy 8.5.3 old-game statement-name merge', 'files':files,
            'baseline_is_not_distributed':True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous-zip', required=True, type=Path)
    report = stage(parser.parse_args().previous_zip)
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports/save-name-baseline.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f"Preserved published statement names from {len(report['files'])} bytecode files.")


if __name__ == '__main__':
    main()
