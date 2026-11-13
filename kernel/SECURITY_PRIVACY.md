# Security and Privacy Boundary

Status: CURRENT

## Principles
- Least privilege: read/write/action access is granted only to the minimum required surface.
- Capability verification: do not assume a connector can read, write, execute, delete, or act because it is connected.
- Secrets exclusion: credentials, tokens, recovery codes, private keys, and equivalent secrets do not belong in ordinary repository memory/state.
- Authority separation: read access, repository mutation, semantic promotion, and external execution are distinct permissions.
- Third-party minimization: retain identities only when materially necessary for authority, provenance, contact, legal/contractual meaning, or disambiguation.
- Cross-domain containment: one domain does not inherit permissions, state, or action authority from another merely because both use the same control plane.
- Receipt discipline: a claimed write/action must have receiver-side evidence when material.
- Revocation/fallback: workflows must degrade safely when access disappears, sources become stale, or permissions change.

## Consequential actions
External communications, destructive writes, production changes, money movement/trading, credential changes, privacy-sensitive disclosure, and semantic authority expansion require stronger evidence and approval appropriate to consequence.

## Storage rule
Store the minimum durable information needed for recovery and learning. Preserve provenance without duplicating unnecessary sensitive source material.
