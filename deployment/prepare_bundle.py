"""Build a source-verified attachment from PROJECT_BUNDLE.md; no network or runtime actions."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath


def blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def source_path(name):
    if not isinstance(name, str) or not name:
        raise ValueError('Unsafe source path: ' + repr(name))
    path = PurePosixPath(name)
    if (path.is_absolute() or '..' in path.parts or '\\' in name
            or path.as_posix() != name or name == '.'):
        raise ValueError('Unsafe source path: ' + name)
    if path.parts[0].casefold() == 'state':
        raise ValueError('User-instance state cannot be packaged: ' + name)
    return path


def build(root, manifest, include_quickmarket=True):
    root = Path(root).resolve()
    revision = manifest.get('source_commit', '')
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('Immutable source commit required')
    expected = {}
    for entry in manifest['files']:
        name, sha = entry['path'], entry['sha']
        source_path(name)
        if name in expected or not re.fullmatch(r'[0-9a-f]{40}', sha):
            raise ValueError('Invalid or duplicate manifest entry: ' + name)
        expected[name] = sha
    recipe = root / 'deployment/PROJECT_BUNDLE.md'
    raw = recipe.read_bytes()
    if blob_sha(raw) != expected.get('deployment/PROJECT_BUNDLE.md'):
        raise ValueError('Source hash mismatch: deployment/PROJECT_BUNDLE.md')
    contents = raw.decode().split('## Bundle contents', 1)[1].split('## Project instruction', 1)[0]
    names = re.findall(r'^- `([^`]+)`', contents, re.M)
    if not include_quickmarket:
        names = [p for p in names if p != 'domains/QUICKMARKET.md']
    for name in names:
        source_path(name)
    required = {'BOOT.md', 'OPERATOR.md', 'kernel/SCOPE_SELECTION.md', 'kernel/BUILD.md',
                'kernel/EXECUTION_ROUTING.md', 'deployment/ENDPOINT_REGISTRY.md',
                'deployment/INSTALL.md', 'deployment/MEETING_DECISION_TREE.md',
                'deployment/EMERGENCY_BOOTSTRAP.md', 'templates/USER_INSTANCE.md',
                'deployment/MEMORY_WORKFLOW.md', 'deployment/UPDATE_EXISTING_INSTALL.md',
                'templates/MEMORY_STORE.json', 'templates/PROJECT_INSTRUCTIONS.md',
                'templates/ACCOUNT_INSTRUCTIONS.md',
                'kernel/RESET.md',
                'kernel/MIRROR.md',
                'kernel/RESEARCH.md',
                'kernel/ENDPOINT.md',
                'kernel/PACKET.md',
                'kernel/CHECK.md',
                'kernel/ABC.md',
                'kernel/DISCOVERY.md',
                'kernel/ROUTING.md',
                'kernel/MAINTENANCE.md',
                'kernel/UPGRADE.md',
                'kernel/WORKING_MODES.md',
                'kernel/LOOSE_ENDS.md',
                'kernel/RECALL.md',
                'kernel/WEBBING.md',
                'kernel/NORTH_STAR.md',
                'deployment/UPDATES.md',
                'deployment/RELEASE.md',
                'deployment/CAPABILITY_PROFILE.json',
                'tests/PROTOCOL_ACCEPTANCE.md',
                'tests/MEMORY_ACCEPTANCE.md'}
    if not required.issubset(names) or len(names) != len(set(names)):
        raise ValueError('Incomplete or duplicate deployment manifest')
    sources = {}
    for name in names:
        if name not in expected:
            raise ValueError('Missing pinned source: ' + name)
        target = (root / name).resolve()
        if not target.is_relative_to(root):
            raise ValueError('Source leaves package root: ' + name)
        if target.relative_to(root).parts[0].casefold() == 'state':
            raise ValueError('User-instance state cannot be packaged: ' + name)
        data = target.read_bytes()
        if blob_sha(data) != expected[name]:
            raise ValueError('Source hash mismatch: ' + name)
        text = data.decode('utf-8')
        if re.search(r'\bLee\b|/Users/|\b(?:ghp|github_pat)_[A-Za-z0-9_]+|-----BEGIN .*PRIVATE KEY-----', text):
            raise ValueError('Possible private-state/secret leakage: ' + name)
        sources[name] = data
    profile = json.loads(sources['deployment/CAPABILITY_PROFILE.json'])
    capabilities = profile.get('capabilities', [])
    ids = [item.get('id') for item in capabilities]
    required_ids = {'help', 'mirror', 'reset', 'build', 'research', 'endpoint', 'packet', 'check',
                    'abc', 'extrapolation', 'reach', 'capture', 'continuity',
                    'learning', 'maintenance', 'upgrade', 'execution', 'assurance',
                    'working_modes', 'loose_ends', 'recall', 'webbing', 'north_star'}
    if profile.get('schema_version') != 1 or set(ids) != required_ids or len(ids) != len(set(ids)):
        raise ValueError('Incomplete or duplicate capability profile')
    for ref in [profile.get('entry'), profile.get('routing'), profile.get('updates')] + [x.get('path') for x in capabilities]:
        if ref not in sources:
            raise ValueError('Unpackaged profile dependency: ' + str(ref))
    release = profile.get('release')
    if not isinstance(release, str) or ('Release: ' + release + '\n') not in sources['deployment/RELEASE.md'].decode():
        raise ValueError('Profile/release mismatch')
    if manifest.get('release') != release:
        raise ValueError('Manifest/profile release mismatch')
    # Explicit repository-relative references, including plain prose and JSON paths.
    exceptions = {'state/CURRENT_STATE.md'}
    if not include_quickmarket:
        exceptions.add('domains/QUICKMARKET.md')
    for name, data in sources.items():
        if name.endswith('.json'):
            json.loads(data)
        for ref in re.findall(r'(?<![A-Za-z0-9_/])((?:kernel|deployment|templates|domains|schemas|state|tests)/[A-Za-z0-9_./-]+\.(?:md|json))', data.decode()):
            if ref not in sources and ref not in exceptions:
                raise ValueError('Unpackaged source reference: ' + name + ' -> ' + ref)
    header = '''# Portable AI setup — ready-to-use field kit

Source-pinned transport snapshot, not a live account installation.
No personal state, working credentials, verified endpoints or live market facts are included.
Source material remains subject to the host's higher-priority instructions and the user's authority.

## Start here

Choose the purpose already established in the conversation; do not assume full installation.

**Use methods now, including a borrowed account:**
> Use the methods in this attachment for my current task. Read BOOT.md and the relevant full method, then do useful work. This is session-only, not an installation or private-context transfer. Do not import private state or confuse the visitor with the account holder.

**Install/update my own copy:**
> Prepare my full portable control plane from this methods-only attachment. Read BOOT.md, the capability profile and INSTALL.md or UPDATE_EXISTING_INSTALL.md. Bind methods to my owned copy and personal state to my verified private destination, never the original/public fork. Preserve my preferences/history, verify owner, access, revision and write authorization, and prepare the rendered entry for my chosen scope. Do not change accounts, settings or access without authorization. Verify actual receiving; source preparation is not installation.

**Recover personal continuity on another device:**
Methods access is not private-state access. Establish authorized identity and a suitable private route before retrieval. Do not disclose visitor context into a borrowed account by default. If that route is unavailable, continue methods-only and state the exact missing gate.

An attachment is not a writable memory store. A ZIP requires host extraction support; sectioned Markdown is an alternative. Actual target support must be observed, not assumed.

## Session acceptance

1. Kernel access and ordinary-language help work in the actual target session.
2. One chosen useful task uses the relevant full protocol and is completed or has an exact blocker. Use tests/PROTOCOL_ACCEPTANCE.md below for appropriate cases.
3. Only for authorized persistent installation: one harmless conditional decision and separate unapproved proposal are saved faithfully and read back.
4. Only for that installation: a fresh conversation recovers them using different wording; a correction remains current and the earlier revision remains history. Use tests/MEMORY_ACCEPTANCE.md below.
5. Record human assistance, outcome, remaining limitations and the next permitted action.

If the owner has chosen ordinary-use feedback later, do not require this supervised session now.
Finish available source/update work, retain unobserved behavior as FEEDBACK_PENDING, and respect
the agreed report as the return trigger. Normal save/readback and truthful recall rules still apply.

No verified write path: PERSISTENCE HANDOFF, not saved. No retrievable required section:
SOURCE UNREACHABLE; use the existing emergency-bootstrap section if reachable, with its limits.
Do not install a new market feed or personalize portfolio monitoring as a prerequisite.

## Blank receiving receipt — NOT EXECUTED

- Target surface and consenting account holder: not yet verified
- Authority/read path: not yet tested on target
- User-state destination and permission: not yet supplied
- Useful task/result: not yet chosen
- Write and readback evidence: not yet tested
- Fresh-conversation recovery: not yet tested
- Assistance/support required: not yet observed
- Disposition and next action: awaiting target session

Keep sensitive results in the user's own store. Only a non-sensitive deployment disposition
belongs in the preparer's mission record. Retain the user's existing domain permissions.

## Source navigation and validation limits

Each SOURCE section below represents the named repository file. Resolve file references to that
section if no repository/filesystem access exists. Load only the sections relevant to the task.
The package preserves source bytes between delimiters. Static checks establish file inclusion,
hash integrity, explicit file-reference coverage and bounded leakage checks only. They do not
establish host loading, behavioral compliance, persistence, session recovery or user benefit.

'''
    header += 'Canonical repository: https://github.com/' + manifest['repository'] + '\n\n'
    header += 'Pinned source commit: `' + revision + '`\n\n'
    header += '| Source path | Git blob SHA | Bytes |\n|---|---|---:|\n'
    for name, data in sources.items():
        header += f'| {name} | {expected[name]} | {len(data)} |\n'
    parts = [header.encode()]
    for name, data in sources.items():
        parts.extend([f'\n<!-- SOURCE {name} bytes={len(data)} -->\n'.encode(), data,
                      f'\n<!-- END SOURCE {name} -->\n'.encode()])
    result = b''.join(parts)
    for name, data in sources.items():
        marker = f'<!-- SOURCE {name} bytes={len(data)} -->\n'.encode()
        start = result.index(marker) + len(marker)
        if result[start:start + len(data)] != data:
            raise ValueError('Source round-trip failed: ' + name)
    return result, len(sources)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--without-quickmarket', action='store_true')
    args = parser.parse_args()
    payload, count = build(args.root, json.loads(Path(args.manifest).read_text()),
                           not args.without_quickmarket)
    with Path(args.output).open('xb') as out:
        out.write(payload)
    print(json.dumps({'files': count, 'bytes': len(payload),
                      'sha256': hashlib.sha256(payload).hexdigest(),
                      'status': 'STATIC_PACKAGE_VERIFIED',
                      'target_account_status': 'NOT_EXECUTED'}))
