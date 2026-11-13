"""Repository navigation, bounded reads and hygiene checks. No network or deletion.

Canonical producer: leestowell-tech/COMMAND/tools/repository_hygiene.py.
Consumer copies are derived tools, not independent authority or runtime gates.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, quote, urlsplit

GENERATED = re.compile(r"^INDEX(?:-\d+)?\.md$")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def prose(text: str) -> str:
    """Exclude fenced examples; inline code URLs can be real owner routes."""
    lines, fence = [], None
    for line in text.splitlines():
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if m:
            if fence is None: fence = (m[1][0], len(m[1]))
            elif m[1][0] == fence[0] and len(m[1]) >= fence[1]: fence = None
            continue
        if fence is None: lines.append(line)
    return "\n".join(lines)


def links(text: str) -> list[str]:
    text = prose(text)
    targets = [m[1].split(" ", 1)[0].strip("<>") for m in LINK.finditer(text)]
    # Definitions also expose references without guessing what a missing label means.
    targets += re.findall(r"^\s{0,3}\[[^\]]+\]:\s*<?([^\s>]+)", text, re.M)
    targets += [s.rstrip(".,;:") for s in re.findall(r"https?://[^\s<>`\]\)\"']+", text)]
    return sorted(set(targets))


def anchors(text: str) -> set[str]:
    slugs, counts = set(), {}
    for item in sections(text):
        slug = re.sub(r"[^\w\s-]", "", item["heading"].lower()).replace(" ", "-")
        count = counts.get(slug, 0); counts[slug] = count + 1
        slugs.add(slug + (f"-{count}" if count else ""))
    slugs.update(re.findall(r'<a\s+(?:id|name)=[\"\']([^\"\']+)', text))
    return slugs


def reference_texts(root: Path, config: dict) -> dict[str, str]:
    paths = set(config.get("entry_files", ["AGENTS.md", "README.md"]))
    paths.update(config.get("reference_files", []))
    result = {p: within(root, p).read_text() for p in sorted(paths)}
    for spec in config.get("reference_sections", []):
        matches = [h for h in sections(within(root, spec["path"]).read_text())
                   if h["heading"].casefold() == spec["heading"].casefold()]
        if len(matches) != 1: raise ValueError("CURRENT_SECTION_MISSING_OR_AMBIGUOUS:" + spec["path"])
        item = read_section(root, spec["path"], spec["heading"],
                            max_bytes=spec.get("max_bytes", 8192))
        result[spec["path"] + "#" + spec["heading"]] = item["content"]
    return result


def owned_reference(url: str, owners: list[str]) -> tuple | None:
    u = urlsplit(url)
    parts = unquote(u.path).strip("/").split("/")
    if len(parts) < 4 or parts[0].casefold() not in {o.casefold() for o in owners}:
        return None
    if u.hostname == "github.com" and parts[2] in ("blob", "tree"):
        return ("/".join(parts[:2]), "/".join(parts[3:]), unquote(u.fragment), parts[2])
    if u.hostname == "raw.githubusercontent.com":
        return ("/".join(parts[:2]), "/".join(parts[2:]), unquote(u.fragment), "blob")
    return None


def references(root: Path, config: dict, evidence: dict | None = None,
               now: datetime | None = None) -> dict:
    """Validate owned links against fresh, complete, externally acquired Git trees.

    No network or credentials. A snapshot is supplied evidence, not an authenticity
    oracle. Missing, stale, ambiguous or incomplete evidence never proves absence.
    """
    now = now or datetime.now(timezone.utc)
    failures, unknown, checked, historical = [], [], [], []
    texts = reference_texts(root, config)
    if any("\0" in t for t in texts.values()): raise ValueError("REFERENCE_SOURCE_NOT_HYDRATED")
    snapshots = (evidence or {}).get("repositories", [])
    owners = config.get("reference_owners", ["leestowell-tech"])
    for source, content in texts.items():
        for url in links(content):
            parsed = owned_reference(url, owners)
            if not parsed: continue
            repo, tail, anchor, kind = parsed
            label = source + ":" + url
            candidates = [s for s in snapshots if s.get("repository", "").casefold() == repo.casefold()
                          and tail.startswith(s.get("ref", "") + "/") and s.get("ref")]
            # Longest matching ref handles slash-containing branches without guessing.
            candidates.sort(key=lambda s: len(s["ref"]), reverse=True)
            if not candidates:
                if re.match(r"^[0-9a-fA-F]{40}(?:/|$)", tail): historical.append(label)
                else: unknown.append("SOURCE_NOT_SUPPLIED:" + label)
                continue
            s = candidates[0]
            try:
                age = (now - datetime.fromisoformat(s["observed_at"].replace("Z", "+00:00"))).total_seconds()
                valid = (0 <= age <= config.get("reference_max_age_seconds", 3600)
                         and s.get("complete") is True and re.fullmatch(r"[0-9a-f]{40}", s.get("commit", ""))
                         and isinstance(s.get("files"), dict))
                if re.fullmatch(r"[0-9a-fA-F]{40}", s["ref"]):
                    valid = valid and s["commit"].lower() == s["ref"].lower()
            except (KeyError, TypeError, ValueError): valid = False
            if not valid:
                unknown.append("SOURCE_STALE_OR_INCOMPLETE:" + label); continue
            path = tail[len(s["ref"]) + 1:]
            if ".." in Path(path).parts:
                failures.append("REFERENCE_PATH_TRAVERSAL:" + label); continue
            entry = s["files"].get(path)
            if kind == "tree":
                if not any(p.startswith(path.rstrip("/") + "/") for p in s["files"]):
                    failures.append("BROKEN_OWNED_TREE:" + label)
                else: checked.append(label)
                continue
            if not entry:
                failures.append("BROKEN_OWNED_LINK:" + label); continue
            if anchor:
                body = s.get("contents", {}).get(path)
                if not isinstance(body, str):
                    unknown.append("ANCHOR_CONTENT_NOT_SUPPLIED:" + label); continue
                raw = body.encode()
                sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                if sha != entry:
                    unknown.append("ANCHOR_CONTENT_HASH_MISMATCH:" + label); continue
                line_anchor = re.fullmatch(r"L(\d+)(?:-L(\d+))?", anchor)
                if line_anchor:
                    start, end = int(line_anchor[1]), int(line_anchor[2] or line_anchor[1])
                    anchor_valid = 1 <= start <= end <= len(body.splitlines())
                else: anchor_valid = anchor in anchors(body)
                if not anchor_valid:
                    failures.append("BROKEN_OWNED_ANCHOR:" + label); continue
            checked.append(label)
    return {"status": "FAIL" if failures else "UNVERIFIED" if unknown else "PASS",
            "failures": sorted(set(failures)), "unverified": sorted(set(unknown)),
            "checked": checked, "historical_not_checked": historical,
            "sources": sorted(texts),
            "limits": "Configured active Markdown links and owned GitHub URLs only. Immutable historical links are preserved, not certified. Other URLs, prose paths, runtime receiving and benefit need separate evidence."}


def incoming(root: Path, config: dict, targets: list[str]) -> dict:
    """Find retirement candidates throughout supplied Markdown, including history.

    A reviewer classifies each occurrence; discovery never authorizes rewriting it.
    """
    active = {p.split("#", 1)[0] for p in reference_texts(root, config)}
    hits = []
    for path in files(root):
        if not path.endswith((".md", ".md.tmpl")): continue
        text = within(root, path).read_text()
        if "\0" in text: raise ValueError("INCOMING_SOURCE_NOT_HYDRATED:" + path)
        for n, line in enumerate(text.splitlines(), 1):
            for target in targets:
                if target in unquote(line):
                    hits.append({"path": path, "line": n, "target": target,
                                 "review": "active_or_mixed" if path in active else "unclassified",
                                 "text": line[:1000]})
    return {"status": "REVIEW_REQUIRED" if hits else "NO_MATCH_IN_SUPPLIED_ROOT",
            "hits": hits, "limits": "Search every affected owner/consumer root and branch; no-match is not proof of estate-wide absence. Classify active, history, example or unverified; never rewrite history by bulk substitution."}


def files(root: Path) -> list[str]:
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=root, capture_output=True)
    if result.returncode == 0:
        return sorted(set(p for p in result.stdout.decode().split("\0") if p and (root / p).is_file()))
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*")
                  if p.is_file() and not any(a in (".git", "__pycache__") for a in p.parts))


def within(root: Path, relative: str) -> Path:
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("PATH_OUTSIDE_REPOSITORY")
    if any((root / Path(*Path(relative).parts[:i + 1])).is_symlink()
           for i in range(len(Path(relative).parts))):
        raise ValueError("SYMLINK_REQUIRES_REVIEW")
    if not path.is_file():
        raise ValueError("MISSING_FILE:" + relative)
    return path


def sections(text: str) -> list[dict]:
    lines = text.splitlines(keepends=True)
    headings = []
    fenced = False
    fence = ""
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        m = re.match(r"(`{3,}|~{3,})", stripped)
        if m:
            token = m.group(1)[0]
            if not fenced:
                fenced, fence = True, token
            elif token == fence:
                fenced = False
            continue
        if fenced:
            continue
        m = HEADING.match(line.rstrip("\r\n"))
        if m:
            headings.append({"heading": m.group(2), "level": len(m.group(1)), "start": i})
    for n, heading in enumerate(headings):
        heading["end"] = next((h["start"] for h in headings[n + 1:] if h["level"] <= heading["level"]), len(lines))
        heading["bytes"] = len("".join(lines[heading["start"]:heading["end"]]).encode())
        heading["line"] = heading["start"] + 1
    return headings


def read_section(root: Path, path: str, heading: str, occurrence: int = 1, max_bytes: int = 24576) -> dict:
    raw = within(root, path).read_bytes()
    text = raw.decode("utf-8")
    matches = [h for h in sections(text) if h["heading"].casefold() == heading.casefold()]
    if occurrence < 1 or occurrence > len(matches):
        raise ValueError("HEADING_NOT_FOUND_OR_OCCURRENCE_INVALID")
    h = matches[occurrence - 1]
    if h["bytes"] > max_bytes:
        children = [a["heading"] for a in sections(text)
                    if h["start"] < a["start"] < h["end"]][:30]
        raise ValueError("SECTION_EXCEEDS_READ_BUDGET:" + json.dumps({"bytes": h["bytes"], "children": children}))
    content = "".join(text.splitlines(keepends=True)[h["start"]:h["end"]])
    source_sha256 = hashlib.sha256(raw).hexdigest()
    # Backward compatibility: sha256 has always identified the complete source,
    # while bytes/content describe only the selected section. Name both objects.
    return {"path": path, "sha256": source_sha256, "sha256_scope": "whole_source_file",
            "source_sha256": source_sha256, "source_bytes": len(raw), "line": h["line"],
            "bytes": h["bytes"], "content_bytes": len(content.encode("utf-8")),
            "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "selection": {"kind": "heading_section", "heading": h["heading"],
                          "occurrence": occurrence},
            "content": content}


def navigation(root: Path, config: dict) -> dict[str, str]:
    all_files = [p for p in files(root) if not GENERATED.match(Path(p).name)]
    outputs = {}
    for navroot in config.get("navigation_roots", ["docs"]):
        members = [p for p in all_files if p.startswith(navroot.rstrip("/") + "/")]
        if not members:
            continue
        directories = {navroot}
        for p in members:
            parent = Path(p).parent
            while parent.as_posix().startswith(navroot):
                directories.add(parent.as_posix())
                if parent.as_posix() == navroot:
                    break
                parent = parent.parent
        for directory in sorted(directories):
            direct = [p for p in members if Path(p).parent.as_posix() == directory]
            children = sorted(d for d in directories if Path(d).parent.as_posix() == directory)
            rows = []
            for child in children:
                name = Path(child).name
                rows.append(f"- [{name}/]({quote(name)}/INDEX.md) — folder index")
            for p in direct:
                name = Path(p).name
                rows.append(f"- [{name}]({quote(name)})")
            pages = [rows[n:n + 60] for n in range(0, len(rows), 60)] or [[]]
            for n, rows_page in enumerate(pages, 1):
                filename = "INDEX.md" if n == 1 else f"INDEX-{n}.md"
                body = f"# {directory} — navigation\n\n"
                body += "Generated from repository paths; this is navigation, not a status or authority register. Read the current controlling record before acting. Historical evidence retains its original scope.\n\n"
                body += "\n".join(rows_page) + "\n"
                if len(pages) > 1:
                    body += "\nPages: " + " · ".join(f"[{j}]({'INDEX.md' if j == 1 else f'INDEX-{j}.md'})" for j in range(1, len(pages) + 1)) + "\n"
                body += "\nRefresh with `python3 tools/repository_hygiene.py generate`.\n"
                outputs[directory + "/" + filename] = body
    return outputs


def local_link_failures(root: Path, path: str, text: str) -> list[str]:
    failures = []
    for target in links(text):
        if path.endswith('.md.tmpl') and re.fullmatch(r'\$\{[A-Za-z_][A-Za-z0-9_]*\}', target):
            continue  # Creator tests validate the substituted destination, not this parameter.
        if not target or re.match(r"^[a-zA-Z][\w+.-]*:", target):
            continue
        target, _, anchor = target.partition("#")
        target = unquote(target)
        anchor = unquote(anchor)
        if not target:
            destination = root / path
        else:
            destination = (root / Path(path).parent / target).resolve()
        if not destination.is_relative_to(root.resolve()):
            failures.append("LINK_OUTSIDE_REPOSITORY:" + path + ":" + target)
        elif not destination.exists():
            failures.append("BROKEN_LOCAL_LINK:" + path + ":" + target)
        elif anchor and destination.is_file() and destination.suffix.lower() == ".md":
            content = destination.read_text()
            if anchor not in anchors(content):
                failures.append("BROKEN_LOCAL_ANCHOR:" + path + ":" + target + "#" + anchor)
    return failures


def workflow_economy(root: Path, config: dict) -> dict:
    """Conservative source checks for ordinary block-style Actions workflows.

    This is not a YAML interpreter, billing interlock or proof of useful tests.
    Unsupported structural forms fail for review rather than passing silently.
    Literal script bodies are excluded so shell examples cannot impersonate YAML.
    """
    failures, checked = [], []
    max_runtime = config.get('workflow_max_timeout_minutes', 45)
    max_retention = config.get('workflow_max_retention_days', 14)
    allowed = config.get('workflow_allowed_runners', ['ubuntu-latest', 'ubuntu-24.04'])
    for path in files(root):
        if not re.fullmatch(r'\.github/workflows/[^/]+\.ya?ml', path):
            continue
        text = within(root, path).read_text()
        def fail(code): failures.append(code + ':' + path)
        prefix = []
        for line in text.splitlines():
            if line.strip() and not line.lstrip().startswith('#'): break
            prefix.append(line)
        header = '\n'.join(prefix)
        for field in ('owner', 'purpose'):
            if not re.search(r'^# Workflow ' + field + r':\s*\S.+$', header, re.M):
                fail('WORKFLOW_MISSING_' + field.upper())
        records, block = [], None
        for raw in text.splitlines():
            if not raw.strip() or raw.lstrip().startswith('#'): continue
            indent = len(raw) - len(raw.lstrip(' '))
            if block is not None and indent > block: continue
            block = None
            if '\t' in raw[:len(raw)-len(raw.lstrip())]: fail('WORKFLOW_UNSUPPORTED_INDENT')
            value = raw.strip()
            if re.search(r':\s*[>|][+-]?\s*(?:#.*)?$', value): block = indent
            if re.search(r':\s*[&*][\w-]+|^<<\s*:|^---', value): fail('WORKFLOW_UNSUPPORTED_YAML')
            records.append((indent, value))
        top = [(i, s) for i, s in records if i == 0]
        triggers = []
        on_indexes = [n for n, (i, s) in enumerate(records) if i == 0 and re.match(r"^(?:on|'on'|\"on\")\s*:", s)]
        if len(on_indexes) != 1: fail('WORKFLOW_TRIGGER_REVIEW_REQUIRED')
        else:
            n = on_indexes[0]; value = records[n][1].split(':', 1)[1].strip()
            if value:
                if re.fullmatch(r'\[[\w\s,\'\"-]+\]', value):
                    triggers = re.findall(r'[a-zA-Z_][\w-]*', value)
                else: fail('WORKFLOW_TRIGGER_REVIEW_REQUIRED')
            else:
                for i, s in records[n+1:]:
                    if i == 0: break
                    if i == 2:
                        m = re.fullmatch(r'([a-zA-Z_][\w-]*):(?:\s*\{\})?', s)
                        if m: triggers.append(m[1])
                        else: fail('WORKFLOW_TRIGGER_REVIEW_REQUIRED')
        if not triggers: fail('WORKFLOW_TRIGGER_REVIEW_REQUIRED')
        automatic = any(t != 'workflow_dispatch' for t in triggers)
        if automatic:
            if not re.search(r'^# Automatic trigger reason:\s*\S.+$', header, re.M):
                fail('WORKFLOW_AUTOMATIC_REASON_MISSING')
            cn = next((n for n, (i, s) in enumerate(records) if i == 0 and s == 'concurrency:'), None)
            concurrency = []
            if cn is not None:
                for i, s in records[cn+1:]:
                    if i == 0: break
                    concurrency.append((i,s))
            if not any(i == 2 and s.startswith('group:') and s.split(':',1)[1].strip() for i,s in concurrency) or (2,'cancel-in-progress: true') not in concurrency:
                fail('WORKFLOW_AUTOMATIC_CONCURRENCY_MISSING')
        jobs_start = next((n for n,(i,s) in enumerate(records) if i == 0 and s == 'jobs:'), None)
        jobs = []
        if jobs_start is not None:
            for n in range(jobs_start+1, len(records)):
                i,s=records[n]
                if i == 0: break
                if i == 2:
                    if re.fullmatch(r'[\w-]+:', s): jobs.append(n)
                    else: fail('WORKFLOW_JOB_REVIEW_REQUIRED')
        if not jobs: fail('WORKFLOW_JOB_REVIEW_REQUIRED')
        if len({records[n][1] for n in jobs}) != len(jobs): fail('WORKFLOW_DUPLICATE_JOB_FIELD')
        uploads = 0
        for k,n in enumerate(jobs):
            end = jobs[k+1] if k+1 < len(jobs) else next((j for j in range(n+1,len(records)) if records[j][0] == 0),len(records))
            body=records[n+1:end]
            fields={}
            for i,s in body:
                if i == 4 and ':' in s:
                    key,val=s.split(':',1)
                    if key in fields: fail('WORKFLOW_DUPLICATE_JOB_FIELD')
                    fields[key]=val.strip()
            timeout=fields.get('timeout-minutes','')
            if not timeout.isdigit() or not 1 <= int(timeout) <= max_runtime: fail('WORKFLOW_RUNTIME_UNBOUNDED')
            if fields.get('runs-on','').strip('\'\"') not in allowed: fail('WORKFLOW_RUNNER_REVIEW_REQUIRED')
            if fields.get('steps') != '': fail('WORKFLOW_STEP_REVIEW_REQUIRED')
            if any(i != 6 and s.startswith('- ') for i,s in body): fail('WORKFLOW_STEP_REVIEW_REQUIRED')
            step_starts=[j for j,(i,s) in enumerate(body) if i == 6 and s.startswith('- ')]
            for k,j in enumerate(step_starts):
                step=body[j:step_starts[k+1] if k+1<len(step_starts) else len(body)]
                if step[0][1].startswith('- {'): fail('WORKFLOW_STEP_REVIEW_REQUIRED')
                upload=any(i in (6,8) and re.match(r"^(?:-\s*)?(?:uses|'uses'|\"uses\")\s*:\s*['\"]?actions/upload-artifact@",s) for i,s in step)
                if not upload: continue
                uploads += 1
                retention=[s.split(':',1)[1].strip() for i,s in step if i == 10 and re.match(r"^(?:retention-days|'retention-days'|\"retention-days\")\s*:",s)]
                if len(retention)!=1 or not retention[0].isdigit() or not 1 <= int(retention[0]) <= max_retention:
                    fail('WORKFLOW_ARTIFACT_RETENTION_UNBOUNDED')
        checked.append({'path':path,'triggers':triggers,'jobs':len(jobs),'artifact_uploads':uploads})
    return {'failures':sorted(set(failures)), 'workflows':checked,
            'limits':'Conservative block-style source checks; scripts, reusable workflows, alternate branches, external providers and actual billing require separate review.'}


def state_consistency(root: Path, config: dict) -> dict:
    """Detect unreviewed owner changes and explicit freshness/status conflicts.

    Pins bind a consumer review to exact owner-section bytes. They are never
    refreshed by generate: matching bytes do not prove semantic correctness.
    """
    failures, checked = [], []

    def selected(spec):
        text = within(root, spec['path']).read_text()
        matches = [s for s in sections(text)
                   if s['heading'].casefold() == spec['heading'].casefold()]
        if len(matches) != 1:
            raise ValueError('STATE_SECTION_MISSING_OR_AMBIGUOUS:' + spec['path'] + '#' + spec['heading'])
        return read_section(root, spec['path'], spec['heading'],
                            max_bytes=spec.get('max_bytes', 24576))['content']

    for rule in config.get('state_projections', []):
        try:
            owner = selected(rule['owner'])
            digest = hashlib.sha256(owner.encode('utf-8')).hexdigest()
            for consumer in rule['consumers']:
                label = rule['id'] + ':' + consumer['path'] + '#' + consumer['heading']
                content = selected(consumer)
                pins = re.findall(r'<!-- state-review: ' + re.escape(rule['id'])
                                  + r' sha256=([0-9a-f]{64}) -->', content)
                if len(pins) != 1 or pins[0] != digest:
                    failures.append('STATE_REVIEW_REQUIRED:' + label)
                failures.extend(local_link_failures(root, consumer['path'], content))
                checked.append(label)
        except (OSError, ValueError, UnicodeError) as e:
            failures.append('STATE_SOURCE_READ_FAILED:' + str(e))

    for spec in config.get('state_freshness_checks', []):
        try:
            content = selected(spec)
            statuses = re.findall(r'^- Status:\s*(.+)$', content, re.M)
            label = spec['path'] + '#' + spec['heading']
            if len(statuses) != 1:
                failures.append('STATE_STATUS_MISSING_OR_AMBIGUOUS:' + label)
                continue
            tokens = {re.sub(r'[\s-]+', '_', token.strip().rstrip('.!').upper())
                      for token in statuses[0].split('/')}
            unknown = bool(tokens & {'SOURCE_AGE_UNKNOWN', 'SOURCE_FRESHNESS_UNKNOWN'})
            current = bool(tokens & {'IMMEDIATE_FLOOR_BREACH', 'CURRENT_VERIFIED', 'CURRENT_SNAPSHOT'})
            if unknown and current:
                failures.append('STATE_FRESHNESS_CONTRADICTION:' + label)
            checked.append(label)
        except (OSError, ValueError, UnicodeError) as e:
            failures.append('STATE_SOURCE_READ_FAILED:' + str(e))
    return {'failures': sorted(set(failures)), 'checked': checked,
            'limits': 'Configured owner/consumer sections and explicit status tokens only. '
                      'Pins require human/assistant meaning review; neither matching pins nor this check prove live source freshness.'}


def audit(root: Path, config: dict) -> dict:
    failures = []
    inventory = files(root)
    metrics = {}
    for path in config.get("entry_files", ["AGENTS.md", "README.md"]):
        try:
            raw = within(root, path).read_bytes()
        except ValueError as e:
            failures.append(str(e)); continue
        limit = config.get("entry_budgets", {}).get(path, 8192)
        metrics[path] = {"bytes": len(raw), "limit": limit}
        if len(raw) > limit:
            failures.append("ENTRY_BUDGET_EXCEEDED:" + path)
        failures += local_link_failures(root, path, raw.decode())
    # A route disappearing from an entry is detectable locally. This does not
    # certify instruction loading, correct behavior or the receiver's outcome.
    for path, routes in config.get("required_entry_routes", {}).items():
        try:
            text = within(root, path).read_text()
            text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
            destinations = set(re.findall(r"\]\(([^\s)]+)\)", text))
            for route in routes:
                if route not in destinations:
                    failures.append("REQUIRED_ENTRY_ROUTE_MISSING:" + path + ":" + route)
        except (ValueError, OSError, UnicodeError) as e:
            failures.append("REQUIRED_ENTRY_READ_FAILED:" + path + ":" + str(e))
    for path in inventory:
        if Path(path).name in ("AGENTS.md", "AGENTS.override.md"):
            if len((root / path).read_bytes()) > config.get("nested_agent_budget", 8192):
                failures.append("AGENT_BUDGET_EXCEEDED:" + path)
            if Path(path).name == 'AGENTS.override.md' and path not in config.get('reviewed_overrides', []):
                failures.append('UNREVIEWED_ENTRY_OVERRIDE:' + path)
    # Model the default root-to-leaf project instruction chain. Actual host/global
    # configuration and custom fallback names still require separate receiving.
    agent_dirs = {Path(p).parent for p in inventory if Path(p).name in ('AGENTS.md', 'AGENTS.override.md')}
    for directory in agent_dirs:
        chain = list(reversed(directory.parents)) + [directory]
        total = 0
        for ancestor in chain:
            candidates = [ancestor / 'AGENTS.override.md', ancestor / 'AGENTS.md']
            selected = next((p for p in candidates if p.as_posix() in inventory), None)
            if selected is not None: total += len((root / selected).read_bytes())
        if total > config.get('project_agent_chain_budget', 32768):
            failures.append('PROJECT_AGENT_CHAIN_BUDGET_EXCEEDED:' + directory.as_posix())
    for path in config.get("scoped_records", []):
        if path not in inventory:
            failures.append("MISSING_SCOPED_RECORD:" + path)
        else:
            limit = config.get("scoped_record_budgets", {}).get(path)
            size = len((root / path).read_bytes())
            if limit is not None and size > limit:
                failures.append("SCOPED_RECORD_GROWTH_EXCEEDED:" + path)
    try:
        for source, content in reference_texts(root, config).items():
            if "\0" in content: raise ValueError("REFERENCE_SOURCE_NOT_HYDRATED:" + source)
            failures += local_link_failures(root, source.split("#", 1)[0], content)
    except (OSError, ValueError, UnicodeError) as e:
        failures.append("ACTIVE_REFERENCE_READ_FAILED:" + str(e))
    expected = navigation(root, config)
    for path, content in expected.items():
        actual = root / path
        if not actual.is_file() or actual.read_text() != content:
            failures.append("NAVIGATION_STALE_OR_MISSING:" + path)
        else:
            failures += local_link_failures(root, path, content)
    generated_actual = {p for p in inventory if GENERATED.match(Path(p).name)
                        and any(p.startswith(r + "/") for r in config.get("navigation_roots", ["docs"]))
                        and "Generated from repository paths;" in (root / p).read_text(errors="replace")}
    for path in generated_actual - expected.keys():
        failures.append("OBSOLETE_GENERATED_INDEX:" + path)
    for path in inventory:
        if (re.match(r"^(debug|tmp|scratch)/", path) or
            re.match(r"^debug_.*\.(gd|py|js|log)$", path) or re.match(r"^[^/]+\.log$", path)):
            if path not in config.get("retained_diagnostics", []):
                failures.append("UNOWNED_TRANSIENT_ARTIFACT:" + path)
    for path in config.get('retired_executable_paths', []):
        if (root / path).exists(): failures.append('RETIRED_EXECUTABLE_REINTRODUCED:' + path)
    source = config.get("derived_checker_sha256")
    if source and hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != source:
        failures.append("DERIVED_CHECKER_DRIFT")
    economy = workflow_economy(root, config)
    failures.extend(economy['failures'])
    state = state_consistency(root, config)
    failures.extend(state['failures'])
    return {"status": "PASS" if not failures else "FAIL", "failures": sorted(set(failures)),
            "entries": metrics, "navigation_files": len(expected),
            "workflow_economy": economy,
            "state_consistency": state,
            "owned_references": "UNVERIFIED: run references with fresh source evidence for active-route changes and source migrations",
            "limits": "Structural and navigation evidence only; host loading, semantic correctness, gameplay and human acceptance are separate."}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("operation", choices=("audit", "generate", "headings", "read", "references", "incoming"))
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--config", default="tools/repository_hygiene.json")
    p.add_argument("--path")
    p.add_argument("--heading")
    p.add_argument("--search", default="")
    p.add_argument("--occurrence", type=int, default=1)
    p.add_argument("--max-bytes", type=int, default=24576)
    p.add_argument("--sources", type=Path, help="Fresh Git tree evidence JSON; see repository-upkeep.md")
    p.add_argument("--retired-target", action="append", default=[], help="Exact old path to find in every Markdown source")
    a = p.parse_args(argv)
    root = a.root.resolve()
    try:
        if a.operation in ("headings", "read"):
            if not a.path:
                p.error("headings/read requires --path")
            if a.operation == "read":
                if not a.heading:
                    p.error("read requires an exact --heading; discover with headings --search")
                result = read_section(root, a.path, a.heading, a.occurrence, a.max_bytes)
            else:
                raw = within(root, a.path).read_bytes()
                matches = [h for h in sections(raw.decode()) if a.search.casefold() in h["heading"].casefold()]
                result = {"path": a.path, "sha256": hashlib.sha256(raw).hexdigest(),
                          "match_count": len(matches), "headings": matches[:50],
                          "truncated": len(matches) > 50}
            print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
        config = json.loads(within(root, a.config).read_text())
        if a.operation == "incoming":
            if not a.retired_target: p.error("incoming requires --retired-target")
            result = incoming(root, config, a.retired_target)
            print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
        if a.operation == "references":
            evidence = json.loads(a.sources.read_text()) if a.sources else None
            result = references(root, config, evidence)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return {"PASS": 0, "FAIL": 1, "UNVERIFIED": 2}[result["status"]]
        if a.operation == "generate":
            outputs = navigation(root, config)
            for path, content in outputs.items():
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_text(content)
            print(json.dumps({"generated": len(outputs)})); return 0
        result = audit(root, config)
        if a.sources:
            result['owned_references'] = references(root, config, json.loads(a.sources.read_text()))
            result['failures'] += result['owned_references']['failures']
            result['failures'] += result['owned_references']['unverified']
            if result['status'] == 'PASS': result['status'] = result['owned_references']['status']
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return {"PASS": 0, "FAIL": 1, "UNVERIFIED": 2}[result["status"]]
    except (OSError, ValueError, UnicodeError) as e:
        print(json.dumps({"status": "FAIL", "error": str(e)})); return 1


if __name__ == "__main__":
    raise SystemExit(main())
