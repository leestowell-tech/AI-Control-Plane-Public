# Mission Ledger Template

Status: TEMPLATE

## Mission

## Primary objective

## Outcome and progress evidence
Use only fields that materially help this task; the assistant maintains them, not the user.
- Actual receiver and useful result:
- Relevant current context / exact sources:
- Baseline and observation unit (UNKNOWN if unavailable):
- Observable progress / success and failure criterion:
- Strongest rival explanation / what would refute success:
- Actual result versus proxy/activity:
- Measured coverage and unmeasured scope:
- Assistance, rework, elapsed time and cost (actual versus estimate):
- Feedback source and next return / stop condition:

## Authority / approval
- Authority source:
- Approved envelope:
- Irreversible or high-impact exclusions:

## Scope selection
- Mode: NARROW_REPAIR / BOUNDED_SUFFICIENT / MAXIMUM_COHERENT
- User direction or inference:
- Why this mode:
- Material alternatives:
- Load-bearing adjacent integrations:
- Explicit non-goals:
- Scope-change history:

A material build/upgrade may not leave scope mode blank. Silence is not permission to select a smaller mode. For architecture, infrastructure, governance, system creation, redesign, and upgrades, default to MAXIMUM_COHERENT unless the user explicitly requests smaller scope.

## Job / routing
- Job envelope ID:
- Candidate-field source / coverage:
- Selected endpoint:
- Dispatch type: DIRECT / PROGRAMMATIC / HUMAN_HANDOFF / SCHEDULED / UNAVAILABLE
- Dispatch payload or durable pointer:
- Budget/quota posture:
- Data locality / privacy class:
- Idempotency key:
- Lease / owner / expiry:
- Fallback:
- Cancellation path:

## Execution state
SELECTED / DISPATCHED / ACKNOWLEDGED / RUNNING / CHECKPOINTED / VERIFYING / RECEIVED / RECONCILED / BLOCKED / CANCELLED / FAILED / CLOSED

## Workstreams
| Lane | Scope item | State | Evidence | Endpoint / owner | Next action / return trigger |
|---|---|---|---|---|---|

## Retained production design — when rebuilding or generating
- Existing editable source / canonical writer and legitimate exceptions:
- Stable identities, source/tool versions and frozen choices:
- Locked facts / allowed variation:
- Current manual edits and preservation/reconciliation rule:
- Outputs and affected dependency/consumer map:
- Input change → invalidated evidence → affected rebuild/check:
- Same-input repeatability / once-only effects and valid no-change:

## Completed

## In progress

## Not started

## Blocked / owner decision required

## Observation-bound

## Negative knowledge / do not relearn

## Receipts
- Routing receipt:
- Dispatch acknowledgement:
- Execution receipt:
- Receiver-side verification:
- Reconciliation receipt:
- Exact candidate / affected input versions at final receiving:
- Supported bad case / legitimate valid or no-change control:
- Actual production path and remaining host/user evidence:

## Bounded improvement loop
- Observation → diagnosis → authorized correction → next observed result:
- Failed producing/context/checking/receiving step and its owner:
- Retry/attempt/cost limits, no-progress escalation and cancellation:
- Reusable procedure/skill and the instance's actual adoption policy:
- Later transfer evidence / false criticism / no demonstrated gain:

## Completion checksum
Before closure:
1. Mark every approved scope item and every load-bearing adjacent integration DONE / DEFERRED / BLOCKED / OBSERVATION / SUPERSEDED.
2. Reconcile delivered scope against the selected scope mode and original objective.
3. Verify actual receiver state; worker/tool narration is insufficient.
4. Record remaining executable lanes and continue them under existing authority.

## Integration and evolution
- KEEP / MERGE / DERIVE / REMOVE / DEFER and rationale:
- Source-class/candidate-field coverage when relevant:
- Producer → receiver → use verification boundary:
- Actual lifecycle receiver, ingress, evidence/return condition:
- DESIGN_PASS / IMPLEMENTATION_PASS / unresolved work:

## Endpoint residual and restart
- What would successful current execution still leave unfinished?
- Independently continuing lanes and real evidence:
- Current grants, holds, proposed new permission and exclusions:
- First permitted restart action and negative knowledge:
- Actual source/structure/host/behavior/ordinary-use evidence, separated:
