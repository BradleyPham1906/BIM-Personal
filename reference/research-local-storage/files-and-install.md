# Saving to real files, large binary storage, and installing the app (research 2026-10-31)

Scope: how this ES5, zero-dependency browser app (served from GitHub Pages under
`https://bradleypham1906.github.io/BIM-Personal/` as hashed files, and also as one
`canvas_v10.html` opened from `file://`) can (a) save and reopen project files on the user's
disk, (b) store large binary data, (c) be installed and work offline. Today it saves projects only in
localStorage; it already downloads PNGs and other bytes through `bimTriggerDownload` (Blob, `<a download>`,
revoke after 1 s) in `src/js/engine/annotation/annotation-pick.js:181`.

Evidence levels follow `reference/research-protocol.md`: **P** read in the primary source (the
specification text, the vendor's own document or release note, MDN's browser-compat-data JSON, a
browser's own bug tracker, or measured here); **S** a dependable secondary (gap stated); **U** a
search-engine summary only (planning only, never code). All pages read 2026-10-31 unless stated.
Measurements: `reference/experiments/local-storage/e12_files_install_surface.js`, run in
Chromium 153.0.8010.12 (Playwright 1.63.0, build chromium-1243, headless), results JSON in the
session scratch directory (`LS_EXP_SCRATCH`), numbers copied below.

Research question: which mechanism should the app use for (a), (b), (c) in each browser it must run
in (desktop Chrome/Edge, Firefox, Safari macOS, iOS/iPadOS Safari, Android Chrome), and from
`file://`? A good answer must decide: the primary save path and its fallback per browser; where large
binaries go; whether to add a manifest and a service worker, and how they behave under the Pages
subpath; and what would lose a user's data.

Hypotheses (each can be proved wrong):
- H1 The File System Access pickers (`showOpenFilePicker`/`showSaveFilePicker`) exist only in
  Chromium; Firefox and Safari have none and have said they will not ship them. **Held** (P).
- H2 File handles can be kept in IndexedDB for a "recent files" list, but reopening one prompts again
  unless Chrome's persistent permission applies. **Held** (P), with a measured test-harness caveat.
- H3 The pickers are refused from `file://` (the spec rejects an opaque origin). **Failed in Chromium**
  (measured): Chromium reaches the picker from `file://`. Spec and implementation disagree.
- H4 OPFS works in every current engine, including Safari, and counts against the same quota as
  IndexedDB. **Held** (P), except Safari Private Browsing (WebKit's own post).
- H5 Chrome no longer requires a service worker for installation. **Held for the menu install**
  (Chrome 108 mobile / 112 desktop); the automatic install prompt still wanted a fetch handler as of
  the post (P).
- H6 A service worker cannot work on `file://`. **Held** (P spec, measured).
- H7 Installing changes eviction: Safari home-screen/Dock apps escape the 7-day cap; Chrome grants
  `persist()` to installed sites. **Held** (P, Chrome via a 2020 page: S on currency).
- H8 `CompressionStream('gzip')` is in all current engines and shrinks project JSON several-fold.
  **Held** (P support; measured 9.3x on a synthetic model).

## (a) Saving and reopening project files on the user's disk

### Takeaway
Only Chromium browsers (Chrome/Edge 86+ desktop, Chrome Android 132+) have the save/open pickers that
let the app write back to the same file; Mozilla rates the API "negative" and WebKit "oppose", so for
Firefox and Safari (macOS and iOS) the path is download (`<a download>` + Blob URL) to save and
`<input type=file>` to open, which the app already half has. Feature-detect `showSaveFilePicker`, and
keep the download path as the general case, not an afterthought.

### Cited Findings
Specification and status
- The File System Access API is a "Draft Community Group Report, 10 October 2025" of the WICG; "It is
  not a W3C Standard nor is it on the W3C Standards Track." Editor Ming-Ying Chung (Google). (P) —
  [WICG File System Access, header and Status](https://wicg.github.io/file-system-access/)
- The pickers are `[SecureContext]`; the steps "verify that an environment is allowed to show a file
  picker": if the origin "is an opaque origin" reject with SecurityError; if the origin is not same
  origin with the top-level origin reject with SecurityError; if no transient activation, throw
  SecurityError. (P) — [WICG FSA §3.1/§3.2, "verify that an environment is allowed to show a file picker"](https://wicg.github.io/file-system-access/)
- The base interfaces (`FileSystemHandle`, `FileSystemFileHandle`, `FileSystemWritableFileStream`,
  OPFS) moved to the WHATWG File System Living Standard, "Last Updated 19 October 2026"; the WICG
  document "extends the API in [FS]" with pickers and permissions. (P) — [WHATWG File System, header](https://fs.spec.whatwg.org/); [WICG FSA abstract](https://wicg.github.io/file-system-access/)

Browser support (MDN browser-compat-data, `main` branch, read raw 2026-10-31; "mirror" means Edge
follows Chrome and iOS follows Safari)
- `Window.showOpenFilePicker`, `showSaveFilePicker`, `showDirectoryPicker`: Chrome 86, Edge mirror,
  **Chrome Android 132**, Firefox `false`, Safari `false` (so iOS `false`); flagged experimental. (P) —
  [BCD api/Window.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/Window.json)
- `FileSystemHandle.queryPermission`/`requestPermission`: Chrome 86, Chrome Android 109, Firefox and
  Safari `false`. `FileSystemHandle.remove` Chrome 110 only (non-standard). (P) —
  [BCD api/FileSystemHandle.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/FileSystemHandle.json)
- `FileSystemFileHandle.createWritable` / `FileSystemWritableFileStream`: Chrome 86, Chrome Android
  109, Firefox 111, **Safari 26**; in Firefox and Safari these reach only OPFS files, since those
  browsers have no picker to give a user-visible handle (inference from the two rows above). (P) —
  [BCD api/FileSystemFileHandle.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/FileSystemFileHandle.json); [BCD api/FileSystemWritableFileStream.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/FileSystemWritableFileStream.json)
- Safari 26.0 release notes: "support for the File System WritableStream API, enabling direct writing
  to files within the user's file system." (P; the wording says "user's file system" but Safari ships
  no picker, so in practice this is OPFS — see the counter-evidence below) — [WebKit, Safari 26.0 features](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/)
- Chrome's article: supported "on most Chromium browsers on Windows, macOS, ChromeOS, Linux, and
  Android. A notable exception is Brave where it is currently only available behind a flag." (P, page
  last updated 2024-08-19) — [Chrome for Developers, File System Access API](https://developer.chrome.com/docs/capabilities/web-apis/file-system-access)

Vendor positions
- Mozilla standards-positions #154 "File System Access API": position **negative**. Rationale: "There's
  a subset of this API we're quite enthusiastic about (in particular providing a read/write API for files
  and directories as alternative storage endpoint), but it is wrapped together with aspects for which we
  do not think meaningful end user consent is possible to obtain (in particular cross-site access to the
  end user's local file system). Overall we consider this harmful therefore". #738 "Implement subset of
  File System Access API" is **defer**; #562 "AccessHandles for the Origin Private File System" is
  **positive**. (P, the repository's data file) — [mozilla/standards-positions merged-data.json](https://raw.githubusercontent.com/mozilla/standards-positions/gh-pages/merged-data.json)
- WebKit standards-positions #28 "File System Access": position **oppose**, concerns ["security"],
  topics storage and app-like capabilities. WebKit #534 "write-only permission mode" is "blocked". (P,
  the repository's data file) — [WebKit/standards-positions summary.json](https://raw.githubusercontent.com/WebKit/standards-positions/main/summary.json)

Handles in IndexedDB, "recent files", and permission re-prompts
- Handles are `[Serializable]`; "a handle retrieved from IndexedDB is also likely to return 'prompt'"
  for its permission; writing then "will require user activation and will result in a confirmation
  prompt." (P) — [WICG FSA §2.3 queryPermission](https://wicg.github.io/file-system-access/)
- Chrome's article: "The web app can continue to save changes to the file without prompting until all
  tabs for its origin are closed. Once a tab is closed, the site loses all access. The next time the user
  uses the web app, they will be re-prompted." Write permission on an existing file needs a prompt, and
  "can only be triggered by a user gesture"; the browser may refuse system folders. (P, 2024-08-19) —
  [Chrome, FSA "Permission persistence"](https://developer.chrome.com/docs/capabilities/web-apis/file-system-access)
- Chrome 122 persistent permissions: a three-way prompt "Allow this time / Allow on every visit / Don't
  allow" is shown when the app retrieves a stored handle from IndexedDB on a later visit and calls
  `requestPermission()`; and "The user must have installed the app. Installed apps will automatically
  persist permissions once the user grants access. In this case, the three-way prompt won't be shown".
  "There are no developer-facing changes". VS Code for the web stores handles in IndexedDB
  (`vscode-web-db` / `vscode-filehandles-store`). (P, page dated 2024-01-09) —
  [Chrome blog, Persistent permissions for the FSA API](https://developer.chrome.com/blog/persistent-permissions-for-the-file-system-access-api)
- Spec privacy note: user agents are encouraged to "automatically expire permission grants except for
  particularly well trusted origins (for example persistent permissions could be limited to 'installed'
  web applications)"; clearing browsing data clears stored handles. (P) — [WICG FSA §5.2](https://wicg.github.io/file-system-access/)

Iframes and file://
- Spec §5.3: in third-party contexts (an iframe whose origin differs from the top frame) sites cannot
  get new files or request more permissions; handles post-message only to same-origin destinations. (P)
  — [WICG FSA §5.3](https://wicg.github.io/file-system-access/)
- Measured (e10): a cross-origin iframe (top `127.0.0.1`, frame `localhost`) calling
  `showSaveFilePicker` after a click: `SecurityError: ... Cross origin sub frames aren't allowed to show a
  file picker.` (P, measured, Chromium 153)
- Measured (e10): on `file://`, `self.origin` is `"null"`, `isSecureContext` is `true`, all three
  pickers exist, and `showSaveFilePicker()` after a click ends in `AbortError: The user aborted a
  request` — the same result as on `http://localhost` — not the spec's SecurityError for an opaque
  origin. Headless Chromium cannot show the dialog and aborts it, so the test shows Chromium does not
  stop `file://` at the origin check; it does not show a save completing. (P, measured; the full
  save from `file://` in headed Chrome is untested here)

Fallbacks for Firefox and Safari
- `<a download>`: "download only works for same-origin URLs, same-origin blob:, and data: schemes"; for
  other URLs the attribute is ignored. (P, MDN) — [MDN, `<a>` element, download](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a)
- `URL.createObjectURL` is not available in service workers; release with `revokeObjectURL()`. (P, MDN)
  — [MDN, URL.createObjectURL](https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL_static)
- Chromium blob limits (its own README): in-memory limit 2 GB on 64-bit desktop, `physical_memory/100`
  on Android; disk limit `disk_size/10` on desktop, `6*disk_size/100` on Android; larger blobs page to
  disk. Example: "Android Fat, 2 GB RAM: in-memory 20 MB, disk limit 1.9 GB". (P) —
  [Chromium storage/browser/blob/README.md, "Blob Storage Limits"](https://chromium.googlesource.com/chromium/src/+/main/storage/browser/blob/README.md)
- Measured (e10): a 64 MiB Blob URL `<a download="project.bim">` click saved 67,108,864 bytes on
  `http://localhost`; an 8 MiB one saved on `file://`, suggested name `project.bim` both times. (P,
  measured, Chromium only)
- WebKit bug 212279 "Revoking an object URL immediately after triggering navigation causes navigation
  to fail": RESOLVED FIXED (r262085, 2020); it was the cause of iOS bug 211234 (Blob download ignored
  `download`). The app's 1 s delay before revoking is the safe pattern either way. (P) —
  [WebKit bug 212279](https://bugs.webkit.org/show_bug.cgi?id=212279)
- WebKit bug 263608 "TXT and XML Files open in tab on iOS Safari instead of downloading": status NEW,
  opened 2023-10-24, last changed 2026-05-19; a commenter's workaround is to recreate the Blob with type
  `application/octet-stream`. (P for the bug's existence and status; the workaround is one user's report)
  — [WebKit bug 263608](https://bugs.webkit.org/show_bug.cgi?id=263608)

Counter-evidence and problems found
- The WICG issue #289 thread (2021-2025): "there's no workaround to the requirement that the user give
  permission to access the file on each new session start" (2021); Chromium does not support
  `requestPermission()` from a worker (a-sully, 2023-01-09, "a Chromium implementation issue"). Chrome
  122's persistent permissions answer the first point only for the cases listed above. (S: read through
  a fetch tool's summary of the GitHub page, which the shell's proxy refused) —
  [WICG/file-system-access #289](https://github.com/WICG/file-system-access/issues/289)
- WebKit bug 231706 "Implement File System standard" is REOPENED (changed 2025-10-17); its last comments
  are developers asking how to get a WritableStream and being pointed to OPFS
  (`navigator.storage.getDirectory()`), consistent with Safari having no picker. (P) —
  [WebKit bug 231706](https://bugs.webkit.org/show_bug.cgi?id=231706)
- **Test-harness fault (measured):** in an off-the-record Playwright context (`browser.newContext()`),
  reading a `FileSystemFileHandle` back out of IndexedDB closed the whole browser in Chromium 153, in
  both the headless shell and full Chromium; the same steps pass in a persistent profile
  (`launchPersistentContext`): the handle came back as `FileSystemFileHandle`, `isSameEntry` true, file
  readable. Whether a real Incognito window does the same is untested. (P, measured; `probe3.js` /
  `probe5.js` were scratch probes, the finding is kept in e10's comments)

### Inferences
- Plan for three tiers: Chromium desktop gets "Save" that writes back to the same `.bim` through a
  stored handle, with "Save As" through `showSaveFilePicker`; Chrome Android 132+ gets the pickers too,
  per BCD (behaviour on Android not tested here); Firefox, Safari and iOS get "Download" (Blob URL) and
  "Open" (`<input type=file accept=".bim">`). A Firefox/Safari user cannot overwrite in place, so the app
  should say plainly that each save is a new download.
- The recent-files list should store the handle in IndexedDB and call `requestPermission({mode:
  'readwrite'})` only inside a click handler; it must not assume the grant survives a reload unless the
  app is installed (Chrome 122+).
- Because `file://` pages in Chromium reach the pickers, the offline single file can keep "Save to
  file" in Chrome/Edge; this rests on one measured behaviour that the spec contradicts, so it must stay
  behind feature detection and a try/catch that falls back to download.
- The app's suites will need persistent-profile contexts for any test that stores handles in
  IndexedDB, or they will crash the browser (measured).
- ES5 constraint: these APIs return Promises and `createWritable` returns a stream object; all of it
  is callable from ES5 with `.then()`, no `async`/`await` needed (the e10 page code is ES5).

### Gaps
- Not tested: a full save and reopen in headed Chrome from `file://` and from Pages; Chrome Android
  132's picker UI; Edge's persistent-permission behaviour (assumed to follow Chromium, U).
- Not found: a primary statement of iOS Safari's maximum download size for a Blob URL, or where iOS
  puts the file (Files app "Downloads"); only bug reports.
- `support.mozilla.org` answered with a JavaScript challenge page, so Firefox's own help article was
  not read.

## (b) Storing large binary data: the Origin Private File System versus IndexedDB

### Takeaway
OPFS (`navigator.storage.getDirectory()`) is in Chrome 86+, Firefox 111+, Safari 15.2+ (iOS 15.2+), and
the fast synchronous handle (`createSyncAccessHandle`, dedicated workers only) in Chrome 102+, Firefox
111+, Safari 15.2+; it counts against the same origin quota and is evicted with the rest of the origin's
data, so it is a faster file-shaped store, not a safer one. Measured here, a 64 MiB write was of the
same order through OPFS and IndexedDB (about 100 ms each); the case for OPFS is in-place partial writes
and a file-shaped API, not raw speed for whole-blob saves.

### Cited Findings
- Support: `StorageManager.getDirectory` Chrome 86, Chrome Android 109, Firefox 111, Safari 15.2;
  `FileSystemFileHandle.createSyncAccessHandle` Chrome 102, Firefox 111, Safari 15.2; sync-returning
  `close/flush/getSize/truncate` Chrome 108, Firefox 111, Safari 16.4; `createSyncAccessHandle` `mode`
  option Chrome 121 only; `StorageManager.estimate` Safari 17; `usageDetails` Chrome only;
  `persist/persisted` Chrome 55, Firefox 57, Safari 15.2. (P) —
  [BCD api/StorageManager.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/StorageManager.json); [BCD api/FileSystemSyncAccessHandle.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/FileSystemSyncAccessHandle.json); [BCD api/FileSystemFileHandle.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/FileSystemFileHandle.json)
- WebKit (2022-02-14): OPFS available on macOS 12.2+ and iOS 15.2+; `getFile()` from macOS 12.4/iOS
  15.4; "The API is currently unavailable for Safari windows in Private Browsing mode"; "its storage
  lifetime is the same as other persistent storage types like IndexedDB and localStorage";
  `FileSystemSyncAccessHandle` "is only available in Worker". (P) —
  [WebKit blog, The File System API with Origin Private File System](https://webkit.org/blog/12257/the-file-system-access-api-with-origin-private-file-system/)
- WHATWG FS: `createSyncAccessHandle()` is `[Exposed=DedicatedWorker]`; writes that exceed "the
  storage quota" reject/throw `QuotaExceededError`; "Storage quota only applies to files stored in a
  bucket file system" (i.e. OPFS, not user-picked files). (P) — [WHATWG File System §2.3.3, §3](https://fs.spec.whatwg.org/)
- web.dev (2023-06-08): OPFS "is subject to browser quota restrictions. When a user clears all browsing
  data or all site data, the origin private file system will be deleted, too"; "there are no
  permissions prompts and no Safe Browsing checks"; sync APIs in workers "can be faster as they avoid
  having to deal with promises"; moving OPFS files to the user-visible file system is not possible,
  copying is. (P, Chrome's team) — [web.dev, The origin private file system](https://web.dev/articles/origin-private-file-system)
- MDN: writes to user-visible files go through security checks (Safe Browsing in Chrome) and "are not
  in-place", so "these operations are fairly slow"; OPFS "doesn't require the same series of security
  checks and permission grants and is therefore faster". No numbers given. (S: a claim without a
  benchmark) — [MDN, Origin private file system](https://developer.mozilla.org/en-US/docs/Web/API/File_System_API/Origin_private_file_system)
- Quotas (MDN, last modified 2026-01-05): quotas apply "to an entire origin, even if this origin is used
  to run several websites, such as https://example.com/site1/ and https://example.com/site2/"; Chromium
  origin up to 60% of disk; Firefox best-effort 10% of disk or 10 GiB group limit, persistent up to 50%
  capped at 8 TiB; WebKit browser apps ~60% per origin, overall 80%. (P for MDN's statement; MDN is
  secondary to each engine) — [MDN, Storage quotas and eviction criteria](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria)
- WebKit storage policy (2023-08-10), Safari 17 / iOS 17 / macOS Sonoma: origin quota up to 60% of disk
  for a browser app, 15% for other apps; overall 80% / 20%; cross-origin frames get 10% of the main
  frame's quota; eviction is per origin, least-recently-used; persistent-mode origins are excluded;
  "WebKit currently grants a request based on heuristics like whether the website is opened as a Home
  Screen Web App." (P) — [WebKit blog, Updates to Storage Policy](https://webkit.org/blog/14403/updates-to-storage-policy/)
- Measured (e10, Chromium 153, `http://localhost`, persistent profile, 64 MiB, 3 runs):
  OPFS `createWritable` + `write(Blob)` + `close`: mean 121.4 ms (111.6-127.5, sd 8.6);
  IndexedDB `put(Blob)`: mean 96.8 ms (88.7-101.2, sd 7.0);
  worker `createSyncAccessHandle` 4 MiB chunked writes + flush: 284, 146.3, 71.8 ms (mean 167.4,
  sd 107.7; includes worker start-up, first run slowest). `estimate()` after one run: usage 134,224,590
  B split `fileSystem` 67,109,020 / `indexedDB` 67,115,570; quota 10,871,642,830 B. (P, measured; one
  machine, one engine, headless)
- Measured (e10): `navigator.storage.getDirectory()` on `file://` rejects with `SecurityError` in
  Chromium; in a cross-origin iframe it succeeds (partitioned storage). (P, measured)

Counter-evidence
- The "OPFS is faster" claim (MDN, web.dev) is about in-place, byte-range writes (SQLite-style); for a
  whole-file save of a Blob, the measurement here found IndexedDB no slower. No vendor benchmark was
  found that contradicts or supports this for whole-blob writes.
- Safari Private Browsing has no OPFS (WebKit 2022 post); whether that still holds in Safari 26 was not
  re-checked against a newer WebKit statement.

### Inferences
- The Pages origin `bradleypham1906.github.io` is shared by every Pages project of that account and by
  the old builds the site keeps under `v/<version>/` (see `tools/build_site.py`): they all share one
  quota, one localStorage, one IndexedDB and one OPFS. Keys and directory names must be namespaced (for
  example an OPFS directory `BIM-Personal/`), and an old build opened from `v/` can read and overwrite
  the current build's data.
- OPFS is not a substitute for a file on disk: clearing site data deletes it, and it is evicted with the
  origin. It suits caches of large binaries (imported meshes, textures, terrain tiles) that the project
  file can rebuild; the project itself still needs a real file (a) or `persist()`.
- `file://` loses OPFS entirely in Chromium (measured), so the offline single file must keep large
  binaries in IndexedDB or inside the saved project file.

### Gaps
- No measurement in Firefox or Safari (only Chromium is installed here).
- Behaviour when quota is exceeded mid-write in each engine (the spec says the write leaves the buffer
  unmodified) was not tested.

## (c) Installing the app and working offline

### Takeaway
Any site can be installed: the W3C manifest draft says so, Safari 17 (macOS Dock) and Safari 26
(iOS/iPadOS) need no manifest at all, and Chrome needs a manifest with name, 192 px and 512 px icons,
start_url and display, over HTTPS — and since Chrome 108 (mobile) / 112 (desktop) no service worker for
the menu install. Offline still needs a service worker, which works on GitHub Pages under the
`/BIM-Personal/` subpath (HTTPS is automatic for `github.io`) and never on `file://`. Installing does help
storage: WebKit exempts home-screen/Dock apps from the 7-day script-storage cap and uses
"opened as a Home Screen Web App" as a `persist()` heuristic; Chrome grants `persist()` to installed or
bookmarked sites, and Chrome 122 persists file permissions for installed apps.

### Cited Findings
Manifest and installability
- Web Application Manifest: "W3C Working Draft 26 October 2026"; editor's draft says "Any website is an
  installable web application", and the user agent may provide a way to install it. (P) —
  [W3C TR appmanifest](https://www.w3.org/TR/appmanifest/); [editor's draft, "Installable web applications"](https://w3c.github.io/manifest/)
- Chrome's criteria for `beforeinstallprompt` and the install promotion: not already installed; user
  clicked or tapped at least once and spent at least 30 seconds on the page; HTTPS; manifest with
  `short_name` or `name`, `icons` with a 192 px and a 512 px icon, `start_url`, `display` one of
  fullscreen/standalone/minimal-ui/window-controls-overlay; `prefer_related_applications` absent or
  false. "Users can install your web app even if it doesn't meet the PWA installability criteria". (P,
  2024-09-19) — [web.dev, What does it take to be installable?](https://web.dev/articles/install-criteria)
- Chrome dropped the fetch-handler requirement "for installation from the menu, since version 108 on
  mobile and 112 on Desktop", and launched "a default custom page for sites that don't implement their
  own" offline page; "For now the algorithm that displays the install prompt still requires the
  presence of a fetch() handler". (P, 2023-12-05; whether the prompt rule changed since was not found) —
  [Chrome blog, Update to install criteria](https://developer.chrome.com/blog/update-install-criteria)
- BCD: manifest `display`, `icons`, `start_url`: Chrome 39 (with the note that each is "required for a
  web app to be installable"), Safari 17 (macOS), Safari iOS 11.3 (`icons` iOS 15.4, used only when no
  `apple-touch-icon`), Firefox desktop `false`, Firefox Android 47. (P) —
  [BCD manifests/webapp/display.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/manifests/webapp/display.json); [icons.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/manifests/webapp/icons.json)
- Safari 17 (2023-09-18): "You can add a website — any website — to your Dock" (File > Add to Dock);
  it opens as a web app "even if the site does not have a manifest file"; "Safari will copy the
  website's cookies to the web app... Safari does not copy over any other kind of local storage. After a
  user adds a web app to the Dock, no other website data is shared". (P) —
  [WebKit, Safari 17.0 features, "Web apps on Mac"](https://webkit.org/blog/14445/webkit-features-in-safari-17-0/)
- Safari 26 (iOS/iPadOS 26): "By default, every website added to the Home Screen opens as a web app";
  "there are now zero requirements for 'installability' in Safari"; Home Screen web apps "never required
  Service Workers". (P) — [WebKit, Safari 26.0 features](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/)
- Firefox 143 (2025-09-16): "On Windows, Firefox now supports running websites as web apps pinned
  directly to the taskbar... This feature is not currently available for Firefox installs from the
  Microsoft Store." No macOS/Linux mention. BCD still lists Firefox desktop manifest support as `false`.
  (P) — [Firefox 143.0 release notes](https://www.firefox.com/en-US/firefox/143.0/releasenotes/); meta bug
  [Bugzilla 1915736 Taskbar Tabs](https://bugzilla.mozilla.org/show_bug.cgi?id=1915736) (U, seen in search only)

Storage and installing
- WebKit (2020-03-24): ITP deletes "all of a website's script-writable storage after seven days of
  Safari use without user interaction on the site"; "Web applications added to the home screen are not
  part of Safari and thus have their own counter of days of use... We do not expect the first-party in
  such a web application to have its website data deleted." (P) —
  [WebKit blog, Full third-party cookie blocking and more](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/)
- MDN: Safari's proactive eviction deletes script-created data of an origin with no click or tap in the
  last seven days of browser use; eviction deletes all of an origin's data at once. (P for MDN) —
  [MDN, Storage quotas and eviction criteria, "Proactive eviction"](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria)
- WebKit: a standalone web app (Home Screen on iOS, Dock on macOS) "has the same origin quota and
  overall quota as when it is opened in a browser app"; `persist()` granted on heuristics such as being
  opened as a Home Screen Web App. (P) — [WebKit, Updates to Storage Policy](https://webkit.org/blog/14403/updates-to-storage-policy/)
- Chrome grants `persist()` automatically or silently denies it, by site engagement, "Has the site been
  installed or bookmarked?", notification permission; Firefox asks the user with a popup. (S: the page
  is dated 2020-05-12, so current Chrome behaviour is not confirmed) —
  [web.dev, Persistent storage](https://web.dev/articles/persistent-storage)
- Measured (e10): on `http://localhost`, not installed, `persisted()` false and `persist()` resolved
  false in headless Chromium 153. (P, measured; says nothing about an installed app)

Service worker, offline and the Pages subpath
- Service Workers spec (Editor's Draft 29 October 2026): register rejects with TypeError if the script
  or scope URL scheme "is not one of 'http' and 'https'", and with SecurityError if the script's origin is
  not potentially trustworthy; a script at `/~bob/sw.js` can control `/~bob/` but not `/`, unless the
  server sends `Service-Worker-Allowed`. (P) — [W3C Service Workers, Register algorithm and §6.5 Path restriction](https://w3c.github.io/ServiceWorker/)
- Measured (e10): on `file://`: `TypeError: Failed to register a ServiceWorker: The URL protocol of the
  current origin ('null') is not supported.` On `http://localhost`, `sw/sw.js` registered for
  `/app/sw/` and `/app/sw/deeper/`, and was refused for `/app/` ("not under the max scope allowed").
  (P, measured)
- GitHub Pages: "GitHub Pages sites created after June 15, 2016, and using github.io domains are served
  over HTTPS automatically"; HTTPS can be enforced for custom domains. Pages sets no custom headers, so
  `Service-Worker-Allowed` is not available (U: inferred, no GitHub page read that says it). (P for the
  quote) — [GitHub Docs, Securing your GitHub Pages site with HTTPS](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https)
- Update flow (Chrome's team): an update check happens on navigation and at most a day apart for
  functional events; Chrome 68+ ignores HTTP caching headers when checking the SW script; a worker is
  updated if "byte-different"; the new worker waits until no client uses the old one, unless
  `skipWaiting()`, which means it "is likely controlling pages that were loaded with an older version".
  (P for Chrome) — [web.dev, The service worker lifecycle](https://web.dev/articles/service-worker-lifecycle)

File handling and launch handling
- `file_handlers` manifest member: Chrome 102 desktop only; Chrome Android, Firefox, Safari `false`;
  spec in WICG manifest incubations. `LaunchQueue`: Chrome 102, Chrome Android `false`. `launch_handler`
  (`client_mode`): Chrome 110. (P) — [BCD manifests/webapp/file_handlers.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/manifests/webapp/file_handlers.json); [BCD api/LaunchQueue.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/LaunchQueue.json); [BCD launch_handler.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/manifests/webapp/launch_handler.json)
- Chrome: "File Handling is currently limited to desktop operating systems"; each handler has an
  `action` URL within the app's scope and an `accept` map of MIME type to extensions; files arrive
  through `launchQueue.setConsumer(function (launchParams) {...})` as `FileSystemFileHandle`s; a
  permission prompt is shown before the app can view the file, every time until the user picks Allow or
  Block or ignores it three times. (P, page updated 2020-10-22, older than the shipping version) —
  [Chrome, Let installed web applications be file handlers](https://developer.chrome.com/docs/capabilities/web-apis/file-handling)
- `launch_handler.client_mode` values `auto` (default), `navigate-new`, `navigate-existing`,
  `focus-existing`. (P, 2021-12-14) — [Chrome, Launch Handler API](https://developer.chrome.com/docs/web-platform/launch-handler)
- Positions: Mozilla #158 "File Handling" **defer**; #567 and WebKit #90 "Web App Launch Handling" no
  position. (P) — [mozilla merged-data.json](https://raw.githubusercontent.com/mozilla/standards-positions/gh-pages/merged-data.json); [WebKit summary.json](https://raw.githubusercontent.com/WebKit/standards-positions/main/summary.json)
- Measured (e10): `window.launchQueue` is an object even on a plain, uninstalled page and on `file://`
  in Chromium 153, so its presence does not mean the page was launched with files. (P, measured)

Compression
- `CompressionStream` / `DecompressionStream` with `gzip`, `deflate`: Chrome 80, Firefox 113, Safari 16.4
  (iOS 16.4); `deflate-raw` Chrome 103; `brotli` Firefox 147, Safari 18.4, Chrome `false`; `zstd` Firefox
  138 behind a flag only. Mozilla position on Compression Streams: positive. (P) —
  [BCD api/CompressionStream.json](https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/CompressionStream.json); [mozilla merged-data.json #207](https://raw.githubusercontent.com/mozilla/standards-positions/gh-pages/merged-data.json)
- Measured (e10, Chromium 153, a synthetic 60,000-element BIM-like JSON of 8,007,274 bytes): gzip to
  860,941 bytes (ratio 0.108, about 9.3x smaller), about 99-117 ms to compress, 29-33 ms to decompress,
  round trip identical; same on `file://` and on `http://localhost`. (P, measured; real project JSON
  will compress differently)

Counter-evidence and problems found
- WebKit bug 232302 "Service worker and storage deleted after 7 days on Web application added to Home
  Screen" (iOS 15.0.2, 2021): RESOLVED WONTFIX; WebKit's answer: "There is no way to get an exception in
  Safari. If you adjust your manifest to use either the 'standalone' or 'fullscreen' display mode, your
  home screen web application will open full-screen in Web.app and you will get the behavior you want."
  So the exemption needs a standalone/fullscreen web app, not a `minimal-ui` one that opens in Safari.
  (P) — [WebKit bug 232302](https://bugs.webkit.org/show_bug.cgi?id=232302)
- WebKit bug 181850 "Cross-origin storage in 'Add to home screen' apps always lost": NEW since
  2018-01-19, last changed 2022-06-21. Does not affect a same-origin app like this one. (P) —
  [WebKit bug 181850](https://bugs.webkit.org/show_bug.cgi?id=181850)
- Safari's web apps do not see Safari's storage (macOS Dock: only cookies copied, P above). For iOS the
  same separation is reported by developers (a Stack Overflow thread found by search), not in a WebKit
  document read here. (U for iOS) — search pointer only
- Chrome's installability documents disagree in age: the criteria page (2024-09-19) no longer lists a
  service worker, the update post (2023-12-05) says the prompt still needs a fetch handler. Which one
  governs the prompt today is not settled by what was read.

### Inferences
- A manifest at `/BIM-Personal/manifest.webmanifest` with `scope` and `start_url` `/BIM-Personal/`,
  `display: standalone`, 192/512 PNG icons is enough for Chrome/Edge install, and improves Safari's.
  It is pure JSON and an ES5-safe `<link rel="manifest">`; no dependency.
- An offline service worker must sit at `/BIM-Personal/sw.js` (not inside `app/`), or its scope will
  stop at `/BIM-Personal/app/` (path restriction, measured; Pages cannot send `Service-Worker-Allowed`,
  U). Its scope then also covers `/BIM-Personal/v/<version>/` old builds; the fetch handler should leave
  those alone or cache them deliberately.
- With hashed file names (`app/engine.<hash>.js` etc.), a cache-first strategy is safe for those files;
  `index.html` must be network-first, or users will run an old build until the worker updates. The
  worker script itself needs a version string that changes each build, or it will not be byte-different
  and will not update.
- Without a service worker, Chrome's installed app shows its default offline page when offline, so
  "installed" and "works offline" are separate deliverables. `canvas_v10.html` from `file://` remains the
  only offline path in Firefox desktop and wherever the user does not install.
- `.bim` double-click opening (file_handlers + launchQueue) is Chrome/Edge desktop only, behind an extra
  permission prompt; it is an enhancement for installed Chromium users, never the main path.
- A gzip step on save (feature-detected, raw JSON otherwise) should shrink project files and downloads
  several-fold in all three engines since Safari 16.4; the saved file needs a header or extension rule so
  the loader knows whether to decompress (for example, sniff the gzip magic bytes 1F 8B).

### Gaps
- No live check of an installed app's behaviour (install UI cannot run headless here): whether Chrome
  now auto-grants `persist()` to installed apps, and whether Chrome 122 persistent file permissions apply
  to the Pages app once installed.
- Firefox taskbar web apps: whether they read the manifest, their storage relation to the Firefox
  profile (search summaries say they are tied to the creating profile, U), and macOS/Linux plans were
  not read in a Mozilla primary source (SUMO page refused, see below).
- iOS 26 home-screen web app storage: no WebKit statement read on whether data entered in Safari is
  visible in the web app on iOS (macOS is documented: not shared).

## Method: search log, sources fetched, refused hosts

Search log (where, query, result, kept/rejected)
1. Shell, raw.githubusercontent.com, MDN browser-compat-data `main`: api/Window, FileSystemFileHandle,
   FileSystemHandle, FileSystemSyncAccessHandle, FileSystemWritableFileStream, FileSystemDirectoryHandle,
   StorageManager, CompressionStream, LaunchQueue, Cache, ServiceWorker, ServiceWorkerContainer,
   manifests/webapp/{display, display_override, file_handlers, icons, launch_handler, scope, start_url},
   html/elements/a. All 200 except `manifests/webapp.json` and `api/NavigatorStorage.json` (404, wrong
   paths). Kept: version rows, parsed with a script that only reads JSON.
2. Shell, wicg.github.io/file-system-access, fs.spec.whatwg.org, w3c.github.io/manifest,
   w3.org/TR/appmanifest, w3c.github.io/ServiceWorker, wicg.github.io/manifest-incubations: all 200;
   read status, picker checks, permission text, quota notes, register algorithm, path restriction.
3. Shell, developer.chrome.com: FSA article, persistent-permissions blog, update-install-criteria blog,
   file-handling (200 at `/docs/capabilities/web-apis/file-handling`; 404 at
   `/docs/web-platform/best-practices/file-handling` and `/docs/capabilities/pwa-file-handling`),
   launch-handler; web.dev install-criteria, origin-private-file-system, storage-for-the-web,
   persistent-storage, service-worker-lifecycle. Kept all, with each page's "Last updated" date.
4. Shell, webkit.org blog posts 10218 (7-day cap), 12257 (OPFS), 14403 (storage policy), 14445
   (Safari 17), 17333 (Safari 26). Kept.
5. Shell, standards positions: `github.com/mozilla/standards-positions/issues/154` refused (403, proxy);
   used the repositories' data files instead: mozilla `gh-pages/merged-data.json`, WebKit
   `main/summary.json`. Kept: #154, #158, #207, #562, #738 and WebKit #28, #49, #90, #238, #534.
6. Shell, firefox.com 143.0 release notes: kept the taskbar web apps paragraph.
   support.mozilla.org `use-web-apps-firefox-windows`: returned a "Client Challenge, JavaScript is
   disabled" page; rejected (not readable).
7. WebSearch "Firefox taskbar tabs web apps Windows release notes 143": pointed to the release notes
   (then read, P) and Bugzilla 1915736 (not read; U).
8. WebSearch "iOS home screen web app storage separate from Safari IndexedDB lost": pointers to WebKit
   bugs 181850 and 232302 (then read as XML, P), a Stack Overflow mirror and a Reddit snapshot
   (rejected: unofficial copies), a vendor blog (rejected: secondary marketing).
9. WebSearch "iOS Safari blob URL download attribute bug.webkit.org": pointers to WebKit bugs 190351,
   211234, 263608 (263608 and 212279 read as XML, P; 190351 not read, rejected as a 2018 regression with
   a known fix path).
10. WebSearch "File System Access API requestPermission every reload complaint github issue WICG":
    pointer to WICG #289, read through WebFetch (S: tool summary, the shell proxy refuses github.com).
11. Shell, bugs.webkit.org `show_bug.cgi?id=N&ctype=xml` for 263608, 212279, 232302, 181850, 231706:
    all 200; kept titles, status, dates and first/last comments.
12. Shell, chromium.googlesource.com `storage/browser/blob/README.md?format=TEXT`: kept the limits table.
13. Repository: `grep` of `src/` for serviceWorker, manifest, showSaveFilePicker, CompressionStream,
    navigator.storage, indexedDB: none; `a.download` in annotation-pick.js, zoom-window-save-image.js,
    viewports.js. `tools/build_site.py`: Pages keeps old builds at `v/<version>/`.

Refused or unusable hosts from this environment: `github.com` web pages through curl (403 from the
agent proxy); `gh api` for repositories not attached to this session (403, "GitHub access to this
repository is not enabled"); `support.mozilla.org` (JavaScript challenge). GitHub-hosted raw copies
(raw.githubusercontent.com) and Bugzilla XML worked instead.

Confidence
- Picker support and vendor positions (H1): **high** — BCD and both vendors' own position files agree,
  and WebKit's bug thread points users to OPFS.
- Handles in IndexedDB and re-prompts (H2): **high** for the spec and Chrome 122 rules (Chrome's own
  posts); **medium** for current Chrome detail, as the FSA article (2024) still says "re-prompted",
  written for the non-persistent case.
- Pickers from `file://` in Chromium (H3 failed): **medium** — measured, but only up to the dialog
  (headless aborts it) and contrary to the spec; no Chromium document read that states it.
- OPFS support and quota (H4): **high** — BCD, WebKit, WHATWG and MDN agree. OPFS-vs-IDB speed:
  **low-medium** — one engine, one machine, 3 runs, whole-blob writes only.
- Install criteria (H5): **medium** — two Chrome pages of different dates do not fully agree on the
  prompt.
- Service worker on `file://` and subpath scope (H6): **high** — spec text plus measurement.
- Storage benefits of installing (H7): **high** for WebKit (two WebKit posts, one WONTFIX bug that
  states the condition); **low-medium** for Chrome's `persist()` auto-grant (a 2020 page, untested
  installed).
- Compression (H8): **high** for support (BCD, Mozilla positive); **medium** for the ratio (synthetic
  data).
