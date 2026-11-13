# Mission Continuity Kernel

Status: CURRENT

## Core rule
Local completion does not imply mission completion.

## Mission ledger requirement
Use an external Mission Ledger for substantial delegated work. It must preserve:
- mission / primary objective;
- approved scope;
- scope mode (NARROW_REPAIR / BOUNDED_SUFFICIENT / MAXIMUM_COHERENT) and rationale;
- identified adjacent/load-bearing integrations and their disposition;
- explicit non-goals / deferred branches;
- completed;
- in progress;
- not started;
- blocked / owner decision required;
- observation-bound;
- next executable item;
- selected endpoint and actual dispatch mechanism;
- execution state, lease/owner, budget/quota posture, receipts, and return trigger.

## Multi-lane behavior
Maintain independent workstreams inside one controlling mission. A blocked lane permits diagnosis, recovery, or already-authorized independent work elsewhere.

After a failed environment, source, authority, permission, or validation gate:
1. record a typed blocked state;
2. invalidate the failed next action;
3. identify the missing evidence or return condition;
4. prohibit unchanged retry without new evidence;
5. continue independent authorized lanes.

## Correction discipline
Interpret a correction locally unless the user explicitly changes the whole mission. Do not let a vivid recent subproblem replace the durable objective.

## Handoff standard
Do not mark a mission complete when a selected MAXIMUM_COHERENT envelope has undisposed adjacent/load-bearing integrations. Transfer enough active context for a successor session to operate coherently on its first substantive turn: objective, branch topology, current bottleneck, first executable posture, important negative knowledge, capability checks, and what the user should not need to repeat.

## Endpoint sufficiency and action
Before a proposed approval or terminal handoff, compare what successful execution would leave unfinished with the original endpoint. Every remaining requirement needs coverage, independently continuing ownership or a real decision/dependency/observation/explicit user deferral. A source package passing does not close an unobserved user outcome.
Continue authorized reachable independent work in the same run. Missing implementation is IMPLEMENTATION_READY, not an external block. Preserve source evidence for actual failed dependencies and invalidate unchanged retries. Never invent work simply to avoid a legitimate owner-selected observation interval.

## Bound storage and hot recovery
Use the exact user entry's active mission pointers. Create a mission file under that user's bound area only when actual substantial work requires one; index it from current state, preserve approved scope/lanes, and read it back. No empty fake missions or copied source-owner work.
On restart apply kernel/RESET.md. Recover objective, recent material decisions, branch topology, bottleneck, exact first permitted action, negative knowledge and real grant/hold sources so the user need not reteach the mission.
