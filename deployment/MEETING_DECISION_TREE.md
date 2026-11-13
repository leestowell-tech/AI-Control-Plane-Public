# AI Control Plane — Meeting Deployment Decision Tree

Status: CURRENT

Use this while standing with the target user. Do not debug one branch indefinitely; move down the ladder.

## Purpose before transport

Recover the intended use from the conversation before choosing a route; do not make the person repeat settled choices. These are distinct purposes, not a fixed product ladder:
- **Use methods now**, including on a borrowed account: read the methods and apply them to the task. Session use needs no personal-memory setup. Do not import the visitor’s private context, bind the account holder’s state to the visitor, or claim personal continuity. Anything entered in that account may remain with its holder.
- **Recover my own continuity away from my usual device**: methods access is not private-context access. Verify the authorized identity and suitable private context route before retrieving personal state. A borrowed account is not permission to disclose that state. If no safe route is established, continue methods-only and identify the precise missing gate.
- **Leave methods for someone else / create their owned copy**: keep the original read-only, use a methods-only artifact, and let the recipient choose scope. Delivery alone does not install anything or authorize state capture.
- **Install or update ongoing operation**: use recipient-owned methods and verified recipient-private memory; preserve their preferences and history. A separate private repository/copy is not a public GitHub fork. Account settings, connectors and permissions require their own authorization.

Use the simplest supported transport for the selected purpose. ZIP extraction is host-dependent; a sectioned Markdown kit is an alternative, not proof of actual host support. Full installation and service offerings remain possible without making them prerequisites to immediate useful work.

## A. Can the target ChatGPT surface read the canonical GitHub repo?
- YES → use the original as a read-only methods reference for session use. For installation, follow `deployment/INSTALL.md` and bind a verified recipient-owned copy; source access is not installation.
- NO → check another available ChatGPT surface that may have GitHub access (for example a research/agent/coding surface).

## B. Can any available ChatGPT surface read the canonical GitHub repo?
- YES → use that surface for the selected purpose under the same identity/privacy gates; do not move private state between accounts merely because another surface can read the methods.
- NO → continue.

## C. Can the user use a ChatGPT Project or upload files?
- YES → use `deployment/PROJECT_BUNDLE.md`: prefer the methods-only ZIP if extraction is supported, otherwise the sectioned Markdown kit. Do not require dozens of separate uploads or upload anything without authorization. Record source and installed-copy versions separately.
- NO → continue.

## D. Can the user provide one attached/pasted bootstrap file or persistent instruction surface?
- YES → use `deployment/EMERGENCY_BOOTSTRAP.md`. This gives the behavioral control plane but not hidden user/domain state.
- NO → provide the emergency bootstrap text in the active chat for that session and explicitly mark continuity as non-durable.

## Separate write-path test
Repo/kernel read access and durable user-state write access are separate questions.

Only for an authorized persistence purpose, after a read path is established, test:
1. Before any personal-state write, verify the actual account/recipient identity, recipient ownership, private visibility/access, exact destination/revision and authorization for that write; then verify receiving state. Writability alone is not sufficient. The original and public forks are never recipient memory destinations. Unknown ownership/privacy or a failed guard means PERSISTENCE HANDOFF, not a write or unchanged retry. Do not create accounts, change permissions, migrate state or import another person’s data without authorization.
2. Can the AI write it?
3. Can the AI verify the receiving state and return a receipt?

Disposition:
- YES → authorized capture/memory operation with actual write/readback receipts. This establishes that persistence path only, not complete installation or fresh-conversation readiness.
- READ-ONLY KERNEL + OTHER WRITABLE STORE → use the other store for user state while retaining kernel authority in GitHub/files.
- NO WRITABLE STORE → activate `PERSISTENCE HANDOFF` mode. Never claim capture succeeded.

## Stop conditions
Do not spend meeting time debugging connector plumbing beyond its value. If a branch does not become usable quickly, descend to the next deployment form and get the user operational.

## Minimum meeting acceptance
Before leaving, verify at least:
- one reachable control-plane authority path;
- `help` or natural-language command discovery;
- `reset` behavior;
- for session-only use, one useful task and an explicit non-durable boundary; for authorized installation, one real capture/persistence test or explicit handoff fallback;
- QuickMarket authority reachable if QuickMarket is being installed;
- user understands only: use AI normally; say `help` when unsure.
