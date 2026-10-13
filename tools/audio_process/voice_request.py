"""Author-only multi-character recipe exchanged with Circuit v1.2.0.

This module does not replace Rain's checked-in voice manifest or Ren'Py channel.
Original code, Copyright (c) 2026 AureliusWu, covered by the repository MIT license.
"""
import hashlib
import json
import re


def prepare_request(row, provider, source_lines):
    """Validate a proposed recording and return its complete cache fingerprint."""
    if not isinstance(row, dict) or not isinstance(provider, dict) or not isinstance(source_lines, dict):
        raise ValueError('Request, provider and source lines must be dictionaries')
    for key in ('asset_id', 'character', 'speaker', 'text', 'instruct'):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError('Missing request field: ' + key)
    for key in ('asset_id', 'character'):
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,79}', row[key]):
            raise ValueError('Unsafe identifier: ' + key)
    seed = row.get('seed')
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError('seed must be an unsigned 32-bit integer')
    ids = row.get('line_ids')
    if not isinstance(ids, list) or not ids or any(not isinstance(id, str) for id in ids) or len(set(ids)) != len(ids):
        raise ValueError('line_ids must be a nonempty unique list')
    for id in ids:
        text = source_lines.get(id)
        if not isinstance(text, str) or row['text'] not in text:
            raise ValueError('Recorded text is absent from source line: ' + id)
    for key in ('model_id', 'revision', 'dtype', 'processing', 'wrapper'):
        if not isinstance(provider.get(key), str) or not provider[key]:
            raise ValueError('Missing provider field: ' + key)
    speakers = provider.get('speaker_bank')
    if not isinstance(speakers, dict) or row['speaker'] not in speakers:
        raise ValueError('Speaker is absent from the recorded provider bank')
    # Copy every field; additional sampler or model hash fields must also invalidate cache.
    request = {'recording': json.loads(json.dumps(row)), 'provider': json.loads(json.dumps(provider))}
    payload = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    return {'request': request, 'sha256': hashlib.sha256(payload).hexdigest()}
