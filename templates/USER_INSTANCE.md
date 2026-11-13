# User Instance Template

Status: TEMPLATE

## Identity / operating preferences
Keep only information that materially improves operation. Do not infer sensitive traits or copy another user's state.

## CURRENT_STATE
- Current objectives:
- Active commitments:
- Waiting / blockers:
- Important near-term dates:
- Cross-domain risks:
- Next safe actions:
- Confidence / source gaps:

## Preferences
- Communication / decision style:
- Attention or bandwidth constraints:
- Default authority preferences:
- Privacy / retention preferences:

## Active domains
For each domain record:
- name;
- durable source / repository;
- authority boundary;
- current-state source;
- write/action capability;
- escalation conditions.

## Memory rule
Personal state is not kernel authority. Time-sensitive state must be refreshed from authoritative sources when material.

## Memory binding — installer populates once
- Personal state entry: exact repository / branch / path or equivalent durable source.
- Memory store/index: exact repository / branch / path; reuse existing compatible store, otherwise initialize from `templates/MEMORY_STORE.json`.
- Shared original: exact source/revision; read-only, never a personal write destination.
- Recipient-owned methods copy: exact owner/source/revision and upstream provenance; record actual copy evidence or NOT_CREATED.
- Private memory boundary: authenticated owner, verified provider visibility/access and verification time/source; exact authorized write destination. Unknown is not private.
- Actual host instruction entry: user-selected account-wide or Project scope, installation location and inspected text/version from the corresponding ACCOUNT_INSTRUCTIONS or PROJECT_INSTRUCTIONS template. Methods/state may share the recipient-owned verified private copy; an upstream/public/shared directory is not privacy. Record actual access boundary.
- Established connection: use known setup; reopen only on an observed failure.
- Domain sources: retain the Active domains bindings above; do not duplicate their authority.
- Receiving status: source readback / instruction loading / semantic save / correction / fresh-chat retrieval / remaining limitations, each with actual evidence or not tested.

Current-state summaries must link to the underlying current memory revision or owning domain. They are navigation/projections, not independent copies of every remembered fact.

## Full capability binding
- Available portable release / inspected source: deployment/RELEASE.md and actual revision.
- Accepted/used source release: actual evidence or UNKNOWN, never inferred from publication.
- Account/Project instructions: selected scope, prepared text, actual installation evidence or UNKNOWN.
- Active mission pointers: actual user work only, stored in this bound area when needed.
- Domain pointers: existing owned sources and present availability; no assumed configuration.
- Endpoint facts: established tools, evidence origin/date, effect permissions, resource limits and receiving; descriptor uses deployment/ENDPOINT_REGISTRY.md.
- Learning/hypotheses: use existing memory record classes or actual domain lifecycle; source of review/adoption authority.
- Update/recovery: deployment/UPDATES.md, previous compatible revision, unresolved receiving.
- Future automation: concrete condition/observer/receiver only when chosen; no scheduled service inferred.
