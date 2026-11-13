"""Offline store integrity and change preparation; no model, network or remote writes.

The assistant interprets the user, prepares a request, then conditionally publishes
the returned store using the receiving provider's revision token and reads it back.
This helper never certifies that an interpretation matches the user's intent.
"""
import argparse
import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


CLASSES = {'CURRENT_STATE', 'DECISION', 'HYPOTHESIS', 'LEARNING_CANDIDATE',
           'DOMAIN_EVENT', 'LONGITUDINAL'}
KINDS = {'user_statement', 'user_decision', 'observation',
         'assistant_proposal', 'hypothesis'}
FIELDS = {'revision', 'recorded_at', 'topic', 'title', 'aliases', 'class',
          'statement_kind', 'status', 'summary', 'details', 'source',
          'valid_until', 'uncertainty', 'decision_maker', 'authorization_source'}
OPTIONAL = {'decision_maker', 'authorization_source'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def date(value):
    require(nonempty(value), 'Date required')
    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('Invalid ISO date/time') from exc


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + '\n').encode()


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def index_for(records):
    return [dict(id=key, revision=records[key]['revisions'][-1]['revision'],
                 **{field: records[key]['revisions'][-1][field]
                    for field in ('topic', 'title', 'aliases', 'class', 'status')})
            for key in sorted(records)]


def validate(store):
    require(isinstance(store, dict), 'Store must be an object')
    require(set(store) == {'schema_version', 'store_id', 'generation', 'records', 'index'},
            'Unexpected or missing store fields')
    require(type(store['schema_version']) is int and store['schema_version'] == 1,
            'Unsupported schema')
    require(nonempty(store['store_id']) and store['store_id'] != 'UNBOUND',
            'Store must be bound to a user instance')
    require(type(store['generation']) is int and store['generation'] >= 0, 'Invalid generation')
    records = store['records']
    require(isinstance(records, dict), 'Invalid records')
    for key, record in records.items():
        require(re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,95}', key) is not None, 'Invalid stable ID')
        require(isinstance(record, dict) and set(record) == {'revisions'}, 'Invalid record')
        require(isinstance(record['revisions'], list) and record['revisions'], 'Missing history')
        for number, r in enumerate(record['revisions'], 1):
            require(isinstance(r, dict) and FIELDS - OPTIONAL <= set(r) <= FIELDS,
                    'Unexpected or missing revision fields')
            require(type(r['revision']) is int and r['revision'] == number, 'Broken revision chain')
            for field in ('topic', 'title', 'summary', 'details'):
                require(nonempty(r[field]), 'Empty ' + field)
            require(isinstance(r['uncertainty'], str), 'Invalid uncertainty')
            require(isinstance(r['aliases'], list) and all(nonempty(x) for x in r['aliases']),
                    'Invalid aliases')
            require(len(r['aliases']) == len(set(r['aliases'])), 'Duplicate aliases')
            require(r['class'] in CLASSES and r['statement_kind'] in KINDS, 'Invalid classification')
            require(r['status'] in {'active', 'withdrawn', 'archived'}, 'Invalid status')
            date(r['recorded_at'])
            if r['valid_until'] is not None:
                date(r['valid_until'])
            source = r['source']
            require(isinstance(source, dict) and set(source) == {'origin', 'reference', 'excerpt'},
                    'Source origin/reference/excerpt required')
            require(all(nonempty(source[x]) for x in source), 'Incomplete provenance')
            if r['class'] == 'DECISION':
                require(r['statement_kind'] == 'user_decision', 'Proposal is not a user decision')
                require(all(nonempty(r.get(x)) for x in OPTIONAL), 'Decision authority missing')
            if r['statement_kind'] == 'user_decision':
                require(r['class'] == 'DECISION', 'User decision requires decision record')
            if r['class'] == 'HYPOTHESIS':
                require(r['statement_kind'] in {'hypothesis', 'assistant_proposal'},
                        'Hypothesis cannot be an established decision')
    require(store['index'] == index_for(records), 'Index is stale or incomplete')
    return store


def empty(store_id):
    return validate(dict(schema_version=1, store_id=store_id, generation=0, records={}, index=[]))


def prepare(store, request, expected_digest):
    """Return a validated candidate. Publication still needs provider SHA CAS/readback."""
    validate(store)
    require(isinstance(request, dict) and set(request) == {'id', 'base_revision', 'value'},
            'Request requires id/base_revision/value')
    key = request['id']
    require(isinstance(key, str) and re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,95}', key), 'Invalid stable ID')
    require(type(request['base_revision']) is int and request['base_revision'] >= 0,
            'Invalid base revision')
    require(isinstance(request['value'], dict) and 'revision' not in request['value'],
            'Revision is assigned by helper')
    old = store['records'].get(key)
    latest = old['revisions'][-1] if old else None
    desired = dict(request['value'], revision=request['base_revision'] + 1)
    # A timeout can be retried after rereading the receiver. Exact already-received
    # intent is a no-op even though the earlier expected digest is now stale.
    if latest == desired:
        return copy.deepcopy(store), 'ALREADY_PRESENT'
    require(digest(store) == expected_digest, 'Store conflict: reread and reconcile')
    require(request['base_revision'] == (latest['revision'] if latest else 0),
            'Record conflict: reread and reconcile')
    candidate = copy.deepcopy(store)
    candidate['records'].setdefault(key, {'revisions': []})['revisions'].append(desired)
    candidate['generation'] += 1
    candidate['index'] = index_for(candidate['records'])
    validate(candidate)
    return candidate, 'PREPARED_NOT_SAVED'


def load_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init')
    init.add_argument('--store-id', required=True)
    init.add_argument('--output', required=True)
    check = commands.add_parser('validate')
    check.add_argument('store')
    change = commands.add_parser('prepare')
    change.add_argument('--store', required=True)
    change.add_argument('--request', required=True)
    change.add_argument('--expected-digest', required=True)
    change.add_argument('--output', required=True)
    args = parser.parse_args()
    if args.command == 'validate':
        store = validate(load_json(args.store))
        status = 'STRUCTURE_VALID_ONLY'
    elif args.command == 'init':
        store, status = empty(args.store_id), 'PREPARED_NOT_SAVED'
    else:
        store, status = prepare(load_json(args.store), load_json(args.request), args.expected_digest)
    if args.command != 'validate':
        # No in-place writes or overwrites. The caller publishes conditionally.
        with Path(args.output).open('xb') as output:
            output.write(encode(store))
    print(json.dumps(dict(status=status, digest=digest(store), generation=store['generation'],
                          records=len(store['records']), remote_persistence='NOT_PERFORMED',
                          semantic_accuracy='NOT_MEASURED')))


if __name__ == '__main__':
    main()
