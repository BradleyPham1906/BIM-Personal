# Flows and app SDK — initial research and threat model

Research date: 2026-11-13. Draft, not a specification, security certification, implementation, or completion of the research protocol. Single author; no independent review. The 48-hour task allowance is a rough backlog assumption, not a validated estimate. App source was inspected as text at main commit `95b7aee4db8be1fc28c0fbe7befc7407fabd1dda`; no application code or third-party code was run. A separate synthetic graph fixture was executed as described below.

## Question and outcome

How could per-object visual flows and an iframe SDK make BIM operations extensible without granting arbitrary access to the project or causing unreviewed changes? Recommend a staged, explicitly permissioned SDK and a typed, deterministic, initially acyclic graph evaluator with preview and a user-authorized commit. Reuse existing registration and action discovery only where their actual semantics are compatible; neither is an isolation boundary. This is a proposal, not an owner's decision.

## Source observations and limits

- The task requests per-object node graphs, read-only snapshots and listeners, and named commands over postMessage [1]. Its prior Giraffe note records per-object flows, state listeners and an iframe bridge as reference observations; it noted no declared npm SDK license at the time [2]. No code should be copied on that basis; re-check current licensing and permissions. Competitor notes are not a guarantee of current behavior.
- Pinned `testing/hooks-legacy.js` attaches `__a3dRegisterCommand`, `__a3dRegisterDiscipline` and `__a3dRegisterTab` to `window`; source calls them an extension API [3]. `discipline-tabs.js` stores a supplied command's function, and its comments say extension commands may override built-in commands; discipline and tab registration reject duplicate IDs [4]. These are trusted in-page JavaScript registration mechanisms, not evidence of iframe isolation, authorization or a stable external SDK. The checked-in phase-71 test describes registering a synthetic domain, but was read, not executed [5].
- The command catalogue gathers typed commands and ribbon actions; the command map includes interactive and destructive UI operations [6,7]. Discoverability is not authorization, and a bulk exposure of that catalogue would be unsafe. Select explicit, versioned commands with schemas, separate read and mutation permissions, and prevent plugins overriding host commands by naming collision.
- The existing dependency graph performs ordering but warns on cycles and appends remaining nodes in model order; visitor exceptions are caught and work proceeds [8]. That is not proof of atomic, fail-closed graph evaluation. A Kahn residual can include nodes downstream of a cycle, so identify true cycle members separately if the UI claims to show them. Reuse portions only after checking their runtime semantics.
- MDN says postMessage target origin matches scheme, host and port, and senders should be checked using origin/source and message syntax; navigation can change the receiving document [9]. For same-origin iframe content, combining allow-scripts with allow-same-origin is strongly discouraged; omitting allow-same-origin makes the origin opaque [10]. Isolation does not stop a permitted plugin transmitting data over its network.

## Design alternatives

| Approach | Benefit | Main limitation |
| --- | --- | --- |
| Trusted in-page registration | Fits current extension hooks; low adaptation | Callback has host-page privileges; cannot safely treat as an untrusted plugin. |
| Approved cross-origin HTTPS iframe + message protocol | Browser origin boundary, independently deployed UI | Requires exact origin and source validation, consent, navigation/revocation handling, and still permits external exfiltration. |
| Opaque sandbox iframe or file:// | Potentially useful for offline/development | Origin cannot establish plugin identity. `file:` target currently requires `*` per MDN; random nonce or channel alone does not establish identity. Authentication/deployment remain unresolved. |

First target an explicit HTTPS deployment and threat model, with owner consent and security review; do not claim other deployment modes are safely supported. Decide whether untrusted third-party plugins are permitted at all. Host and plugin origins, registration, distribution, plugin update provenance and cross-origin redirects need design and testing. An origin allows all scripts on that origin, not just one desirable package.

## Proposed graph contract

Each document stores schema version, graph ID, owner/object stable ID, node ID and version, typed input/output ports, edges, parameter values with dimensions/units, and source model revision. Define a small allowlist of pure nodes; no arbitrary eval or downloaded scripts in graph nodes. Validate imported graphs (unique IDs/ports, supported node versions, type/unit compatibility, resource quotas, and missing references) before execution. Explicit scalar/list semantics and cross-project ID remapping are essential; unknown nodes must remain inspectable without executing them. Version and migrate intentionally, preserving originals/backups.

