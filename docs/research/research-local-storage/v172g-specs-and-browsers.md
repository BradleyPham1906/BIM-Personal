# V172g "files as the real save": specs and browser sources

Date: 2026-11-07. Read by a research agent (Claude), for phase V172g, under
`docs/research/research-protocol.md`. Levels: P = read in the primary source at a pinned commit (spec
text, browser source, curated compat data, the vendor's own release notes or bug tracker); S = dependable
secondary, or an inference from P code that was not run; U = search-summary or memory only, never used
by the code. Nothing here was run in a browser: every behaviour claim from browser source is what the
code says, not a measurement.

Downloads were kept as data under the session scratchpad (`specs/`), never run.

## Pinned sources

| Short name | Repository / URL | Commit or date |
|---|---|---|
| FSA | https://github.com/WICG/file-system-access `index.bs` | 93119927fa7a678c1863996f6f3a32d9ac53943d |
| FS | https://github.com/whatwg/fs `fs.bs` | d76d3455d5afe2f85754ed24ffdbf99fe30032d4 |
| COMP | https://github.com/whatwg/compression `index.bs` | 94b42518d2c2f97e64bd5a483d6deb8c8f14c365 |
| RFC1952 | https://www.rfc-editor.org/rfc/rfc1952.txt | fetched 2026-11-07 (RFCs are immutable) |
| CR | https://github.com/chromium/chromium | e72d336b09f61d197b626c2187d92ff27939b2cc |
| BCD | https://github.com/mdn/browser-compat-data | 82daeebf5a7073d55223a8cdb8aa54fb9416e27d |
| WK | https://github.com/WebKit/WebKit | 49106eb6c484fb3d2d80817e6957e341baa3b778 |
| FF | https://github.com/mozilla-firefox/firefox | db547b61903f9dee2ddb1a86de3beeab88b2c923 |
| WKBUG | https://bugs.webkit.org/rest/bug/263608 and `/comment` | fetched 2026-11-07 (last change 2026-05-19) |
| FX115 | https://www.mozilla.org/en-US/firefox/115.0/releasenotes/ | fetched 2026-11-07 |
| MOZPOS | https://github.com/mozilla/standards-positions `activities.yml` | f5bd8e4d050a4555f9a29c21d61c0e577ed4b1e6 |
| WKPOS | https://github.com/WebKit/standards-positions `summary.json` | 86c1e3cb359101e6cbc3f13a41352bc459a53cb9 |

Raw file URLs have the form `https://raw.githubusercontent.com/<org>/<repo>/<sha>/<path>`.

## Search log

| Where | Query or path | What came back | Kept / set aside |
|---|---|---|---|
| git ls-remote | HEAD of the 8 repositories above | commit SHAs | kept (pins) |
| FSA | `index.bs`, grep extension, transient activation, opaque, permission, suggestedName, id, startIn | 1145 lines; the suffix rules, picker gate, permission algorithms | kept |
| FS | `fs.bs` (the path `index.bs` 404s; the file is `fs.bs`) | 1778 lines; createWritable, [[buffer]], close/abort, getFile | kept |
| COMP | `index.bs` | 226 lines; formats, gzip rules, [Exposed=*] | kept |
| RFC1952 | rfc-editor.org text | 675 lines | kept |
| CR | `third_party/blink/renderer/modules/file_system_access/global_file_system_access.cc` | suffix and id validation, picker gate | kept |
| CR | `content/browser/file_system_access/file_system_access_file_handle_impl.cc`, `..._file_writer_impl.cc`, `..._safe_move_helper.cc` | .crswap creation, close = Safe Browsing check + move | kept |
| CR | `storage/browser/file_system/native_file_util.cc`, `base/files/file_util_posix.cc`, `file_util_win.cc` | MOVE = base::Move = rename() / MoveFileEx | kept |
| CR | `third_party/blink/renderer/platform/weborigin/security_origin.{h,cc}`, `url/origin.cc`, `services/network/public/cpp/is_potentially_trustworthy_unittest.h`, `file_system_access_manager_impl.cc` | file:// origin is a tuple origin, potentially trustworthy | kept (S: inference) |
| CR | `services/network/public/cpp/is_potentially_trustworthy.cc` | 404 (the code now lives in `net/`) | set aside; used the unittest instead |
| CR | `chrome/browser/file_system_access/chrome_file_system_access_permission_context.cc`, `file_system_access_features.cc`, `content/.../file_system_access_handle_base.cc` | activation for prompts; persistent permissions feature | kept |
| CR | `storage/browser/quota/quota_settings.cc`, `quota_manager_impl.cc`, `quota_features.cc` | incognito pool; static reported quota | kept |
| CR | `third_party/blink/renderer/modules/compression/inflate_transformer.cc` | truncated / junk errors | kept |
| BCD | `api/Window.json`, `FileSystemHandle.json`, `FileSystemFileHandle.json`, `FileSystemWritableFileStream.json`, `CompressionStream.json`, `DecompressionStream.json`, `Worker.json`, `html/elements/a.json`, `IDBFactory.json` | version data | kept; IDBFactory has no private-browsing note (set aside) |
| WK | `NetworkStorageManager.cpp`, `OriginQuotaManager.cpp`, `WebsiteDataStore.h`, `WebsiteDataStoreCocoa.mm`, `LocalStorageManager.cpp`, `MemoryStorageArea.cpp`, `IDBStorageManager.cpp`, `StorageMap.cpp`, `Modules/compression/DecompressionStreamDecoder.cpp` | ephemeral quota and in-memory stores | kept |
| WK | a "safe download" rule for gzip | not looked for file by file; WebKit has no such list in the files read | set aside (see U) |
| WKBUG | REST bug and comments 263608 | 8 comments, status NEW, InRadar | kept |
| FF | `modules/libpref/init/StaticPrefList.yaml`, `dom/quota/ActorsParent.cpp` | pref `dom.indexedDB.privateBrowsing.enabled` true; private persistence type; 50% disk limit | kept |
| FX115 | Firefox 115 release notes | "IndexedDB is now also supported in private browsing ..." | kept |
| developer.mozilla.org | Firefox/Releases/115 | page fetched, no matching sentence found by grep | set aside |
| MOZPOS / WKPOS | File System Access position | Mozilla: negative (issue 154); WebKit: oppose (issue 28) | kept (counter-evidence) |

## 1. File System Access pickers (WICG)

| Finding | Evidence (URL@sha, lines) | Level | Confidence |
|---|---|---|---|
| A valid suffix code point is ASCII alphanumeric, `+` or `.`; the note names compound extensions such as `.tar.gz` as the reason `.` is allowed. | FSA@93119927 index.bs 84-90 | P | high |
| "validate a suffix": must start with `.`; only valid suffix code points; must not end with `.`; length more than 16 throws TypeError. The 16 counts the leading dot. So `.acad3d.json` (12), `.json.gz` (8) and `.acad3d.json.gz` (15) are all valid; more than one dot is allowed. | FSA@93119927 index.bs 500-512; also 392-395 | P | high |
| An empty accepts-options list (all types filtered out and excludeAcceptAllOption true) throws TypeError. | FSA@93119927 index.bs 494 | P | high |
| `excludeAcceptAllOption` defaults to false; when false an "all files" option is appended. | FSA@93119927 index.bs 311, 404-407, 489-492 | P | high |
| `id` is a "valid path id": ASCII alphanumeric, `_` or `-`, at most 32 characters, else TypeError; the UA should remember at least 16 ids per origin. | FSA@93119927 index.bs 589-596, 628-631 | P | high |
| `startIn` is a WellKnownDirectory (desktop, documents, downloads, music, pictures, videos) or a FileSystemHandle (its parent directory is used for a file handle). An explicit `id` with a remembered path wins over a WellKnownDirectory `startIn`. | FSA@93119927 index.bs 302-313, 513-584, 635-650 | P | high |
| `suggestedName` pre-fills the save dialog; its interaction with `types` is implementation-defined; a UA should ignore or sanitize a dangerous name as it does for downloads. | FSA@93119927 index.bs 321, 808-817 | P | high |
| "is allowed to show a file picker": opaque origin rejects with SecurityError; cross-origin to top-level rejects; no transient activation throws SecurityError. | FSA@93119927 index.bs 362-376 | P | high |
| requestPermission when the state is "prompt" needs a Window global and transient activation, else SecurityError; same-origin with top-level required. queryPermission needs no activation. | FSA@93119927 index.bs 135-156, 240-250, 277-288 | P | high |
| A handle read back from IndexedDB "is also likely to return prompt"; after that the site must call requestPermission (needs a click). | FSA@93119927 index.bs 218-222, 259-261 | P | high |
| Handles are [Serializable] (so can be stored in IndexedDB and posted same-origin only); clearing browsing data is expected to clear stored handles. | FS@d76d3455 fs.bs 329, 358-372, 426, 471-472; FSA@93119927 index.bs 199, 1080-1082, 1097-1098 | P | high |
| Chromium implements the same suffix rules: `IsValidSuffixCodePoint` = alnum or `+` or `.`; errors "must start with '.'", "contains invalid characters", "must not end with '.'", "cannot be longer than 16 characters". The leading dot is then stripped before passing to the browser. | CR@e72d336b global_file_system_access.cc 53-55, 61-82, 102-108 | P | high |
| Chromium id rule: `_`/`-`/alnum, max 32 characters. | CR@e72d336b global_file_system_access.cc 57-59, 84-99 | P | high |
| Chromium picker gate: sandboxed or opaque origin ("Sandboxed documents aren't allowed...", "This document isn't allowed..."), cross-origin subframe, and "Must be handling a user gesture to show a file picker." | CR@e72d336b global_file_system_access.cc 168-204; security_origin.h 258 (`CanAccessFileSystem() { return !IsOpaque(); }`) | P | high |
| Chromium permission prompt without transient activation returns outcome kNoUserActivation (no prompt). | CR@e72d336b chrome_file_system_access_permission_context.cc 1390-1396; file_system_access_handle_base.cc 225-302, 324 | P | high |
| Chromium persistent permissions ("allow on every visit") are behind `kFileSystemAccessPersistentPermissions`, disabled by default on Android, enabled elsewhere. | CR@e72d336b chrome/browser/file_system_access/file_system_access_features.cc 24-30 | P | medium (the non-Android branch was read only as the `#else`) |

## 2. WHATWG File System: createWritable

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Changes made through the stream are not reflected in the file until the stream is closed; the UA tries to ensure no partial writes ("old contents or whatever data was written ... until closed"); typically a temporary file replaces the entry on close. | FS@d76d3455 fs.bs 524-534 | P | high |
| `keepExistingData` defaults to false: the temporary file starts empty; true copies the existing file into [[buffer]] first. | FS@d76d3455 fs.bs 423, 536-538, 586-589 | P | high |
| Writes go to [[buffer]] (expected to be a temporary file); close() runs implementation-defined malware / Safe Browsing checks (failure rejects with AbortError) and then sets the file's binary data to [[buffer]]; a note says this is expected to update the file on disk atomically. | FS@d76d3455 fs.bs 1122-1127, 1155-1186 | P | high |
| abort() only releases the lock; the file entry's data is never touched, so the original survives. | FS@d76d3455 fs.bs 1189-1192 | P | high |
| createWritable takes a shared lock; a sync access handle cannot be created until close. | FS@d76d3455 fs.bs 540-544 | P | high |
| getFile() sets File.lastModified to the entry's modification timestamp; entries may be changed by applications outside the spec, and how that is reflected is not fully defined. So comparing lastModified (and size) before a save is the available check, with no guarantee. | FS@d76d3455 fs.bs 128-133, 193-199, 485-512 | P | high (rule) / medium (as a detector) |

## 3. Chromium: validation, swap file, file://

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Extension validation lives in Blink, not the browser process: `VerifyIsValidExtension` (max length 16). | CR@e72d336b third_party/blink/renderer/modules/file_system_access/global_file_system_access.cc 61-82 | P | high |
| The swap file is a sibling named `<name>.crswap` (then `<name>.1.crswap`, ... up to `max_swap_files_`). On Android, for content:// URIs the swap file is written in the app cache dir (`FileSystemAPISwap`) and "copied back" on close. | CR@e72d336b content/browser/file_system_access/file_system_access_file_handle_impl.cc 729-761 | P | high |
| On close, `FileSystemAccessSafeMoveHelper` moves swap to destination after "after write" checks (Safe Browsing, required when the extensions differ, which they do against `.crswap`) and quarantine (mark-of-the-web). Failure: "Blocked by Safe Browsing." The swap file is deleted on writer destruction only when close failed. | CR@e72d336b file_system_access_file_writer_impl.cc 59-75, 140-150, 266-294; file_system_access_safe_move_helper.cc 222-238, 276-318 | P | high |
| The move is `NativeFileUtil::CopyOrMoveFile` MOVE -> `base::Move` -> POSIX `rename()` (atomic replace within one filesystem; falls back to copy+delete if rename fails) or Windows `MoveFileEx(MOVEFILE_COPY_ALLOWED | MOVEFILE_REPLACE_EXISTING)`. | CR@e72d336b storage/browser/file_system/native_file_util.cc 299-367; base/files/file_util_posix.cc 1777-1800; base/files/file_util_win.cc 1577-1590 | P (code) / S (atomicity is OS semantics) | high on desktop same-volume; low for the Android content-URI copy-back and the copy fallback |
| file:// pages: Blink's picker gate checks only opacity, cross-origin and activation. `url::Origin` serialises file origins as `file://` (a tuple origin, not opaque), and Chromium's own tests treat `file:///...` as potentially trustworthy, so the browser-side `BindReceiver` check (`IsOriginPotentiallyTrustworthy`) passes. So the code says pickers can be used from file:// in Chromium. | CR@e72d336b global_file_system_access.cc 168-204; url/origin.cc 138-155; services/network/public/cpp/is_potentially_trustworthy_unittest.h 211-213; content/browser/file_system_access/file_system_access_manager_impl.cc 614-625 | S (inference from P code, not run) | medium |

## 4. Compression Streams

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Formats: brotli (RFC 7932), deflate (RFC 1950), deflate-raw (RFC 1951), gzip (RFC 1952). | COMP@94b42518 index.bs 19, 31-80 | P | high |
| gzip: compliant per RFC 1952 2.3.1.2; CM must be 8; FHCRC, CRC32, ISIZE mismatches are errors; MTIME/XFL/OS ignored; only one member allowed; additional input after the member is an error. | COMP@94b42518 index.bs 59-71 | P | high |
| Truncated input: at flush, "If the end of the compressed input has not been reached, then throw a TypeError". Trailing data: TypeError (line 149). The readable side errors, so a half-written .gz file is detected. | COMP@94b42518 index.bs 145-149, 153-158 | P | high |
| Both CompressionStream and DecompressionStream are `[Exposed=*]` (windows and all workers). | COMP@94b42518 index.bs 83, 123 | P | high |
| Chromium throws "Compressed input was truncated." and "Junk found after end of compressed data."; WebKit checks extra bytes and incomplete input the same way. | CR@e72d336b third_party/blink/renderer/modules/compression/inflate_transformer.cc 93, 108, 147-158; WK@49106eb6 Source/WebCore/Modules/compression/DecompressionStreamDecoder.cpp 89-107 | P | high |

## 5. RFC 1952

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| ID1 = 31 (0x1f), ID2 = 139 (0x8b) identify gzip. | RFC1952 lines 243, 289-292 | P | high |
| A gzip file is a series of members appearing one after another, with nothing before, between or after; each member ends with CRC32 and ISIZE. (The Compression standard narrows this to one member.) | RFC1952 lines 233-236, 276, 419-430 | P | high |
| A compliant decompressor must check ID1, ID2 and CM. | RFC1952 lines 464-472 | P | high |

## 6. Browser support (MDN browser-compat-data)

All from BCD@82daeebf; "mirror" means the same as the upstream browser (Safari iOS = Safari, Edge = Chrome,
Chrome Android = Chrome where marked). File and line of each key given.

| Feature (file:line) | Chrome | Chrome Android | Firefox | Safari | Safari iOS | Level | Conf. |
|---|---|---|---|---|---|---|---|
| Window.showSaveFilePicker (api/Window.json:7278) | 86 | 132 | no | no | no | P | high |
| Window.showOpenFilePicker (api/Window.json:7238) | 86 | 132 | no | no | no | P | high |
| FileSystemHandle.queryPermission (api/FileSystemHandle.json:184) | 86 | 109 | no | no | no | P | high |
| FileSystemHandle.requestPermission (api/FileSystemHandle.json:252) | 86 | 109 | no | no | no | P | high |
| FileSystemFileHandle.createWritable (api/FileSystemFileHandle.json:107) | 86 | 109 | 111 | 26 | 26 | P | high |
| FileSystemWritableFileStream (api/FileSystemWritableFileStream.json:3) | 86 | 109 | 111 | 26 | 26 | P | high |
| CompressionStream, "gzip" (api/CompressionStream.json:3, 240) | 80 | 80 | 113 | 16.4 | 16.4 | P | high |
| DecompressionStream, "gzip" (api/DecompressionStream.json:3, 240) | 80 | 80 | 113 | 16.4 | 16.4 | P | high |
| Worker (api/Worker.json:3) | 2 | 2 | 3.5 | 4 | 5 | P | high |
| `<a download>` (html/elements/a.json:180) | 14 (cross-origin not since 65) | 14 | 20 | 10.1 | 13 | P | high |

Notes: showSaveFilePicker and the permission methods are flagged experimental in BCD. Firefox and Safari
have createWritable only for the origin private file system (no pickers), so it cannot write a user's
file there. Brotli in CompressionStream: Firefox 147, Safari 18.4, Chrome not yet (BCD
api/CompressionStream.json, "brotli" entry). BCD Firefox Android note for `download`: the filename
only affects `blob:` and `data:` URLs.

## 7. WebKit private browsing, downloads, bug 263608

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| An ephemeral session has an empty storage path; IndexedDB then uses an in-memory backing store (`MemoryIDBBackingStore` or `SQLiteMemoryIDBBackingStore`). | WK@49106eb6 Source/WebKit/NetworkProcess/storage/IDBStorageManager.cpp 343-348; NetworkStorageManager.cpp 192-193 | P | high |
| Ephemeral localStorage is a `MemoryStorageArea` created with `StorageMap::noQuota`; persistent localStorage is a SQLite area with a 5 MB quota. So a private window accepts more than 5 MB of localStorage where a normal one throws QuotaExceededError: a page can observe this. | WK@49106eb6 LocalStorageManager.cpp 38-40, 195-203; MemoryStorageArea.cpp 39-41; Source/WebCore/storage/StorageMap.cpp 106 | P (code) / S (observable effect not run) | medium |
| Origin quota: with an origin-quota ratio (Safari: 0.6 of volume capacity for a full browser, 0.15 for apps) the quota is ratio x volume capacity of `m_path`; when the capacity is unknown, as for an empty path, the quota stays at the default per-origin quota, 1000 MB, and quota increases go to the UI process. Reported quota = min(quota, standard reported quota), where standard = 128 GB (Mac) or 64 GB (iOS) x ratio, doubling with usage. So estimate().quota in a Safari private window is expected near 1000 MB against tens of GB in a normal window. | WK@49106eb6 NetworkStorageManager.cpp 101-102, 752-786; OriginQuotaManager.cpp 175-185; WebsiteDataStore.h 433-441; WebsiteDataStoreCocoa.mm 80-83, 937-945 | P (code) / S (that `volumeCapacity("")` fails, not run) | medium |
| No eviction is performed for an ephemeral session. | WK@49106eb6 NetworkStorageManager.cpp 625-626 | P | high |
| No WebKit code was found that decides "safe" downloads for gzip; that decision ("open safe files after downloading") belongs to Safari, which is closed source. | not found in the files read | U (absence) | low |
| WebKit bug 263608 "TXT and XML Files open in tab on iOS Safari instead of downloading": status NEW, component DOM, version Safari 16, InRadar (rdar 117435170), last change 2026-05-19. Comments report the same for PDF blobs and images; comment 6 says the fault is in Safari, tracked internally. Comment 7 (2026-05-19) gives a workaround: re-wrap the Blob as `application/octet-stream` before `a.download`. `application/json` is not discussed. The workaround is a user's claim, not tested by WebKit. | WKBUG comments 0-7 | P (tracker) / U (workaround effect) | high (status) / low (workaround) |

## 8. Private-window quota in Chromium and Firefox

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Chromium incognito quota pool = physical memory x a random ratio between 0.15 and 0.2; per-origin (storage key) quota = pool / 3. | CR@e72d336b storage/browser/quota/quota_settings.cc 31-49, 54-61 | P | high |
| But what pages see is static: with `kStaticStorageQuota` (enabled by default), `CalculateReportedQuota` returns usage + 10 GiB when the disk is 10 GiB or more OR the profile is incognito. So navigator.storage.estimate().quota no longer tells an incognito window from a normal one on ordinary disks. Writes still fail at the real (memory-based) quota. | CR@e72d336b storage/browser/quota/quota_manager_impl.cc 135-153, 1155-1196, 1300-1320; storage/browser/quota/quota_features.cc 37-38 | P | high |
| Chromium incognito keeps the quota database in memory. | CR@e72d336b quota_manager_impl.cc 1726-1728 | P | high |
| Firefox: IndexedDB in private browsing is on by default (`dom.indexedDB.privateBrowsing.enabled: true`), stored encrypted on disk under a `private` repository and cleared when the last private context exits. | FF@db547b61 modules/libpref/init/StaticPrefList.yaml 3554-3558; dom/quota/ActorsParent.cpp 292, 304, 1846-1864, 1970-1971 | P | high |
| Since Firefox 115: "IndexedDB is now also supported in private browsing without memory limits thanks to encrypted storage on disk ... keys ... held in RAM only". | FX115 release notes | P (vendor notes) | high |
| Firefox's temporary-storage limit is 50% of disk capacity (or a fixed pref, or a spoofed value under resist-fingerprinting); private storage is counted in the same group eviction. | FF@db547b61 dom/quota/ActorsParent.cpp 1428-1455, 2229-2290 | P (code) / S (that the private limit equals the normal one) | medium |

## Counter-evidence

- Mozilla's position on File System Access is "negative" (MOZPOS activities.yml 701-710, issue 154) and
  WebKit's is "oppose" (WKPOS summary.json, issue 28). Pickers will not arrive in Firefox or Safari on
  any planned date; the download path stays the only "save to a file" there. (P, high)
- Atomic replace is not guaranteed everywhere: the spec only says "expected" and "try to ensure"
  (FS 528-534, 1179-1180); Chromium on Android content URIs copies the swap file back; POSIX `base::Move`
  falls back to copy+delete when rename fails (e.g. across volumes). A crash or kill between create and
  close leaves a `.crswap` file next to the user's file, because the purge runs only in the writer's
  destructor (CR file_writer_impl.cc 59-75). (P code / S effect, medium)
- Close can fail after all writes succeeded: Safe Browsing ("Blocked by Safe Browsing.") or quarantine
  failure aborts the move (CR safe_move_helper.cc 276-296), and the spec allows this (FS 1171-1173).
  The app must treat close() as the commit point and keep its own copy until close resolves. (P, high)
- Chrome on Android lists showSaveFilePicker only from 132, but createWritable from 109 (BCD); the two
  differ by 23 versions, so feature-detect each, not one. (P, high)
- The incognito-detection premise in question 8 is contradicted for Chromium by the static reported
  quota (above). For Safari the code still suggests a difference (about 1000 MB against tens of GB); this
  has not been measured and WebKit may change it, so it must not gate behaviour. (P/S, medium)
- Safari iOS bug 263608 shows `a.download` does not always download; it opens text-like types in a
  tab. Whether `application/json` or gzip Blobs are affected is not discussed in the bug. (P, high)
- RFC 1952 allows several members; the Compression standard forbids it. A .gz made by concatenating
  members (some tools do) will fail DecompressionStream. (P, high)

## Still U (not to reach the code)

- Whether `showSaveFilePicker` works from a file:// page in a shipping Chrome: inferred from code (S),
  not run.
- That a Safari private window really reports about 1000 MB from estimate() and accepts more than
  5 MB of localStorage: inferred from code, not measured.
- Whether `application/octet-stream` (or `application/gzip`) Blobs download rather than open in a tab on
  iOS Safari: a user comment only.
- Safari's list of "safe" file types after download, and how it treats `.gz`: closed source, not found.
- The exact Firefox version history before 115 of private-browsing IndexedDB (BCD has no note).
- Chrome Android's handling of multi-dot extensions in the Android picker (extensions go to the OS as
  MIME types there); not read.
