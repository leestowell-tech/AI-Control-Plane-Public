# AI Control Plane

A complete portable architecture for sustained human–AI work: research, Build, Mirror, Reset, planning, execution routing, capture/recovery, verification, learning and maintenance. Deep capabilities, ordinary-language use. All 23 declared capabilities remain included; this is not a reduced prompt pack.

## Give your AI its own working setup

The intended GitHub handoff is a clean template copied into the recipient’s own **private repository**, not a public fork. An existing GitHub account and ChatGPT connection should be reused, not set up again. Template/copy creation and actual account configuration require the recipient’s authorization. This repository is published as a public GitHub template. Choose **Use this template → Create a new repository → Private** to make your own independent copy.

Then follow [the installation guide](deployment/INSTALL.md) in the recipient’s chosen account-wide scope (or a Project only if chosen). Bind the recipient’s copy and own private memory; preserve existing preferences and records. Start normal operation with [BOOT](BOOT.md). Say help for [the small everyday menu](OPERATOR.md); all commands exposes the complete capabilities. Exact command wording is optional.

**GitHub reading is not memory writing.** Standard ChatGPT’s GitHub app is read-only according to current provider documentation. Qualify the actual connected surface and its existing write options before promising durable saves. If no authorized write path exists, prepare a handoff and state the unfulfilled installation requirement. Do not invent a connector, force an account change or claim that a successful read installed the system.

## What must actually work

One useful task, correct scope/settings, verified private save/readback, a correction recovered in a fresh conversation, and any representative permitted tool effect included in the setup. Test public/wrong-owner/stale-revision rejection, preserve customization on updates, and keep newest memory on rollback. Source availability, copying, installation and independent ordinary usefulness are separate milestones. A truthful fallback is not full working continuity.

## Included source and checks

The kernel, routes/profile, all templates, domain interface, source packager, memory helper, schemas, complete offline test suite and repository upkeep tools are included. Historical schema fixtures retain counterfactual regressions without exporting old recipient setup. deployment/RELEASE.md describes current limits. requirements-test.txt describes test dependencies; do not install them without applicable authority.

Run python3 -m unittest discover -s tests after the maintainer supplies the verified current source manifest; a local candidate test manifest is not release provenance. Repository navigation: python3 tools/repository_hygiene.py generate, then audit. Neither test suite establishes the recipient host’s behavior.

No personal state, credentials or source Git history is distributed. Reuse/license terms remain owner decisions; no open-source license is asserted. Recipient instructions and actual permissions govern every effect.
