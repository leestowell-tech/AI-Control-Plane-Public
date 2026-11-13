# Endpoint Registry Contract

Status: CURRENT

## Purpose
Maintain live, instance-specific facts needed to route work. This defines registry shape; deployments store actual endpoints in writable user-instance or deployment state.

Do not hard-code vendor assumptions into the portable kernel. Capabilities, quotas, prices, models, permissions, and interfaces drift.

## Endpoint record
Record endpoint ID/name, class, capabilities/exclusions, dispatch type and exact launcher, authentication/permissions, reachable sources/receivers, privacy/data locality, concurrency/leases, cost/quota window, observed quota posture, latency/reliability and last verification, acknowledgement/checkpoint/cancel/receipt support, verification mechanisms, fallbacks, maintenance owner, and revalidation triggers.

Endpoint classes: CHAT_CONTROL / CODE_AGENT / WORK_AGENT / LOCAL_HOST / CI_RUNNER / CONNECTOR / SCHEDULER / HUMAN.
Quota postures: ABUNDANT / METERED / SCARCE / EXHAUSTED / UNKNOWN.

## Live preflight
Before consequential routing, verify only properties the job depends on. Prefer one batched preflight over chatty probes.

Revalidate after quota-window/exhaustion changes, authentication or permission changes, tool/model changes, dispatch/receipt changes, receiver failure, material performance divergence, or descriptor staleness beyond the job’s currentness requirement.

## Routing policy
Use kernel/EXECUTION_ROUTING.md.

For monetary-value resources, distinguish advertised monthly allowance from actual spendable balance on the exact account/pool. Before a discretionary charge or credit-consuming call, recover the instance owner's current spending policy and actual explicitly priced approval (action/result, native units and total cost, ceiling/scope/attempts). A quota flag, owned credits or generic task grant is not cost approval. Do not invent a credit-to-dollar conversion. Include trial/prepaid/plan credits in the owner's approval boundary; hold only unapproved billable work.

A registry entry is descriptive, not action authority. Availability does not grant permission. A named endpoint without a verified dispatch mechanism is not programmatically routable.

## Operator burden
For human launch, state the limitation, provide one complete payload, identify one verified destination, preserve the envelope/return route, and do not require the operator to reconstruct context.
