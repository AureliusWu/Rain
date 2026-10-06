"""Bind formal v1 publication to the exact technically and human-reviewed ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import zipfile

HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
GROUPS = ("ordinary_windows", "display_dpi", "listening", "creative_and_freeze")
ERROR_COUNTS = ("failed", "xfailed", "xpassed", "skipped", "not_run")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def has_text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_machine(machine, version):
    require(isinstance(version, str) and re.fullmatch(r"[1-9][0-9]*\.[0-9]+\.[0-9]+", version), "Formal gate requires a v1+ version")
    require(isinstance(machine, dict), "Machine acceptance must be a JSON object")
    require(machine.get("status") == "technical_and_visual_passed_with_human_limits", "Machine/visual acceptance incomplete")
    require(machine.get("unresolved_machine_issues") == [], "Unresolved or missing machine issue record")
    candidate = machine.get("candidate_commit", "")
    package = machine.get("package", {})
    require(isinstance(package, dict), "Invalid package record")
    require(isinstance(candidate, str) and HEX40.fullmatch(candidate), "Invalid candidate commit")
    require(machine.get("version") == version, "Machine version mismatch")
    digest = package.get("sha256")
    require(isinstance(digest, str) and HEX64.fullmatch(digest), "Invalid package SHA-256")
    require(package.get("file") == f"BeforeTheRainStops-{version}-win.zip", "Package filename/version mismatch")
    require(type(package.get("size_in_bytes")) is int and package["size_in_bytes"] > 0, "Missing package size")
    require(package.get("crc") == "passed" and package.get("test_scripts_in_original_zip") is False, "Package cleanliness/CRC not accepted")
    python_tests = machine.get("python_tests")
    require(isinstance(python_tests, dict) and type(python_tests.get("passed")) is int
            and python_tests["passed"] > 0 and machine.get("lint") == "passed", "Authoring/lint acceptance incomplete")
    suites = machine.get("suites")
    require(isinstance(suites, dict), "Missing suite records")
    for scope in ("source", "standalone", "fresh_process"):
        suite = suites.get(scope)
        require(isinstance(suite, dict), f"Missing {scope} suite")
        process = suite.get("process", {})
        require(all(type(suite.get(k)) is int and suite[k] > 0 for k in ("cases", "assertions")), f"Invalid {scope} test counts")
        require(all(type(suite.get(k)) is int and suite[k] == 0 for k in ERROR_COUNTS), f"Incomplete {scope} suite")
        require(isinstance(process, dict) and type(process.get("returncode")) is int
                and process["returncode"] == 0 and process.get("timed_out") is False, f"Unaccepted {scope} process")
    require(all(suites["source"][k] == suites["standalone"][k] for k in ("cases", "assertions")), "Source/EXE suite counts differ")
    require(type(machine.get("run_id")) is int and machine["run_id"] > 0, "Missing accepted CI run")
    artifacts = machine.get("artifacts")
    require(isinstance(artifacts, list) and all(isinstance(a, dict) for a in artifacts), "Invalid artifact records")
    artifacts = [a for a in artifacts if a.get("name") == f"windows-{candidate}"]
    require(len(artifacts) == 1 and type(artifacts[0].get("id")) is int and artifacts[0]["id"] > 0, "Missing unique accepted package artifact")
    return {"version": version, "candidate": candidate, "run_id": machine["run_id"],
            "artifact_id": artifacts[0]["id"], "package": package["file"],
            "sha256": package["sha256"], "size": package["size_in_bytes"]}


def validate_approval(machine, human, version, publication=None, voice=None):
    selection = validate_machine(machine, version)
    require(isinstance(human, dict), "Human acceptance must be a JSON object")
    if publication is not None:
        require(isinstance(publication, dict) and publication.get('schema_version') == 1
                and publication.get('status') == 'authorized_by_user', 'Invalid publication authorization')
        require(publication.get('version') == version
                and publication.get('candidate_commit') == selection['candidate']
                and publication.get('package_sha256') == selection['sha256'], 'Publication targets another candidate or ZIP')
        require(publication.get('instruction') == '完成后发布正式版'
                and publication.get('condition') == 'voice_upgrade_completed'
                and has_text(publication.get('requested_at')), 'Missing explicit conditional publication instruction')
        require(human.get('version') == version and human.get('candidate_commit') == selection['candidate']
                and human.get('package_sha256') == selection['sha256'], 'Human follow-up targets another candidate')
        require(human.get('schema_version') == 1 and human.get('status') in ('pending','approved') and human.get('unresolved_issues') == [],
                'Unresolved human issues or malformed follow-up record')
        pending = []
        for group in (*GROUPS, 'reading_time'):
            item = human.get(group)
            require(isinstance(item,dict) and item.get('status') in ('pending','passed'), 'Invalid human follow-up status')
            if item['status'] == 'pending':
                pending.append(group)
                require(item.get('evidence') == '', 'Pending group cannot claim completed evidence')
            else:
                require(has_text(item.get('evidence')), 'Completed group lacks evidence')
        require(publication.get('pending_human_checks') == pending, 'Authorization must disclose actual pending checks')
        require(human['status'] == ('pending' if pending else 'approved'), 'Human overall status disagrees with groups')
        if 'reading_time' in pending:
            require(human['reading_time'].get('normal_minutes') is None and human['reading_time'].get('true_minutes') is None,
                    'Pending timing cannot claim measured minutes')
        require(isinstance(voice,dict) and voice.get('status') == 'signals_and_asr_passed'
                and voice.get('unresolved_machine_issues') == [] and voice.get('human_listening') is False,
                'Voice upgrade verification incomplete')
        provider = voice.get('provider', {})
        from tools.audio_process.qwen_voice import MODEL_ID, REVISION, SPEAKER
        require(isinstance(provider,dict) and (provider.get('model_id'),provider.get('revision'),provider.get('speaker'))
                == (MODEL_ID, REVISION, SPEAKER), 'Wrong voice provider')
        records = voice.get('recordings')
        require(isinstance(records,list) and len(records) == 17 and all(isinstance(r,dict) for r in records), 'Incomplete voice set')
        require(len({r.get('voice_id') for r in records}) == 17, 'Duplicate voice recordings')
        for recording in records:
            asr, audio = recording.get('asr', {}), recording.get('audio', {})
            require(isinstance(asr,dict) and asr.get('passed') is True and asr.get('polarity_counts_match') is True
                    and type(asr.get('cer')) in (int,float) and 0 <= asr['cer'] <= .2, 'Failed voice transcription')
            require(isinstance(audio,dict) and audio.get('sample_rate') == 24000 and audio.get('channels') == 1
                    and type(audio.get('frames')) is int and audio['frames'] > 0
                    and type(audio.get('peak')) in (int,float) and 0 < audio['peak'] < .99
                    and type(audio.get('rms_dbfs')) in (int,float) and -30 <= audio['rms_dbfs'] <= -18,
                    'Failed voice signal checks')
        require(publication.get('voice_generation_commit') == voice.get('producer_commit')
                and isinstance(voice.get('producer_commit'),str) and HEX40.fullmatch(voice['producer_commit']),
                'Voice production identity mismatch')
        digest = publication.get('voice_generation_sha256')
        upgrade = machine.get('voice_upgrade')
        require(isinstance(digest,str) and HEX64.fullmatch(digest)
                and isinstance(upgrade,dict) and upgrade.get('generation_sha256') == digest, 'Voice evidence binding mismatch')
        return {**selection, 'approval_mode':'user_requested_after_voice_upgrade', 'qwen_license_required':'true'}
    require(human.get("schema_version") == 1 and human.get("status") == "approved", "Human acceptance pending")
    require(human.get("version") == version and human.get("candidate_commit") == selection["candidate"], "Human acceptance targets another candidate")
    require(human.get("package_sha256") == selection["sha256"], "Human acceptance targets another ZIP")
    require(has_text(human.get("reviewer")) and has_text(human.get("reviewed_at")), "Missing human reviewer/date")
    require(human.get("unresolved_issues") == [], "Unresolved human issues")
    for group in GROUPS:
        item = human.get(group, {})
        require(isinstance(item, dict) and item.get("status") == "passed" and has_text(item.get("evidence")), f"Human {group} pending or lacks evidence")
    timing = human.get("reading_time", {})
    require(isinstance(timing, dict) and timing.get("status") == "passed" and has_text(timing.get("evidence")), "Human reading timing pending")
    for ending in ("normal", "true"):
        minutes = timing.get(f"{ending}_minutes")
        require(type(minutes) in (int, float) and math.isfinite(minutes) and 30 <= minutes <= 60,
                f"{ending} measured playtime must be 30–60 minutes; revise or record a user-approved scope change first")
    return selection


def validate_zip(path, selection):
    path = Path(path)
    require(path.name == selection["package"], "Downloaded ZIP filename mismatch")
    require(path.stat().st_size == selection["size"], "Downloaded ZIP size mismatch")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    require(digest.hexdigest() == selection["sha256"], "Downloaded ZIP differs from reviewed bytes")
    with zipfile.ZipFile(path) as archive:
        require(archive.testzip() is None, "ZIP CRC failure")
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate ZIP entries")
        roots = {name.split('/')[0] for name in names}
        require(len(roots) == 1, "Unexpected ZIP roots")
        root = next(iter(roots))
        require(f"{root}/BeforeTheRainStops.exe" in names, "Standalone EXE missing")
        for name in names:
            require(not name.startswith('/') and '..' not in name.split('/'), "Unsafe ZIP path")
            relative = name.removeprefix(root + '/')
            require(not relative.startswith(("game/data/", "game/tests/", "game/saves/", "assets_source/", "tools/", "tests/", "prompts/", ".git/")), "Authoring/private files in ZIP")
            require(not relative.startswith("game/testcases."), "Injected tests in original ZIP")
            require(not relative.endswith((".onnx", ".pt", ".pth", ".safetensors")), "Inference model in ZIP")
        info = json.loads(archive.read(f"{root}/game/cache/build_info.json"))
        require(info.get("version") == selection["version"], "ZIP build version mismatch")
        for file in ("PLAYER_README.txt", "CREDITS.md", "LICENSE", "licenses/RENPY.txt", "licenses/SourceHanSans-OFL.txt", "licenses/Kokoro-model-Apache-2.0.txt"):
            require(f"{root}/{file}" in names, f"Missing player/license file: {file}")
        if selection.get('qwen_license_required') == 'true':
            require(f'{root}/licenses/Qwen3-TTS-Apache-2.0.txt' in names, 'Missing Qwen license')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine", type=Path, default=Path("docs/evidence/v10-acceptance.json"))
    parser.add_argument("--human", type=Path, default=Path("docs/review/V10_HUMAN_ACCEPTANCE.json"))
    parser.add_argument('--authorization',type=Path,default=Path('docs/review/V10_PUBLICATION_AUTHORIZATION.json'))
    parser.add_argument('--voice',type=Path,default=Path('docs/evidence/voice-qwen-generation.json'))
    parser.add_argument("--version", required=True)
    parser.add_argument("--zip", type=Path)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        machine = json.loads(args.machine.read_text(encoding="utf-8"))
        validate_machine(machine,args.version)
        publication = json.loads(args.authorization.read_text(encoding='utf-8')) if args.authorization.exists() else None
        voice = json.loads(args.voice.read_text(encoding='utf-8')) if publication is not None else None
        selection = validate_approval(machine,
                                      json.loads(args.human.read_text(encoding="utf-8")), args.version, publication, voice)
        if publication is not None:
            require(hashlib.sha256(args.voice.read_bytes()).hexdigest() == publication['voice_generation_sha256'],
                    'Voice generation evidence bytes changed')
        if args.zip:
            validate_zip(args.zip, selection)
        if args.preview:
            shots = [s for s in machine.get("screenshots", []) if s.get("scope") == "standalone"
                     and s.get("path") == "reports/package/screenshots/native-main-menu.png"]
            require(len(shots) == 1, "Accepted main-menu preview evidence missing")
            require(args.preview.name == f"BeforeTheRainStops-{args.version}-preview.png", "Preview filename mismatch")
            require(hashlib.sha256(args.preview.read_bytes()).hexdigest() == shots[0]["sha256"], "Preview differs from accepted EXE screenshot")
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as stream:
                for key, value in selection.items():
                    stream.write(f"{key}={value}\n")
        print("Formal release acceptance passed for the exact reviewed candidate.")
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Release blocked: {exc}\n")


if __name__ == "__main__":
    main()
