# Deployment Capability and Fallback Contract

Status: CURRENT

The control plane is transport-agnostic. Do not assume a specific ChatGPT plan, connector, agent surface, or repository write capability.

## Purpose before transport

Recover the intended use from the conversation before choosing a route; do not make the person repeat settled choices. These are distinct purposes, not a fixed product ladder:
- **Use methods now**, including on a borrowed account: read the methods and apply them to the task. Session use needs no personal-memory setup. Do not import the visitor’s private context, bind the account holder’s state to the visitor, or claim personal continuity. Anything entered in that account may remain with its holder.
- **Recover my own continuity away from my usual device**: methods access is not private-context access. Verify the authorized identity and suitable private context route before retrieving personal state. A borrowed account is not permission to disclose that state. If no safe route is established, continue methods-only and identify the precise missing gate.
- **Leave methods for someone else / create their owned copy**: keep the original read-only, use a methods-only artifact, and let the recipient choose scope. Delivery alone does not install anything or authorize state capture.
- **Install or update ongoing operation**: use recipient-owned methods and verified recipient-private memory; preserve their preferences and history. A separate private repository/copy is not a public GitHub fork. Account settings, connectors and permissions require their own authorization.

Use the simplest supported transport for the selected purpose. ZIP extraction is host-dependent; a sectioned Markdown kit is an alternative, not proof of actual host support. Full installation and service offerings remain possible without making them prerequisites to immediate useful work.

## Capability preflight
For each deployment verify separately:
- can the AI read the kernel repository?
- can it read the user-state source?
- can it write durable user state?
- can it create/update domain artifacts?
- can it perform external actions?
- can it verify those actions at the receiver?

## Routing preflight
Capability alone does not select an endpoint. Use the live Endpoint Registry and `kernel/EXECUTION_ROUTING.md` to compare capability fit, authority, data locality, receiver access, marginal cost, quota/scarcity, latency, reliability, continuity, verification, and fallback.

The selected route must name its actual dispatch mechanism. If no programmatic launcher exists, classify the route HUMAN_HANDOFF; generate one complete payload and keep state at SELECTED until the human dispatch is acknowledged.

## Preferred topology
1. Canonical kernel repository — maintained centrally; session/reference use consumes it read-only; installed operation binds a recipient-owned methods copy with explicit source provenance.
2. User-instance durable store — personal state, missions, captures, preferences; recipient-owned and verified private; writable only with authorized receiving verification.
3. Domain stores — specialist authority/state/lineage as warranted.

## Degradation ladder
- Full read/write: persist directly and return commit/action receipt.
- Kernel read + user-store write: normal portable operation.
- Read-only GitHub: use GitHub for authority/recovery; write captures to another approved durable store.
- No durable write path: produce a typed `PERSISTENCE HANDOFF`; never claim the record was saved.
- Selected endpoint unavailable or quota-exhausted: reselect from permitted fallbacks; preserve idempotency and current mission state; do not loop unchanged retries.
- Manual-only endpoint: issue one self-contained handoff, record the user-visible destination when known, and wait for acknowledgement without pretending execution began.
- No authoritative read path: expose `SOURCE UNREACHABLE`, reduce confidence, and avoid consequential state claims that depend on it.

## Personal-state gate

Before any personal-state write, verify the actual account/recipient identity, recipient ownership, private visibility/access, exact destination/revision and authorization for that write; then verify receiving state. Writability alone is not sufficient. The original and public forks are never recipient memory destinations. Unknown ownership/privacy or a failed guard means PERSISTENCE HANDOFF, not a write or unchanged retry. Do not create accounts, change permissions, migrate state or import another person’s data without authorization.

## Deployment rule
Capabilities are verified by actual reads/writes/receipts, not by UI labels or model assertions.
