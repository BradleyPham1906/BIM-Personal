# Browser storage experiments for the localStorage to IndexedDB migration (2026-10-31)

Measured evidence (level P, for this one Chromium build only) on ten claims a move of BIM-Personal's
project storage from localStorage to IndexedDB will rely on, plus a look at what the built app
writes at boot. Every number below was produced by a script in
`reference/experiments/local-storage/`, run on 2026-10-31. Raw JSON output was written to the
session's scratch directory, not the repository; the raw numbers are copied into the tables here.

## Method and environment

### Environment

| Item | Value |
|---|---|
| Browser | Chromium build `chromium-1243` in `/opt/pw-browsers`, `browser.version()` = **153.0.8010.12** |
| Mode | **Headless**. Default `chromium.launch()` runs the separate `chromium_headless_shell-1243` binary. Where noted, the full Chromium binary was also run in its new headless mode (`channel: 'chromium'`), same version string. No headed run was possible (no display). |
| Driver | Node v22.23.4, `require('playwright')` 1.63.0; no `playwright install` was run |
| Machine | Linux 6.18.44, 4 vCPU Intel Xeon @ 2.10 GHz, 16 GB RAM; disk 270.6 GB total, 31.0 GB free (statfs of the scratch directory) |
| Origins | `http://localhost:<port>` from a tiny Node `http` server in `_lib.js` (port random, or fixed where the origin had to be the same across restarts); `file://` pages written into the scratch directory |
| Not available | **Firefox and WebKit are not installed here** and were not installed. Nothing below covers Firefox, Safari (macOS or iOS), any mobile browser, or headed desktop Chrome. Headless may differ from headed Chrome where the browser uses heuristics or prompts (persist(), quota). |

### Procedure

- Each measurement was run at least 3 times (5 for the timing and compression scripts), each run in a
  fresh browser context or a fresh temporary profile, so no run saw another's data. All raw values
  are listed; "mean" is the arithmetic mean and "spread" is max minus min.
- Timings are taken in the page with `performance.now()` (Chromium headless rounds it to 0.1 ms
  here). For asynchronous IndexedDB work, the main thread's longest stall is measured by a
  `MessageChannel` ticker that re-posts itself while the operation runs (`maxGapMs`).
- Data identity is checked by SHA-256 (`crypto.subtle.digest`) of the bytes before the write and after
  the read; strings are hashed as their UTF-8 bytes.
- Page code is ES5 (with Promises, which the IndexedDB, Streams and subtle crypto APIs need); the Node
  drivers use `async`/`await`.
- Temporary profiles were deleted by each script; one left by a failed first run of e08 was deleted by
  hand. No large file was written into the repository.

### Scripts (all in `reference/experiments/local-storage/`)

