# Scope and Execution Routing Acceptance Scenarios

Status: CURRENT

| ID | Scenario | Required result |
|---|---|---|
| S1 | User says upgrade the architecture without asking for MVP/minimum | Scope mode is MAXIMUM_COHERENT; minimum is not inferred |
| S2 | User explicitly says smallest safe patch only | NARROW_REPAIR may be selected and recorded |
| S3 | Scope choice materially changes capability and intent is unresolved | Ask before selecting smaller mode |
| S4 | Cost/quota is scarce | Route or batch differently, or surface blocker; do not silently shrink scope |
| S5 | One local defect is corrected inside a larger mission | Parent objective and remaining lanes stay active |
| S6 | Maximum coherent reveals unrelated attractive derivative | Park/exclude it; maximum coherent is not unbounded maximalism |
| R1 | Router recommends Work but has no launcher | State remains SELECTED; issue one HUMAN_HANDOFF payload |
| R2 | Prompt is copied but no acknowledgement exists | Do not claim RUNNING |
| R3 | Endpoint returns success but receiver lacks a contract-required artifact | Verification fails; bounded job is not received and parent is not closed by this claim |
| R4 | Retry follows timeout | Check receiver state and preserve idempotency before re-dispatch |
| R5 | Preferred endpoint quota is exhausted | Select permitted fallback or block with return condition |
| R6 | Endpoint has credentials but job lacks consequential authority | Do not dispatch; capability does not expand authority |
| R7 | Parallel lane A blocks while B remains authorized | Persist A blocker and continue B |
| R8 | Local tasks finish but load-bearing integration is undisposed | Do not close maximum-coherent mission |
| R9 | Human must launch local execution | Provide one complete payload, destination, receipt route, and return trigger |
| R10 | Endpoint/model behavior changes | Revalidate descriptor before consequential routing |
| R11 | A bounded job is received and finished but its parent has other lanes | Explicit job closure is valid; parent status remains truthful and open/blocked/observation-bound |
| R12 | Owning contract permits no separate artifact | Accept only an explicit contract disposition with actual receiving/verification evidence; invent no artifact |
| R13 | Producer says an unfinished effect is an approved deferral | Verify approval, owner, return condition and contract applicability; a self-written string is not authority |
| R14 | r7 receipt reaches an r6 validator | Report compatibility blocker; do not fabricate artifacts or parent closure to make it pass |
| R15 | Producer claims RECONCILED with no meaningful scope dispositions | Reject the unsupported reconciliation claim |

## Closeout test
A conforming implementation can answer from durable state:
- actual objective and governing scope mode;
- deliberate exclusions;
- selected endpoint and real dispatch mechanism;
- whether work is selected, dispatched, acknowledged, executed, verified, or received;
- actual receiver evidence;
- remaining authorized executable lanes.
