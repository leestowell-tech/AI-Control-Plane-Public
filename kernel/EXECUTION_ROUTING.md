# Execution Routing Kernel

Status: CURRENT

## Objective
Turn an intent into verified receiver-side work through an explicit, recoverable execution path. Routing is operational state, not advice about which tool sounds suitable.

## State machine
SELECT → DISPATCH → ACKNOWLEDGE → EXECUTE → CHECKPOINT → VERIFY → RECEIVE → RECONCILE → CLOSE

Allowed exception states: BLOCKED / FAILED / CANCELLED / EXPIRED / SUPERSEDED.

A later state may not be inferred from an earlier one:
- selected endpoint is not a dispatched job;
- dispatched job is not acknowledged ownership;
- acknowledged ownership is not execution;
- execution/tool success is not receiver acceptance;
- local completion is not mission reconciliation.

## Required records

### Job Envelope
Carries objective, scope mode, approved envelope, inputs, source versions, authority, constraints, expected outputs, success tests, stop conditions, urgency, privacy/data-locality class, idempotency key, and callback/receipt route.

### Endpoint Descriptor
Carries capabilities, dispatch mechanism, permission posture, data locality, cost model, quota/scarcity, concurrency, latency, reliability/currentness, continuity limits, supported receipts, verification boundary, and fallback compatibility.

### Routing Receipt
Records candidate endpoints, exclusions, selection rationale, actual dispatch type, estimated resource class, fallback, human action required, and state transition achieved.

### Execution Receipt
Records endpoint/job identity, acknowledgement, lease/owner, timestamps, checkpoints, artifact references, consumption when observable, validation evidence, receiver state, exceptions, and reconciliation disposition.

The receipt's `state` describes its bounded job. `reconciliation.mission_status` describes the parent mission; they are not interchangeable. A `CLOSED` job with an open, blocked or observation-bound parent explicitly records `reconciliation.job_status: CLOSED`. A declared unfinished job cannot be closed merely because the parent says closed. For compatibility only, older whole-mission receipts may omit `job_status` when `mission_status` is `CLOSED`; new producers should record both. No local job receipt closes undisposed parent lanes.

Parent `CLOSED` is a separately owned assertion requiring parent-owner evidence at actual mission reconciliation. Neither the legacy syntax, a child receipt nor schema validation establishes that assertion. The job schema does not infer the state of a different scope from its own state (for example, a separately authorized follow-up after a parent endpoint).

`RECEIVED`, `RECONCILED` and `CLOSED` require a verified receiver, received timestamp and nonempty passing verification with evidence. Artifact-bearing outcomes identify every returned artifact and hash. Empty artifacts are not proof of receipt. They are valid only when the owning job contract actually permits an artifact-free result and `reconciliation.artifact_disposition` records its kind (`NO_CHANGE`, `ARTIFACT_FREE`, `APPROVED_DEFERRAL` or `OBSERVATION_BOUND`), exact contract reference, reason and evidence. Approved deferrals also require the actual approval reference; deferral and observation dispositions require an owner and return condition. These fields document evidence and authority, not create them. An observation or deferral closes a bounded job only if that disposition itself fulfills its authorized contract; unfinished executable work remains open.

The receiver verifies the exact job, expected outputs, success tests, applicable contract/version and authority against independent source or receiver observations. It must not accept a producer-written reference, `PASS`, `VERIFIED` or approval string as proof by itself. Do not invent an artifact, approval, deferral or closed parent to satisfy validation. `RECONCILED` and `CLOSED` require meaningful dispositions for the bounded scope. Durable receipt retention is still required even when the result needs no separate deliverable artifact.

These are portable contracts, not an installed receiver. A package builder carrying the schema does not execute it. A real adapter must invoke a compatible validator (including date-time format checking where supported), preserve the parent/job distinction and perform the owning contract's effect/evidence checks at receiving. Older r6 validators reject the explicit artifact-free and parent-open job-closure forms; update the actual consumer before emitting them, or keep the job unreceived with that compatibility blocker. Never translate them into fabricated artifacts or whole-mission closure. Record the exact adapter/consumer version and unverified boundaries.

Machine-checkable schemas live in schemas/.

## Endpoint selection
Filter before scoring:
1. required capability;
2. action authority and permissions;
3. privacy/data-locality constraints;
4. receiver reachability and required environment;
5. verification capability;
6. hard budget/quota/deadline constraints.

Then compare capability fit, outcome reliability, continuity/recoverability, marginal cost, quota scarcity/opportunity cost, latency, operator burden, batchability, independence of verification, and fallback quality.

Cost efficiency may change endpoint or batching strategy. It may not silently reduce the approved scope mode.

## Dispatch types
- DIRECT: current operator can execute immediately.
- PROGRAMMATIC: callable launcher/API starts the job and returns acknowledgement.
- HUMAN_HANDOFF: no valid launcher exists; produce exactly one complete copy-paste payload and identify the destination if verified.
- SCHEDULED: governed scheduler owns future dispatch.
- UNAVAILABLE: no permitted dispatch path currently exists.

For HUMAN_HANDOFF, remain at SELECTED until dispatch is evidenced. Never say running because a prompt was prepared.

## Dispatch contract
Every dispatch includes stable job ID/idempotency key, immutable objective/scope/authority snapshot, source refs, expected output location, one clear owner, lease/timeout where asynchronous, checkpoint cadence, cancellation channel, receipt route, forbidden actions, and escalation conditions.

## Budget and quota governance
Track resource classes even when exact prices are unavailable: ABUNDANT / METERED / SCARCE / EXHAUSTED / UNKNOWN.

Record quota window and observed capacity when available, estimated job class without fabricated precision, batching/caching opportunity, fallback trigger, and actual consumption when exposed. Unknown capacity is not zero and not infinite. Prefer one high-information preflight and batched execution.

## Ownership, leases, and concurrency
- One active owner per exclusive lane.
- A lease has owner, start, expiry/heartbeat, and takeover rule.
- Branch movement does not prove worker liveness.
- Parallel lanes preserve independent state.
- Prevent duplicate execution with idempotency keys and receiver checks.
- On expiry, verify target state before re-dispatch.

## Retry and failure
Classify failures: SOURCE / CAPABILITY / PERMISSION / QUOTA / DISPATCH / ACK / EXECUTION / VALIDATION / RECEIVER / RECONCILIATION.

After failure: persist typed state/evidence; invalidate the failed action; check partial effects; preserve idempotency; change evidence, endpoint, payload, or condition before retry; continue independent authorized lanes. No unchanged retry loops.

## Verification and receipt
Verify the property that matters: artifact/version at receiver, deterministic tests, human-visible behavior when load-bearing, authority/non-goal preservation, and scope-mode reconciliation. Same-agent self-review is supporting evidence, not independent assurance.

## Security and authority
Routing never expands authority. Capability, credentials, or authentication do not grant permission for financial trades, external communication, destructive action, semantic promotion, production activation, or other consequential action. Transmit minimum necessary data without losing mission context.

## Reconciliation
Close a bounded job only when its receiver state is verified, all its scope items have dispositions, receipts are durable, residual risks/observation items are explicit, endpoint performance is available for calibration, and no independent authorized executable lane remains inside that job. Reconcile the parent mission separately against all its lanes and acceptance conditions; a child job closure is not parent completion.

## Persistent configuration administration

Configuration changes are routed effects. Preserve target/account identity, complete field coverage, desired source revision, observed revision/time, exact change digest, permitted operation, receiver and rollback. Treat missing fields as UNKNOWN, not empty or conformant. Separate proposed, draft, published and behavior-verified state. Revalidate the target immediately before a write; use the provider's atomic revision precondition when available. A digest is integrity evidence, not a grant or lock.

No component may unilaterally redefine its governing objective and enlarge its permission envelope. Changes to instructions can alter authority semantically even when a field is structurally editable. Required semantic/effect review cannot be replaced by a field allowlist. A failed or ambiguous write requires target reconciliation before retry. Rollback restores the named state; it does not undo external effects already performed.

Bind metered dispatch to provider/account/pool/window/unit and current evidence. Keep credits, API currency, requests and local resource measures distinct. Reuse the instance's atomic reservation journal. Conservative retained reservations are not observed actual cost; do not release/reset them because a job finished or a quota window name changed. Actual provider limits and externally shared consumption remain separate enforcement boundaries.

Apply these controls through existing owners and proportional adapters; this contract does not activate a new controller, scheduler, production publisher or semantic promotion process.
