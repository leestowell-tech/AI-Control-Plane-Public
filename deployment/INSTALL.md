# Deployment Guide

Status: CURRENT

## Goal
Install the control plane without requiring the user to learn the architecture or memorize command vocabulary.

## Minimum deployment
1. For the installed owned-copy route, bind runtime methods to the verified recipient-owned copy. Reading the original directly is a separate session/reference route, not that installation; the original is never a recipient write destination.
2. Resolve or prepare the recipient's own verified private copy/store under the binding rules below before initializing `templates/USER_INSTANCE.md`.
3. Verify whether the active AI surface can actually write that store.
4. Add only the domain modules the user actually uses.
5. Run a fresh-session boot test using `BOOT.md`.
6. Run a real persistence test: `capture this` or a natural-language equivalent must produce a durable receipt or a typed persistence handoff.
7. Run a reset test after opening a fresh/shifted conversation, including a natural-language reset equivalent.
8. Run a discoverability test: `help`, `what are the commands again?`, or similar wording must recover the operator menu.

## User onboarding
Tell the user only:
- use AI normally;
- exact command wording is not required;
- if you ever do not know what to say, say `help` or ask what the commands are.

The AI should recognize ordinary-language equivalents for reset, capture, build, resume, current-state recovery, blocker diagnosis, and help. It should perform the matching behavior directly when safe rather than instructing the user to repeat a magic phrase.

Do not require the user to classify records, choose repositories, remember mission files, remember command names, or debug connectors unless they are genuinely the dependency.

## Personal memory integration

Use the established account/connector setup when supplied; do not reopen it as a speculative blocker. The installer owns these steps:
1. Resolve the user's existing memory home; if absent, agree the personal destination once and initialize the empty `templates/MEMORY_STORE.json` there. Keep user records outside shared rule files and never reset an existing store. A directory in a public or source-owner shared repository is not a private recipient store. Prefer the recipient's own private copy; an existing compatible private destination can remain in place. Verify authenticated owner, actual visibility/access, exact branch/path and recipient write authorization before capture. Unknown privacy means handoff, not write. Do not migrate, create accounts/repositories or change permissions without the required authorization.
2. Populate the Memory binding in the user instance and install a rendered account-wide or Project instruction entry according to the user's chosen scope (`templates/ACCOUNT_INSTRUCTIONS.md` or `templates/PROJECT_INSTRUCTIONS.md`). Bind source, branch and path; do not leave placeholders or rely on a link in the current chat.
3. Apply `deployment/MEMORY_WORKFLOW.md` for classification, update, provenance, indexing and retrieval. Keep domain-owned detail with its existing owner.
4. Exercise `tests/MEMORY_ACCEPTANCE.md` with synthetic material, then one harmless real task in the user's actual fresh conversation. The installer performs record inspection and cleanup; the user need not learn the test machinery.
5. Record exact installed source/package version and separate structural/semantic/fresh-chat results. Keep the mission open for untested behavior. Sending a bundle does not update an earlier uploaded copy or install host instructions.

The GitHub connector is a transport. The qualification target is faithful, organized and retrievable memory through normal language. Do not substitute repeated connectivity checks for that outcome.

## New or changed domain entries

Apply `templates/DOMAIN_CONTRACT.md#entry-inheritance-and-receiving` before accepting new, extracted or replacement entries. Resolve the user instance's current shared sources, use its current producer/template, verify generated bindings and published receiving, and test the intended host/branch instruction chain. Existing children do not establish future inheritance; untested loading remains explicit. A missing loader test is not permission to expand authority.

## Validation gates
Deployment is not accepted until:
- kernel read access is confirmed;
- user-state read access is confirmed;
- write capability or fallback is empirically tested;
- fresh-session recovery works;
- natural-language command discovery works;
- kernel/user/domain authority separation is preserved;
- the user can operate from the thin cockpit without architecture study or command memorization.

## Owner-selected ordinary-use feedback

If the owner explicitly chooses ordinary use with feedback later instead of an immediate supervised trial, record that choice and proceed with authorized source preparation and updates. Do not demand a fresh-chat demonstration, make the user arrange an observation, or reopen established connector capability. Preserve normal per-save readback and truthful retrieval behavior during use. Record source readiness separately from unobserved behavior; the quality criteria above remain criteria for a verified claim, not an artificial hold on owner-authorized provisional use. Use the promised report as the return trigger without inventing a date, reminder or automatic watcher.

## Complete protocol profile
Install deployment/CAPABILITY_PROFILE.json and its local dependencies as one compatible source release. BOOT.md and kernel/ROUTING.md select the relevant methods. Build and Reset are primary paths; the account entry should describe cumulative work and the full methods, not only saving notes.
Bind actual user state, active work/domain sources, available endpoints and authority without fabricating initial goals or deployment evidence. Use deployment/UPDATES.md for release comparison, receiving and rollback. Apply tests/PROTOCOL_ACCEPTANCE.md proportionately with the owner's actual observation choice. No access to source-owner private repositories is required at runtime.

## Recipient-owned copy route — November13 correction

The recipient obtains their own copy and uses that copy; the original methods are read-only to them. Preserve source provenance without inheriting source-owner private state, credentials, accounts or grants. A download is not installation and a copy is not proof of private storage.

GitHub: do not use an ordinary public fork for private memory. Public forks are public. A new repository created from a sanitized template can have recipient-selected private visibility; a downloaded snapshot imported into a separate private repository/workspace is another route. Verify actual owner/access after creation and before capture. Do not assume a button or template enforces privacy. No repository/account creation or visibility change is authorized merely by these instructions.

Use only necessary template/default-branch files; exclude source-owner state and private history. Keep source version and license/provenance. Recipient changes and memory belong to their copy. Updates are reviewed imports of source-owned methods only: preserve private state, customization, current records and existing grants; never mirror/push recipient content back into the original. Stop on conflicts and retain the last working copy. No automatic updater is installed.

References: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template ; https://docs.github.com/en/pull-requests/reference/forks