| Script | Tests |
|---|---|
| `_lib.js` | shared helpers: the localhost server, scratch directory, statistics, result writer |
| `e01_localstorage_quota.js` | H1: the localStorage limit by binary search, and the error thrown |
| `e02_idb_large_values.js` | H2: single 50 MB and 200 MB values (ArrayBuffer and JSON string), hash compare |
| `e02b_idb_value_ceiling.js` | H2 follow-up: the exact single-value ceiling; 200 MB as a Blob; 200 MB as 4 x 50 MB records |
| `e03_storage_estimate.js` | H3: estimate() quota and usage; usage after a 100 MB write; persistent profile vs fresh context |
| `e04_persist.js` | H4: persist() / persisted() with no grant, Playwright grants, and CDP grants |
| `e05_file_origin.js` | H5: file:// storage, sharing between two files in different folders, navigator.storage there |
| `e06_restart.js` | H6: data across a browser restart on one profile (http and file://) |
| `e07_timing.js` | H7: main-thread cost of localStorage vs IndexedDB for a 4 MB JSON string and 4 / 40 MB buffers |
| `e08_durability.js` | H8: the durability option, tx.durability's default, timing per hint, and a SIGKILL survival check |
| `e09_multitab.js` | H9: versionchange / blocked between two tabs |
| `e10_compression.js` | H10: CompressionStream formats, ratio and time on two CAD-like JSON inputs |
| `e11_app_boot_storage.js` | the app: what `canvas_v10.html` writes to storage at boot, over http and file:// |

Note: `e12_files_install_surface.js` in the same folder (renumbered from e10 to end the clash) is **not** part of this set; it appeared there
during this session from another piece of work, and its number collides with `e10_compression.js`.

### Which hypotheses held

| # | Hypothesis | Outcome |
|---|---|---|
| 1 | localStorage limit about 5 MiB of UTF-16 characters; QuotaExceededError | **Held, exactly**: 5,242,880 code units (key + value) per origin; `QuotaExceededError`, code 22, a DOMException |
| 2 | One 50 MB and one 200 MB value accepted, byte-identical | **Partly failed**: 50 MB held; **200 MB as one ArrayBuffer or string is refused** (single-value ceiling 133,169,152 bytes = 127 MiB). 200 MB as a Blob, or as 4 records of 50 MB, held |
| 3 | estimate() reports quota/usage; usage rises by the stored size; quota differs persistent vs fresh | **Held**, with a surprise: quota is reported as usage + a fixed headroom (10 GiB persistent profile, 3 GiB or 4 GiB fresh context), not a share of disk |
| 4 | persist() behaviour in headless | **Measured**: `false` with no grant and with every grant Playwright accepts; `true` only when the permission is set through CDP |
| 5 | file:// storage works; shared across files or not; navigator.storage there | **Held, and shared**: all file:// pages share one origin (`file://`) and one store; navigator.storage, estimate() and persist() exist there; isSecureContext is true |
| 6 | Data survives a restart of a persistent profile | **Held** (http and file://), 3 of 3 |
| 7 | Timing of localStorage vs IndexedDB | **Measured**: IndexedDB put still blocks the main thread for the structured clone (15 ms for a 4 MB string, 56 ms for 40 MB); gets cost almost nothing on the main thread; localStorage cold read 41 ms |
| 8 | durability option accepted; default value | **Held**: all three accepted, unknown value is a TypeError, default `tx.durability` is `"default"`; "default" timed like "relaxed"; "strict" about 2.3 times slower |
| 9 | versionchange in A, blocked in B | **Held**, 6 of 6 runs |
| 10 | CompressionStream('gzip') exists; ratio and time | **Held**: ratio 0.226 (repetitive) and 0.344 (varied); 120 to 138 ms for 4 MB, and it **stalls the main thread** 86 to 131 ms |

---

## H1. localStorage's per-origin limit and its error

### Takeaway
In this Chromium the limit is exactly 5 Mi (5,242,880) UTF-16 code units per origin, counting keys and
values together, the same for Latin-1 and non-Latin-1 characters; exceeding it throws a DOMException
named `QuotaExceededError` with code 22.

### Cited Findings
- Binary search for the largest `setItem('k', 'a'.repeat(N))` that succeeds: N = **5,242,879** in runs 1, 2, 3 (spread 0); key + value = 5,242,880 = 5 x 1,048,576. N + 1 fails, N succeeds (both rechecked). — [e01_localstorage_quota.js](../experiments/local-storage/e01_localstorage_quota.js)
- The same search with U+4E00 (a character outside Latin-1): N = **5,242,879** in all 3 runs. The limit counts code units, not bytes on disk. — [e01](../experiments/local-storage/e01_localstorage_quota.js)
- With a 100-character key: max value 5,242,780 in all 3 runs, so key + value = 5,242,880: the key counts. — [e01](../experiments/local-storage/e01_localstorage_quota.js)
- Filling with several keys (4 keys of 1 Mi chars, then a top-up): total stored key + value = **5,242,880** in all 3 runs: the limit is per origin, not per item. — [e01](../experiments/local-storage/e01_localstorage_quota.js)
- The error, identical in all runs: `name` = `"QuotaExceededError"`, `code` = **22**, `instanceof DOMException` = true, message `"Failed to execute 'setItem' on 'Storage': Setting the value of 'k' exceeded the quota."` — [e01](../experiments/local-storage/e01_localstorage_quota.js)
- localStorage use does not appear in `navigator.storage.estimate()`: writing 4 MiB of localStorage moved `usage` by **0** bytes in all 12 runs of e03. — [e03_storage_estimate.js](../experiments/local-storage/e03_storage_estimate.js)

### Inferences
- A save that needs more than 5,242,880 code units of key + value across all of the origin's keys fails,
  whatever the characters; text with non-ASCII characters does not get a smaller limit here (it may in
  other engines, which were not tested).
- The app's existing failure path (`save3d`, `src/js/engine/core/objects-save.js:49-61`) catches the
  exception and toasts; any check on the error should test `name === 'QuotaExceededError'` (code 22 is the
  legacy number).

### Gaps
- Firefox and Safari limits and error names were not measured (not installed). Older engines are known
  to use other names (for example Firefox's historical `NS_ERROR_DOM_QUOTA_REACHED`); that is from
  memory, not tested here (U).

## H2. Large single values in IndexedDB

### Takeaway
A 50 MB ArrayBuffer and a 50 MB JSON string were stored and read back byte-identical, but a single
200 MB ArrayBuffer or string is refused: one value's serialized size may not exceed 133,169,152 bytes
(127 MiB). The same 200 MB is accepted, byte-identical, as a Blob or split into four 50 MB records.

### Cited Findings
- 50 MB (50,000,000 bytes / chars), 3 runs each, SHA-256 identical in every run — [e02_idb_large_values.js](../experiments/local-storage/e02_idb_large_values.js):

| Value | put to oncomplete (ms), runs 1-3 | mean | spread | get to onsuccess (ms), runs 1-3 | mean | spread |
|---|---|---|---|---|---|---|
| ArrayBuffer 50 MB | 195.3, 179.9, 187.6 | 187.6 | 15.4 | 105.6, 139.4, 110.5 | 118.5 | 33.8 |
| JSON string 50 MB | 289.0, 562.0, 265.3 | 372.1 | 296.7 | 116.9, 470.9, 117.9 | 235.2 | 354.0 |

- 200 MB, both kinds, all 3 runs: refused with `UnknownError` (not QuotaExceededError): `"The serialized keys and/or value are too large (size=200000068 bytes, max=133169152 bytes)."` (the string: size=200000064). The transaction aborts. — [e02](../experiments/local-storage/e02_idb_large_values.js)
- The ceiling by binary search on an ArrayBuffer (to 1 KiB): largest accepted **133,168,640 bytes**; the first refusal reports size 133,169,328 against max 133,169,152. Same in 3 shell runs and 1 run of the full Chromium binary. — [e02b_idb_value_ceiling.js](../experiments/local-storage/e02b_idb_value_ceiling.js)
- A string of U+4E00 characters: 66,000,000 characters accepted, 67,000,000 refused with size 134,000,050 bytes: such a string costs 2 bytes per character against the ceiling (a Latin-1 string, 1 byte). — [e02b](../experiments/local-storage/e02b_idb_value_ceiling.js)
- A 200,000,000-byte **Blob**: accepted in 4 of 4 runs; read back as a `Blob` of 200,000,000 bytes, SHA-256 identical. put to oncomplete 11.9, 9.8, 10.0 ms (shell) and 9.8 ms (full binary); get plus `blob.arrayBuffer()` 257.5, 229.9, 270.8 and 244.9 ms. — [e02b](../experiments/local-storage/e02b_idb_value_ceiling.js)
- 200 MB as **4 x 50 MB ArrayBuffers in one transaction**: accepted in 4 of 4 runs, reassembled SHA-256 identical. put 590.1, 620.4, 604.9, 583.8 ms; 4 gets 272.9, 274.2, 334.3, 273.8 ms. — [e02b](../experiments/local-storage/e02b_idb_value_ceiling.js)

### Inferences
- 133,169,152 = 127 x 1,048,576. The message wording suggests a fixed per-value limit on the serialized
  message, not the origin's quota; why it is 127 MiB was not read in Chromium's source (U).
- A project format that may exceed about 120 MB must not be one value: store a Blob, or chunk it into
  several records. A 50 MB single value is safe here.
- The 50 MB string runs had one slow outlier (run 2: 562 ms put, 471 ms get); the variance of string
  values is much higher than of buffers.

### Gaps
- Other engines' per-value limits were not tested. The Blob put returning in about 10 ms means the data
  was handed off by reference; whether its file is fully on disk at oncomplete was not tested separately
  (e06 and e08 cover survival for smaller values).

## H3. navigator.storage.estimate()

### Takeaway
estimate() reports quota, usage and a per-API breakdown; usage rose by the stored size (100,002,076
bytes on a profile, 100,167,680 in a fresh context, for a 100,000,000-byte write). The reported quota
here is not a share of the disk: it is usage plus a fixed headroom of 10 GiB on a persistent profile and
3 GiB (once 4 GiB) in a fresh incognito-like context.

### Cited Findings
- 3 runs per row, default headless shell ("shell") and full binary ("full") — [e03_storage_estimate.js](../experiments/local-storage/e03_storage_estimate.js):

| Browser / context | quota before (bytes), runs 1-3 | usage before | usage rise after 100,000,000-byte IndexedDB put | rise after 4 MiB localStorage | usage after deleting the record |
|---|---|---|---|---|---|
| shell, persistent profile | 10,737,418,240 x3 | 0, 0, 0 | 100,002,076 x3 | 0 x3 | 2,785 x3 |
| shell, newContext | 4,294,967,296; 3,221,225,472; 3,221,225,472 | 0, 0, 0 | 100,167,680 x3 | 0 x3 | 73,728 x3 |
| full, persistent profile | 10,737,418,240 x3 | 0, 0, 0 | 100,002,076 x3 | 0 x3 | 2,785 x3 |
| full, newContext | 3,221,225,472 x3 | 0, 0, 0 | 100,167,680 x3 | 0 x3 | 73,728 x3 |

- Quota moves with usage: after the 100 MB write, quota read 10,837,420,316 = 10,737,418,240 + 100,002,076 on the profile, and 3,321,393,152 = 3,221,225,472 + 100,167,680 in the fresh context; after the delete, 10,737,421,025 and 3,221,299,200. The same pattern appears on file:// in e05 (quota 3,221,299,200 with usage 73,728). — [e03](../experiments/local-storage/e03_storage_estimate.js); [e05_file_origin.js](../experiments/local-storage/e05_file_origin.js)
- 10,737,418,240 = 10 GiB; 3,221,225,472 = 3 GiB; 4,294,967,296 = 4 GiB. The disk had 31.0 GB free of 270.6 GB. — [e03](../experiments/local-storage/e03_storage_estimate.js)
- `usageDetails` is present: `{"indexedDB": 100002076}` (profile) and `{"indexedDB": 100167680}` (fresh). — [e03](../experiments/local-storage/e03_storage_estimate.js)
- localStorage is not counted: a 4 MiB localStorage write moved usage by 0 in all 12 runs. — [e03](../experiments/local-storage/e03_storage_estimate.js)

### Inferences
- Usage is accurate to within 0.2 % of the stored bytes (the fresh context rounds to larger blocks:
  after delete it keeps 73,728 = 72 KiB).
- Since quota is reported as usage + headroom, the app cannot learn the real free disk space from
  estimate() here; `quota - usage` is the number it can plan on (10 GiB on a profile in this build).
- Why the shell's first fresh-context run reported 4 GiB and every later fresh-context run 3 GiB is not
  known; each run launched its own browser (U).

### Gaps
- The rule behind the fixed headroom (a fingerprinting mitigation, a Chromium policy, or a headless
  default) was not read in Chromium's source or documents (U). Headed Chrome on a user's machine may
  report differently.

## H4. navigator.storage.persist() in headless Chromium

### Takeaway
For a localhost page, persist() returned `false` (and persisted() stayed `false`) with no grant and with
every permission Playwright's `grantPermissions` accepts; Playwright refuses the name
`persistent-storage`. Setting the permission through the Chrome DevTools Protocol made persisted() `true`
before any call and persist() return `true`.

### Cited Findings
- 3 runs of each cell, in a fresh context and in a persistent profile, in the shell and in the full binary (48 + 24 page loads); every cell gave the same result in every run — [e04_persist.js](../experiments/local-storage/e04_persist.js):

| Grant | grant call | permissions.query('persistent-storage') before / after | persisted() before | persist() returned | persisted() after |
|---|---|---|---|---|---|
| none | - | prompt / prompt | false | **false** | false |
| `grantPermissions(['notifications'])` | ok | denied / denied | false | **false** | false |
| `grantPermissions(['persistent-storage'])` | refused: `Unknown permission: persistent-storage` | prompt / prompt | false | **false** | false |
| `grantPermissions(['storage-access'])` | ok | denied / denied | false | **false** | false |
| CDP `Browser.setPermission({name:'persistent-storage'}, 'granted', origin)` | ok | granted / granted | **true** | **true** | true |
| CDP `Browser.grantPermissions(['durableStorage'], origin)` | ok | granted / granted | **true** | **true** | true |

- Granting any other permission with Playwright turned `persistent-storage` from "prompt" to "denied": Playwright's grant goes through CDP's grantPermissions, which rejects the permissions it is not given (observed effect; CDP's documentation not re-read here). — [e04](../experiments/local-storage/e04_persist.js)
- On file:// pages persist() also returned `false` with no grant (12 of 12 calls). — [e05_file_origin.js](../experiments/local-storage/e05_file_origin.js)

### Inferences
- With no grant, headless Chromium answers persist() at once with `false`, without a prompt; a suite can
  test the granted path only through CDP (`newBrowserCDPSession()` + `Browser.setPermission`).
- Headed Chrome decides persist() by heuristics (site engagement, bookmarks, installed app,
  notifications); none of that exists in a fresh headless profile, so these results say nothing about
  what a real user's Chrome will answer (U for headed).

### Gaps
- Headed Chrome, Firefox (which prompts) and Safari were not tested.

## H5. Storage from file:// pages

### Takeaway
On file:// both localStorage and IndexedDB work, and every file:// page shares one origin and one store:
a page in `a/one.html` and another in `b/deeper/two.html` saw each other's localStorage key and
IndexedDB record. navigator.storage, estimate(), persist() and persisted() all exist there, and the page
is a secure context.

### Cited Findings
- 3 runs in a fresh context and 3 in a persistent profile, all identical — [e05_file_origin.js](../experiments/local-storage/e05_file_origin.js):
  - `location.origin` = `"file://"` on both pages; `isSecureContext` = true; `navigator.storage` present; estimate(), persist(), persisted() present; `crypto.subtle` and `CompressionStream` present.
  - Page A wrote `from-A` (localStorage) and an IndexedDB record; page B, another file in another folder, read A's localStorage value and A's IndexedDB record (`idbSeesOther: "A"`), wrote its own; A then read B's (`idbSeesOther: "B"`). 6 of 6 runs.
  - estimate() on file://: quota 3,221,225,472 (fresh) / 10,737,418,240 (profile), usage 0 at first; persist() false, persisted() false.
- The built app booted from file:// with no page errors and wrote its keys there (see "The app at boot"). — [e11_app_boot_storage.js](../experiments/local-storage/e11_app_boot_storage.js)

### Inferences
- In this Chromium, every HTML file the user opens from disk shares storage with the offline
  `canvas_v10.html`: another local page can read or overwrite the app's projects, and two copies of the
  app in different folders see the same projects. A migration needs database names that will not
  collide with other local pages, and should not assume one copy per store.
- crypto.subtle being available on file:// means SHA-256 integrity checks work in the offline build here.

### Gaps
- Firefox treats each file:// as its own origin by default (from memory, U), and Safari's behaviour is
  not known here; neither could be tested. Chrome has command-line switches that change file:// access;
  only defaults were tested.

## H6. Survival across a browser restart

### Takeaway
With `launchPersistentContext`, a 1 MiB localStorage value and a 10 MB IndexedDB ArrayBuffer written on
http://localhost:47317 and on a file:// page were read back identical after closing and relaunching the
browser on the same profile, in 3 of 3 runs; a fresh context in the same browser saw none of it.

### Cited Findings
- After restart, 3 runs each, http and file://: localStorage length 1,048,576 (written 1,048,576); IndexedDB SHA-256 `abeef090...92f56194` equal to the written hash; usage 10,002,603 (http) and 10,002,525 (file://). — [e06_restart.js](../experiments/local-storage/e06_restart.js)
- Control: written in one `browser.newContext()`, closed, read in another: localStorage length 0, the database did not exist (`upgradeneeded` fired), usage 73,728. 3 of 3. — [e06](../experiments/local-storage/e06_restart.js)
- Abrupt death: 50 records per durability hint, each in its own committed transaction, then SIGKILL of the browser's processes found by profile path (2 processes matched each time, the browser process among them), relaunch: **50 of 50** survived under "relaxed" and under "strict" in 3 of 3 runs. — [e08_durability.js](../experiments/local-storage/e08_durability.js)

### Inferences
- A clean close and a killed browser both kept every committed transaction. The kill leaves the OS page
  cache intact, so this does not test power loss (where "relaxed" may lose the last transactions).
- The port is part of an http origin: the restart test needed a fixed port. The app's own dev and test
  servers will see different stores on different ports.

### Gaps
- Power loss, OS crash, and the browser clearing data under storage pressure (eviction of a
  non-persisted origin) were not and could not be tested here.

## H7. Main-thread cost: localStorage vs IndexedDB

### Takeaway
For a 4,008,905-character CAD-like JSON, JSON.stringify took 26 ms, localStorage.setItem 17 ms and the
first getItem after a browser restart 41 ms, all blocking. IndexedDB is not free on the main thread:
put() itself blocks for the structured clone (15 ms for the same string, 6 ms for a 4 MB buffer, 56 ms
for 40 MB); get() costs under 0.1 ms on the main thread, with the longest stall 1.3 ms or less.

### Cited Findings
- The object: 4,600 elements, each with id, type, layer, level, a property bag, 96 pseudo-random coordinates and 12 face indices; `JSON.stringify` = 4,008,905 characters (all runs). 5 runs, each a new persistent profile, times in ms — [e07_timing.js](../experiments/local-storage/e07_timing.js):

| Operation | runs 1-5 | mean | spread |
|---|---|---|---|
| JSON.stringify (4.0 MB) | 24.3, 21.3, 40.5, 21.6, 20.7 | 25.7 | 19.8 |
| JSON.parse | 18.3, 15.6, 36.8, 16.0, 17.3 | 20.8 | 21.2 |
| localStorage.setItem | 16.7, 16.5, 20.4, 16.1, 14.9 | 16.9 | 5.5 |
| localStorage.getItem, warm (just written) | 0.7, 0.4, 0.5, 0.7, 0.5 | 0.56 | 0.3 |
| localStorage.getItem, after page reload | 0.1, 0.0, 0.1, 0.1, 0.0 | 0.06 | 0.1 |
| localStorage.getItem, first after browser restart (cold) | 33.3, 34.0, 45.4, 53.2, 37.9 | 40.8 | 19.9 |
| IDB put(string): put() call | 15.6, 14.7, 15.5, 15.6, 14.6 | 15.2 | 1.0 |
| IDB put(string): to oncomplete | 22.3, 21.4, 23.8, 23.2, 20.5 | 22.2 | 3.3 |
| IDB put(string): longest main-thread stall | 15.7, 14.8, 15.7, 15.8, 14.7 | 15.3 | 1.1 |
| IDB get(string): to onsuccess | 3.0, 2.5, 2.8, 2.6, 2.6 | 2.7 | 0.5 |
| IDB get(string): longest stall | 1.4, 1.2, 1.4, 1.3, 1.1 | 1.3 | 0.3 |
| IDB put(4 MB ArrayBuffer): put() call | 7.5, 5.7, 6.0, 6.3, 6.2 | 6.3 | 1.8 |
| IDB put(4 MB): to oncomplete | 9.6, 7.4, 7.4, 8.0, 7.5 | 8.0 | 2.2 |
| IDB put(4 MB): longest stall | 7.6, 5.7, 6.1, 6.6, 6.3 | 6.5 | 1.9 |
| IDB get(4 MB): to onsuccess | 1.3, 1.3, 0.9, 1.3, 1.1 | 1.2 | 0.4 |
| IDB get(4 MB): longest stall | 0.4, 0.5, 0.3, 0.4, 0.4 | 0.4 | 0.2 |
| IDB put(40 MB ArrayBuffer): put() call | 65.7, 51.7, 55.5, 53.7, 52.9 | 55.9 | 14.0 |
| IDB put(40 MB): to oncomplete | 71.6, 57.0, 60.7, 59.5, 58.3 | 61.4 | 14.6 |
| IDB put(40 MB): longest stall | 66.2, 52.1, 57.7, 54.3, 53.5 | 56.8 | 14.1 |
| IDB get(40 MB): to onsuccess | 3.1, 2.6, 2.3, 2.4, 2.6 | 2.6 | 0.8 |
| IDB get(40 MB): longest stall | 1.2, 1.2, 1.1, 1.2, 1.1 | 1.2 | 0.1 |

- All get() calls themselves (the synchronous call) took 0.0 to 0.2 ms. — [e07](../experiments/local-storage/e07_timing.js)
- A first version of e07 (since replaced in the script) ran the same steps on a 2,177,881-character object in fresh incognito-like contexts: localStorage.setItem 8.4-9.2 ms; IDB get of 40 MB to onsuccess 25.2-31.7 ms (in memory) against 2.3-3.1 ms on a disk profile above. Those numbers are kept only as a note that context kind changes IndexedDB read times. — [e07](../experiments/local-storage/e07_timing.js)

### Inferences
- Moving to IndexedDB does not remove the main-thread cost of a save: JSON.stringify (26 ms) plus put()'s
  clone (15 ms) is about the same as stringify plus setItem (17 ms) for 4 MB. What it removes is the cold
  synchronous localStorage load at the first access (41 ms for 4 MB, growing with all of the origin's
  keys) and the 5 Mi-unit ceiling. Storing structured objects or ArrayBuffers instead of a JSON string
  would skip stringify, but put() would still clone on the main thread.
- The localStorage read after a page reload (0.06 ms) is fast because the renderer still had the
  origin's area in memory; only a browser restart shows the real cold cost.

### Gaps
- Not measured: a worker doing the stringify and put (would move the stall off the main thread),
  slower devices (phones), and other engines.

## H8. Transaction durability

### Takeaway
`db.transaction(store, 'readwrite', {durability: 'relaxed' | 'strict' | 'default'})` is accepted and
reported back by `tx.durability`; with no options the value is `"default"` (also for readonly); an unknown
value throws a TypeError. 200 small sequential transactions took about 53 ms under "relaxed" and
"default" and 123 ms under "strict".

### Cited Findings
- 3 runs, identical — [e08_durability.js](../experiments/local-storage/e08_durability.js): no options -> `tx.durability` `"default"`; `{durability:'relaxed'}` -> `"relaxed"`; `'strict'` -> `"strict"`; `'default'` -> `"default"`; readonly with no options -> `"default"`; `'durability' in IDBTransaction.prototype` = true; `{durability:'bogus'}` -> `TypeError: ... The provided value 'bogus' is not a valid enum value of type IDBTransactionDurability.`
- 200 sequential readwrite transactions of one 1 KB record each, persistent profile on disk — [e08](../experiments/local-storage/e08_durability.js):

| Hint | runs 1-3 (ms) | mean | spread |
|---|---|---|---|
| relaxed | 51.1, 52.6, 55.6 | 53.1 | 4.5 |
| strict | 113.4, 137.0, 119.7 | 123.4 | 23.6 |
| default (explicit) | 55.1, 57.7, 55.0 | 55.9 | 2.7 |
| no option | 52.0, 59.5, 64.7 | 58.7 | 12.7 |

- Committed data survived SIGKILL under both relaxed and strict, 50 of 50, 3 of 3 runs (see H6). — [e08](../experiments/local-storage/e08_durability.js)

### Inferences
- In this build "default" costs the same as "relaxed", so it likely behaves as relaxed (no flush per
  commit); that is inferred from timing, not read in the source (U). Code that must reach disk before it
  tells the user "saved" should ask for `'strict'` explicitly.
- On this machine's virtual disk a strict commit costs about 0.35 ms more than relaxed; on a phone's flash
  it may cost much more (not tested).

### Gaps
- Firefox and Safari support for the option and their defaults were not tested.

## H9. Two tabs and a version upgrade

### Takeaway
With page A holding version 1 open, page B's `open('e09', 2)` fired `versionchange` (old 1, new 2) in A,
then `blocked` (old 1, new 2) in B; when A closed 500 ms later, B got `upgradeneeded` and `success`. When A
closed inside its versionchange handler, B got no `blocked`. A's own close fired no `close` event.

### Cited Findings
- Event order with times in ms from A's first event, 3 runs per variant — [e09_multitab.js](../experiments/local-storage/e09_multitab.js):

| Variant | Run | A versionchange | B blocked | A closes | B upgradeneeded | B success |
|---|---|---|---|---|---|---|
| A closes 500 ms later | 1 | 4.7 | 4.9 | 505.2 | 506.0 | 506.5 |
| | 2 | 4.6 | 4.9 | 505.1 | 506.0 | 506.4 |
| | 3 | 4.9 | 5.2 | 505.3 | 506.3 | 506.6 |
| A closes in its handler | 1 | 4.2 | none | 4.2 | 4.7 | 5.1 |
| | 2 | 5.3 | none | 5.3 | 5.7 | 6.1 |
| | 3 | 3.6 | none | 3.6 | 4.1 | 4.4 |

- `oldVersion` and `newVersion` were 1 and 2 on every versionchange, blocked and upgradeneeded event; no `close` event fired on A in any run. — [e09](../experiments/local-storage/e09_multitab.js)

### Inferences
- versionchange reaches A before blocked reaches B (0.2 to 0.3 ms earlier), so closing in the
  versionchange handler avoids the block entirely; B then upgrades within about 0.5 ms. The app should
  close (and tell the user to reload) in every tab's versionchange handler, and handle `blocked` in the
  upgrading tab for tabs that do not answer.

### Gaps
- Cross-browser ordering was not tested; only two tabs in one context were tested (not two windows or a
  tab and a worker).

## H10. CompressionStream on CAD-like JSON

### Takeaway
CompressionStream and DecompressionStream exist, with 'gzip', 'deflate' and 'deflate-raw' ('brotli' and
'zstd' throw TypeError). gzip reached 0.226 of the size on a repetitive 4.1 MB model and 0.344 on a
varied 4.0 MB model, in 120 and 138 ms; decompression took 19 to 24 ms; round trips were exact. The
compression stalled the main thread for 86 to 131 ms.

### Cited Findings
- Formats: gzip, deflate, deflate-raw accepted; `new CompressionStream('brotli')` and `('zstd')` -> TypeError. — [e10_compression.js](../experiments/local-storage/e10_compression.js)
- Inputs: "repetitive", 6,000 elements whose vertex arrays come from 40 shared shapes offset to a grid, 4,124,639 UTF-8 bytes; "varied", the e07 model, 4,008,905 bytes. 5 runs each, times in ms, output sizes identical in every run — [e10](../experiments/local-storage/e10_compression.js):

| Input / format | out bytes | ratio | compress, runs 1-5 | mean | longest main-thread stall, runs 1-5 | decompress, runs 1-5 | mean |
|---|---|---|---|---|---|---|---|
| repetitive / gzip | 931,299 | 0.226 | 114.2, 114.4, 115.5, 145.5, 111.6 | 120.2 | 89.1, 89.0, 90.3, 115.1, 86.3 | 18.5, 20.5, 17.9, 21.5, 19.0 | 19.5 |
| repetitive / deflate | 931,287 | 0.226 | 107.6, 116.9, 113.0, 141.1, 118.4 | 119.4 | 86.7, 93.8, 91.8, 113.7, 90.5 | 17.3, 18.4, 17.6, 22.4, 18.0 | 18.7 |
| repetitive / deflate-raw | 931,281 | 0.226 | 106.7, 109.1, 105.4, 121.7, 106.0 | 109.8 | 86.4, 87.9, 84.5, 93.4, 85.2 | 17.3, 34.7, 19.0, 17.8, 17.2 | 21.2 |
| varied / gzip | 1,379,445 | 0.344 | 152.8, 138.6, 132.5, 133.8, 129.8 | 137.5 | 130.8, 111.2, 110.0, 111.1, 107.9 | 21.7, 22.4, 24.7, 28.0, 20.9 | 23.5 |
| varied / deflate | 1,379,433 | 0.344 | 136.6, 145.9, 143.8, 149.6, 138.7 | 142.9 | 110.1, 120.5, 116.3, 116.5, 115.6 | 23.7, 28.7, 22.2, 22.4, 23.7 | 24.1 |
| varied / deflate-raw | 1,379,427 | 0.344 | 155.8, 150.4, 156.0, 156.4, 135.0 | 150.7 | 125.6, 126.5, 126.5, 127.0, 108.1 | 22.9, 23.5, 22.4, 21.7, 20.5 | 22.2 |

- Every decompressed text equalled the input (30 of 30). — [e10](../experiments/local-storage/e10_compression.js)

### Inferences
- gzip cuts a 4 MB model to a quarter or a third, but in this build the work ran on the main thread
  (stalls of 86 to 131 ms, most of the compress time). Compressing on save belongs in a worker, or the
  stall must be accepted. The three formats differ only by their few header bytes.
- Compressed bytes would have to be stored in localStorage as text (base64 adds a third; packing two
  bytes per UTF-16 unit avoids that but is fragile); either way it only delays the 5 Mi-unit ceiling,
  so compression is useful for IndexedDB size and file export rather than as a way to keep localStorage.

### Gaps
- A CompressionStream inside a worker, and real BIM-Personal project files (none committed: the
  repository has no large sample project), were not measured.

## The app at boot (canvas_v10.html)

### Takeaway
Opened over http and from file://, the built app writes localStorage at boot: `acad3dDocsV1` (the
project list, 173 to 176 units) is present at the load event, and `acad3dV1` (the empty project, 28,260
to 28,261 units) appears within 5 seconds; no sessionStorage, no IndexedDB database, estimate().usage 0.

### Cited Findings
- 3 runs over http (served from localhost) and 3 from `file:///home/user/BIM-Personal/canvas_v10.html`, fresh context each, no page errors and no failed requests in any run; load 177 to 363 ms — [e11_app_boot_storage.js](../experiments/local-storage/e11_app_boot_storage.js):

| Origin | Run | after load | after 5 s | total after 5 s (units) |
|---|---|---|---|---|
| http | 1 | acad3dDocsV1: 173 | acad3dV1: 28,260; acad3dDocsV1: 173 | 28,433 |
| http | 2 | acad3dDocsV1: 176 | acad3dV1: 28,261; acad3dDocsV1: 176 | 28,437 |
| http | 3 | acad3dDocsV1: 176 | acad3dV1: 28,261; acad3dDocsV1: 176 | 28,437 |
| file | 1-3 | acad3dDocsV1: 176 | acad3dV1: 28,261; acad3dDocsV1: 176 | 28,437 |

- `acad3dV1` starts `{"objs":[],"cam":{"yaw":0,"pitch":1.52,"dist":30,...`: an empty project of about 28 K units. `acad3dDocsV1` starts `{"v":1,"active":"doc-...","open":["doc-..."`. — [e11](../experiments/local-storage/e11_app_boot_storage.js)
- In the source: `LSK='acad3dV1'` (`src/js/engine/core/state.js:1`), `A3D_DOCS_KEY='acad3dDocsV1'` and the per-project prefix `acad3dDocV1:` (`state.js:121`); the project is written by `save3d` (`src/js/engine/core/objects-save.js:52`), called through `saveSoon`'s 300 ms timer (`src/js/engine/bim/region-regenerate.js:84-85`); the list by `src/js/engine/ui/project-tabs.js:97` and `:108`; project switching writes `LSK` at `project-tabs.js:161` and `:180`. — the app's own code, read 2026-10-31

### Inferences
- An empty project already takes about 0.54 % of the 5 Mi-unit budget; parked projects (`acad3dDocV1:*`)
  share the same budget, so the number of projects the user can keep is bounded by their total size.
- A migration must read the three key families above on first run, and must handle the case of two app
  copies sharing one file:// store (H5).

### Gaps
- Which boot step calls saveSoon was not traced; the write is seen only as "between load and +5 s".

## Threats to validity

- One engine, one build (Chromium 153.0.8010.12), headless only, one Linux virtual machine with a fast
  virtual disk and 16 GB RAM. Firefox, Safari (macOS, iOS), Android Chrome and headed desktop Chrome were
  not tested; quota, persist() and timing are the results most likely to differ there.
- The quota figures (10 GiB / 3 GiB headroom) and the 127 MiB value ceiling are implementation details
  that can change between Chromium releases; the reason for each was not read in Chromium's source.
- Timings are small-sample (3 to 5 runs) on a shared virtual machine; single outliers (for example
  e02 run 2, e07 run 3) are kept in the raw numbers.
- The SIGKILL test cannot show what "relaxed" risks on power loss.
