"""Split exact CI package and native evidence into verifiable 20 MiB transfers."""
import hashlib
import json
import os
from pathlib import Path
import zipfile
from tools.story_model import ROOT


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def main():
    destination=ROOT/'transfer'
    if destination.exists(): raise ValueError('Transfer outcome already exists; inspect before rerun')
    destination.mkdir()
    version=(ROOT/'VERSION').read_text().strip()
    package=ROOT/'dist'/f'BeforeTheRainStops-{version}-win.zip'
    if not package.is_file(): raise ValueError('Validated Windows package missing')
    files=[]
    for file in sorted((ROOT/'dist').glob('*')):
        if file.is_file(): files.append((file,'windows/'+file.name))
    reports=ROOT/'reports'
    for file in sorted(reports.rglob('*')):
        if not file.is_file(): continue
        relative=file.relative_to(reports).as_posix()
        if '/' not in relative or relative.startswith(('source-process/','screenshots/','package/')):
            files.append((file,'evidence/reports/'+relative))
    if len([f for f,_ in files if f.suffix=='.png' and '/screenshots/' in f.as_posix()]) != 131:
        raise ValueError('Expected all 131 native screenshots')
    archive=destination/'bundle.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for file,name in files: z.write(file,name)
    manifest={'schema_version':1,'candidate_commit':os.environ['GITHUB_SHA'],'version':version,
              'package_sha256':digest(package),'bundle_sha256':digest(archive),
              'bundle_bytes':archive.stat().st_size,'parts':[]}
    with archive.open('rb') as stream:
        index=0
        while data:=stream.read(20*1024*1024):
            folder=destination/f'part{index:02d}';folder.mkdir()
            (folder/'bundle.part').write_bytes(data)
            manifest['parts'].append({'index':index,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            index+=1
    if len(manifest['parts'])>20: raise ValueError('Increase workflow transfer capacity before upload')
    for part in manifest['parts']:
        (destination/f"part{part['index']:02d}"/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f"Exact package/evidence transfer: {manifest['bundle_bytes']} bytes in {len(manifest['parts'])} parts")


if __name__=='__main__': main()