Evaluate acyclic graphs in deterministic topological order with a stable tie-breaker, capture input revision, distinguish available, missing, failed and not evaluated, and propagate failures without manufacturing zero geometry. Reject cycles before *any* write. Pure evaluation yields a proposed change set, never direct model mutation. Preview and explicit user apply are separate; check revision, object existence, permissions and invariants at apply time, then commit as a single undoable transaction or reject the entire change. This behavior is proposed, not demonstrated in the app. Stale result, concurrent edit, close/undo, deleted owner, unit mismatch, graph migration and resource budget each need explicit UX. Define who owns generated geometry and whether downstream objects can refer to it before building.

## Proposed iframe API

Use a versioned bounded envelope `{version, session, id, kind, payload}` with a distinct request/response/event model, schemas, size and rate limits, timeouts and stable error codes. A request ID supports correlation; replay/deduplication and idempotency need explicit command-specific semantics. Session values identify a session but are not proof of identity. Listeners must unsubscribe on navigation, permission revocation, unload and timeout; event ordering, coalescing and backpressure need defined rules. No secrets in URLs or logs.

1. Host loads a pre-approved HTTPS origin and sends only to its exact target origin. Verify both event origin and expected iframe window, validate schema and permission on every request; invalidate the session on navigation or close. Each side authenticates the other under the deployment's trust assumptions. A matched origin/source is not proof that the plugin is benign.
2. Default deny. Consent names the plugin, origin, project, data categories and requested operations. Return minimum copied snapshot, with project and revision metadata; never hand out mutable host references. Scope geometry, selection, properties and subscription independently, and disclose that plugins may transmit granted data. Revoke and stop future events; previously disclosed data cannot be recalled.
3. Expose only audited named commands and typed parameters, not raw UI dispatch, host callbacks or arbitrary JS. Read commands require read grants; write commands require explicit write grant and, where appropriate, human preview/confirmation. Enforce project scope, invariant checks, revision preconditions, result/error and transactional undo. A read-only snapshot API does not imply all commands are read-only.
4. No unauthenticated wildcard fallback for private data. Offline `file:` and opaque sandbox mode stay disabled for sensitive SDK use until a separately reviewed bootstrap and trust model exists. Do not mistake nonce, `null` origin, or MessageChannel for identity.

## Reproducible isolated experiment

Run `python3 docs/research/fixtures/flows-dag-fixture.py` with Python 3.13. The toy evaluator tested A=2, B=3, sum then double = 10; changing A to 4 yields 14; unavailable B propagates None; cycle, duplicate input edge and missing reference are rejected. The script uses only the Python standard library. Output: `PASS: original=10; edited=14; unknown propagated; cycle, duplicate and missing node rejected`. It rebuilds all values and is neither incremental nor concurrent, is not the app, has no geometry, units, persistence, browser messaging, rollback, cross-frame security or independent replication. The fixture is evidence only that these toy assertions passed.

## Proposed tests and open gates

| Area | Fixture or check |
| --- | --- |
| Graph identity | Save/reopen, duplicate and cross-project import remap all node/object IDs and protect unknown versions. |
| Types and failures | Wrong units, scalar/list mismatch, deleted object, missing data, stale revision, quota and exception yield explicit errors, no guessed zero. |
| Ordering and writes | Fan-out, cycles with descendants, concurrent edits, repeated command, undo/redo, partial failure; no side effect on rejected graph; atomicity is verified against real model. |
| Messaging | Wrong origin, wrong window, oversized/malformed payload, schema downgrade, duplicate request, frame navigation/redirect, unsubscribe/revoke and delayed response are rejected or handled deterministically. |
| Isolation | Test deployed HTTPS hosts, same- vs cross-origin sandbox flags, network exfiltration, malicious plugin, plugin updates and host navigation with a dedicated security review; no data leaks outside granted scope. |
| SDK compatibility | Version handshake, capability discovery, backward compatibility, allowed and denied commands, listener event ordering, timeout and recovery. |
| Offline | Establish and independently review trust/bootstrap before testing; until then no security claim. |

Next: inventory actual app model snapshot and persistence APIs, real command effects and undo boundaries; verify existing tests against pinned commit; run browser and adversarial tests on agreed deployment; assess plugin distribution and licenses; choose scope, permissions and offline policy with owner; perform independent protocol review before SPEC, runnable acceptance tests and narrowly scoped implementation tasks. The fixture does not close those gates.

## References

[1] Task https://app.notion.com/p/3fecbfcc3a38812e97e1d103cae7d4cd
[2] https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/docs/research/research-giraffe.md
[3] https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/testing/hooks-legacy.js
[4] https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/ui/discipline-tabs.js
[5] https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/tests/e2e/bim_phase71_disciplines_scalability_browser_tests.py
[6] https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/commands/command-catalogue.js
[7] https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/commands/command-map.js
[8] https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/bim/dependency-graph.js
[9] https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
[10] https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe
