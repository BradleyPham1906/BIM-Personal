# Independent check, V172f (multi-tab locks and unload)

Date: 2026-11-07

Method: each pinned source was downloaded to a scratch folder and the cited lines were re-read with sed and grep; no downloaded code was run.

| Fact | Source and lines read | Result | Note |
|---|---|---|---|
| F1 ifAvailable, not grantable: callback(null), not queued | W 615-619 (request a lock) | Confirmed | The callback runs with `null`, the promise resolves with its result and the steps abort before "Enqueue request in queue". |
| F2 steal: held locks removed, released promise rejected with AbortError, request prepended | W 608-613 | Confirmed | Exact wording at 610-613. |
| F3 steal + ifAvailable rejects NotSupportedError | W 510 | Confirmed | Also 511 (steal with shared mode) and 512 (signal with steal or ifAvailable) reject NotSupportedError. |
| F4 unloading document cleanup steps terminate the agent's locks and requests | W 314, 320-326 | Confirmed | Requests aborted first, then locks released, on the lock task queue. |
| F5 [SecureContext]; SecurityError when obtaining a lock manager fails; "web-locks" bottle map | W 340, 357, 508, 186 | Confirmed | 507 also rejects InvalidStateError when the document is not fully active. |
| F6 auto-commit after all results handled; commit() does not wait for script | I 1061-1069 | Confirmed | Also requires no new requests and the transaction not aborted. |
| F7 connection closed with destroyed context; close waits for transactions; only forced aborts | I 458-471, 5093-5113 | Confirmed | The note at 5109-5113 adds corruption or an I/O error as abnormal closes. |
| F8 pagehide fired, then visibility updated to hidden | H 114782-114792 (dfn at 114730) | Confirmed | Order: page showing false, pagehide, then "Update the visibility state ... hidden". |
| F9 LockManager, Lock: Chrome 69, Firefox 96, Safari 15.4; mobile mirror | B LockManager.json, Lock.json | Confirmed | chrome_android, firefox_android, safari_ios are "mirror". |
| F10 BroadcastChannel: Chrome 54, Firefox 38, Safari 15.4 | B BroadcastChannel.json | Confirmed | Mobile entries "mirror". |
| F11 commit 76/74/15; durability 83/126/15 | B IDBTransaction.json | Confirmed | No flags on these entries; mobile "mirror". |
| F12 OnLockContention on contention or query; bfcache holder evicted, locks broken synchronously, re-evaluated | C lock_manager.h 50-54, 314-346, 565-571 | Confirmed | Granted at 344-346 when can_grant after re-evaluation; locks broken only when the observer returns true. |
| F13 RFH::OnLockContention evicts with kWebLocksContention, returns true | C render_frame_host_impl.cc 4905-4912 | Confirmed | Returns false when not in bfcache. |
| F14 PGlite: leader via awaited Web Lock, per-tab close lock, BroadcastChannel, no steal | P1 150-190, 540-555, 585-600, 641-642, 745-757; LICENSE | Confirmed | Election lock `pglite-election-lock:<id>` never released (551); no `steal` or `ifAvailable` anywhere; LICENSE is Apache 2.0. |
| F15 wa-sqlite: navigator.locks.request, polling with ifAvailable | P2 1-10, 375-395; LICENSE | Confirmed | Incomplete rather than wrong: only some acquisitions poll (POLL_SHARED/POLL_EXCLUSIVE); others wait, with an AbortSignal timeout when lockTimeout is finite (378-385). LICENSE is MIT. |
| F16 Firestore: lease in IndexedDB every 4000 ms, 5 s eligibility, unload note, zombie via localStorage from pagehide | P3 83-98, 134-135, 150-160, 990-1011, 1052-1066; LICENSE | Confirmed | Lease in the "owner" store; handler is registered for `pagehide` (1011) and calls markClientZombied (localStorage.setItem) first. LICENSE: Apache-2.0 (protobuf part BSD-3-Clause). |

Tally: 16 confirmed, 0 corrected, 0 not confirmed (F15 confirmed with a scope note).
