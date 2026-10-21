"""Stable identities for native read records; no story or save mutation."""
import math
import time
from replay_search import normalize_history_text
SPEAKERS = {'n': '旁白', 'h': '许澄', 'p': '我'}


def make_catalog(story, voices):
    voice_map = {voice['voice_id']: voice for voice in voices}
    by_line = {voice['line_id']: voice for voice in voices}
    chapters = {chapter['id']: chapter['title'] for chapter in story['chapters']}
    catalog = {}
    for node in story['nodes']:
        lines = list(node.get('lines', []))
        for choice in node.get('choices', []):
            lines.extend(choice.get('response', []))
        for line in lines:
            voice = voice_map.get(line.get('voice')) or by_line.get(line['id'], {})
            catalog[line['id']] = dict(id=line['id'], chapter=node['chapter'], chapter_title=chapters[node['chapter']],
                speaker=SPEAKERS[line['speaker']], text=line['text'], voice=voice.get('file'), voice_tag=None)
    return catalog


def identify(entry, catalog, plain=lambda value: value):
    who, what = plain(entry.who or '旁白'), plain(entry.what)
    identity = getattr(entry, 'rain_line_id', None)
    if identity:
        record = catalog.get(identity)
        return identity if record and record['speaker'] == who and record['text'] == what else None
    # Old saves lack a stable ID. Accept only a unique exact speaker/text pair.
    matches = [key for key, record in catalog.items() if record['speaker'] == who and record['text'] == what]
    return matches[0] if len(matches) == 1 else None


def clean_records(value, catalog):
    # Keep deletion timestamps too: unioning simple ID lists resurrects removed
    # bookmarks, while Ren'Py's default field merge loses an older imported list
    # to a freshly initialized empty list on the destination device.
    if isinstance(value, (list, tuple)):
        return {key: [True, 0.0] for key in value if isinstance(key, str) and key in catalog}
    if not isinstance(value, dict): return {}
    return {key: [record[0], float(record[1])] for key, record in value.items()
        if isinstance(key, str) and key in catalog and isinstance(record, (list, tuple)) and len(record) == 2
        and type(record[0]) is bool and type(record[1]) in (int, float) and math.isfinite(record[1]) and record[1] >= 0}


def clean_ids(value, catalog):
    return [key for key, record in clean_records(value, catalog).items() if record[0]]


def merge(old, new, catalog):
    records = clean_records(old, catalog)
    for key, record in clean_records(new, catalog).items():
        previous = records.get(key)
        if previous is None or record[1] > previous[1] or (record[1] == previous[1] and not record[0]):
            records[key] = record
    return records


def toggle(value, identity, history, catalog, plain=lambda value: value, now=None):
    records = clean_records(value, catalog)
    active = identity in records and records[identity][0]
    if identity not in catalog or (not active and not any(identify(entry, catalog, plain) == identity for entry in history)):
        return records
    timestamp = time.time() if now is None else now
    records[identity] = [not active, max(timestamp, records.get(identity, [False, 0.0])[1] + 0.000001)]
    return records


def bookmark_rows(value, catalog, chapter='', query='', speaker=''):
    terms = normalize_history_text(query).split()
    return [catalog[key] for key in clean_ids(value, catalog)
        if (not chapter or catalog[key]['chapter'] == chapter)
        and (not speaker or catalog[key]['speaker'] == speaker)
        and all(term in normalize_history_text(catalog[key]['speaker'] + ' ' + catalog[key]['text']) for term in terms)]
