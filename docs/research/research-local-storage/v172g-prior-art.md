# V172g prior art: files as the real save

Research date: 2026-11-07. Phase V172g, "files as the real save": the app will (a) mark each project that has
changes not yet saved to a file and remind the user after 30 minutes, and at the first save in Safari or a private
window; (b) Save and Open through the File System Access pickers in Chrome and Edge, re-saving to the same file
handle, with a download and `<input type=file>` elsewhere; (c) offer an optional gzip-compressed file recognised by
its first bytes 1F 8B. This note records how comparable open-source apps do each of these, read in their code at
pinned commits.

**Method.** Licence read first, code read as text, never run, never built. Files were fetched from
`raw.githubusercontent.com/<org>/<repo>/<sha>/<path>` or from blobless shallow sparse clones in the session
scratchpad (outside the repository). Commit SHAs come from `git ls-remote <url> HEAD` or `git rev-parse HEAD` in the
clone, on 2026-11-07. Line numbers refer to those commits. The GitHub REST issue endpoints for these repositories were
refused ("GitHub access to this repository is not enabled for this session"), and github.com issue pages returned
403, but `gh api search/issues` with `is:issue` worked: issue titles and the first part of each body were read
from its results (level P for what the reporter wrote; nothing in an issue is taken as a fact about the code).

**Levels** (per `docs/research/research-protocol.md`): **P** read in the primary source at a pinned commit, or the
vendor's own page; **S** dependable secondary, gap stated; **U** search summary, a pointer only, never reaches the
code.

## Search log

| # | Date | Where | Query or path | Result |
|---|---|---|---|---|
| 1 | 2026-11-07 | git ls-remote | HEAD of the six repositories | SHAs below |
| 2 | 2026-11-07 | raw.githubusercontent.com | browser-fs-access `LICENSE`, `src/supported.mjs`, `src/file-save.mjs`, `src/file-open.mjs`, `src/fs-access/*`, `src/legacy/*`, `README.md`, `package.json` | read, P |
| 3 | 2026-11-07 | sparse clone | excalidraw `packages/excalidraw/data`, `packages/excalidraw/actions`, `packages/common/src`, `excalidraw-app` | read, P |
| 4 | 2026-11-07 | sparse clone | tldraw `LICENSE.md`, `packages/tldraw/src/lib/utils/tldr`, `apps/dotcom/client/src` | read, P; note HEAD moved between ls-remote (616a7c49) and clone (547f507b); the clone's SHA is cited |
| 5 | 2026-11-07 | raw.githubusercontent.com | drawio `LICENSE`, `src/main/webapp/js/diagramly/{LocalFile,App,EditorUi,DrawioFile,Editor}.js` | read, P |
| 6 | 2026-11-07 | raw.githubusercontent.com | vscode `LICENSE.txt`, `src/vs/platform/files/browser/{htmlFileSystemProvider,webFileSystemAccess}.ts` | read, P |
| 7 | 2026-11-07 | raw.githubusercontent.com | detectIncognito `LICENSE`, `README.md`, `src/detectIncognito.ts`; `CHANGELOG.md` | read, P; CHANGELOG.md 404 (does not exist at that commit) |
| 8 | 2026-11-07 | github.com/.../issues, api.github.com/repos/.../issues | issue lists | 403 refused (proxy / session scope) |
| 9 | 2026-11-07 | gh api search/issues | `repo:GoogleChromeLabs/browser-fs-access is:issue safari`, `... cancel` | #72, #88, #107, #153, #158 read |
| 10 | 2026-11-07 | gh api search/issues | `repo:excalidraw/excalidraw is:issue lost work`, `... save file handle permission`, `... safari download`, `... save unsaved indicator` | #8817, #10567, #5100, #5951, #1714 read |
| 11 | 2026-11-07 | gh api search/issues | `repo:jgraph/drawio is:issue lost diagram device`, `... File System Access`, `... unsaved changes click here to save`, `... draft recover` | titles #3722, #4771, #828, #2126 seen; no body read |
| 12 | 2026-11-07 | gh api search/issues | `repo:Joe12387/detectIncognito is:issue false positive` | #21, #60, #63, #65 read |
| 13 | 2026-11-07 | gh api search/issues | `repo:microsoft/vscode is:issue NotAllowedError file system access vscode.dev` | no results |
| 14 | 2026-11-07 | photopea.com/learn/opening-saving | vendor page | 200, read |
| 15 | 2026-11-07 | help.figma.com/hc/en-us/articles/8403626871063 | vendor page "Save a local copy of files" | 200 after redirect, read |
| 16 | 2026-11-07 | drawio.com/docs/manual/editor/save-file-formats/ | vendor page | 200 after redirect, read |

## Pinned sources

| Project | Commit | Licence (read) |
|---|---|---|
| GoogleChromeLabs/browser-fs-access 0.38.0 | 686165d55fc159dae80ef95dc2a70472923aeccd | Apache-2.0 (`LICENSE`; header in each file) |
| excalidraw/excalidraw | 701b901a0f1ba3d0b390d9cdf63d112e25abac4b | MIT (`LICENSE`) |
| tldraw/tldraw | 547f507b25381d057365f053cab3bdef0bb8effe | tldraw licence (`LICENSE.md`): source-available, not open source; "Not to use the Software in Production Environments" without a licence key. Method only, nothing taken. |
| jgraph/drawio | c72c9a98b7a6ce392556ed04c05e0ff19f43f5c3 | Apache-2.0 (`LICENSE`) |
| microsoft/vscode | 17c503e7ef0c2575daa5338b706a767a24b10e7b | MIT (`LICENSE.txt`) |
| Joe12387/detectIncognito 1.8.1 | 04d041218058d201c811b68b551a0e46108747a5 | MIT (`LICENSE`, header lines 7-27) |

Short forms below: `bfa@686165d`, `ex@701b901`, `tl@547f507`, `dio@c72c9a9`, `vsc@17c503e`, `di@04d0412`.

## 1. browser-fs-access (Apache-2.0)

| Finding | Evidence (path@sha:lines) | Level | Confidence |
|---|---|---|---|
| Support test: false outside a window (`typeof self === 'undefined'`); false in a cross-origin iframe, found by writing `top.window.document._ = 0` in try/catch; then true only if `'showOpenFilePicker' in self`. It does not test `showSaveFilePicker` separately. | `src/supported.mjs@686165d:23-45` | P | High |
| The choice is made once, at module load: `supported ? import('./fs-access/...') : import('./legacy/...')`. | `src/file-save.mjs@686165d:20-30`; `src/file-open.mjs@686165d:20-30` | P | High |
| Save with an existing handle: the handle is checked with `await existingHandle.getFile()`; if that throws (file deleted or moved), the handle is dropped and the save picker is shown, unless `throwIfExistingHandleNotGood` is true, which rethrows. No `queryPermission`/`requestPermission` call: write permission is left to `createWritable()`, which prompts in Chrome. | `src/fs-access/file-save.mjs@686165d:64-74, 75-87` | P | High |
| Save picker: `showSaveFilePicker({ suggestedName: fileName or 'Untitled', id, startIn, types, excludeAcceptAllOption })`; `types` built from `mimeTypes`/`extensions`, with `*/*` when neither is given. `filePickerShown(handle)` is called only when a new picker was shown. Returns the handle. | `src/fs-access/file-save.mjs@686165d:32-63, 75-86, 101` | P | High |
| Write: streams with `blob.stream().pipeTo(writable)` when available (pipeTo closes the writable), else `writable.write(blob)` then `close()`. | `src/fs-access/file-save.mjs@686165d:87-101` | P | High |
| Legacy save: `<a download>` with `a.download = options.fileName or 'Untitled'`, `a.href = URL.createObjectURL(blob)`, `a.click()`; the URL is revoked 30 seconds after the click (comment cites a Scratch GUI issue for why not at once). The anchor is not appended to the document. Resolves `null` (no handle). No iOS or Safari branch. | `src/legacy/file-save.mjs@686165d:22-56` | P | High |
| Legacy open: hidden `<input type=file>` appended to `document.body` ("else Safari on iOS won't fire the `change` event reliably"), `accept` = MIME types plus extensions; the `cancel` event rejects with `DOMException('The user aborted a request.', 'AbortError')` and removes the input; `change` resolves `input.files[0]`; uses `input.showPicker()` when present, else `input.click()`. Browsers without the `cancel` event leave the promise pending. | `src/legacy/file-open.mjs@686165d:22-57` | P | High |
| Modern open attaches the handle to the returned File as `file.handle`, which callers keep for re-saving. | `src/fs-access/file-open.mjs@686165d:18-20, 46-53` | P | High |

## 2. Excalidraw (MIT)

| Finding | Evidence (path@sha:lines) | Level | Confidence |
|---|---|---|---|
| Uses browser-fs-access; `fileSave` passes `fileName = name.extension`, `extensions: ['.excalidraw']`, the existing handle, and `throwIfExistingHandleNotGood = false` (a lost handle falls back silently to the picker). | `packages/excalidraw/data/filesystem.ts@701b901:1-5, 49-73` | P | High |
| Extension `.excalidraw`, MIME `application/vnd.excalidraw+json`; library `application/vnd.excalidrawlib+json`. | `packages/common/src/constants.ts@701b901:315-321`; `packages/excalidraw/data/json.ts@701b901:77-100` | P | High |
| Save (Ctrl/Cmd+S, `saveToActiveFile`) is offered only when `appState.fileHandle` exists; it writes to that handle, or re-saves a PNG/SVG with the scene embedded when the handle is an image; toast "saved to <filename>". Save as (`saveFileToDisk`) passes `fileHandle: null` and stores the new handle. An `AbortError` (picker cancelled) is logged as a warning and clears the toast; other errors are logged. A single `onExportInProgress` flag stops a second save during the first. | `packages/excalidraw/actions/actionExport.tsx@701b901:253-326, 328-370` | P | High |
| Lost permission: no explicit permission query or user message in the save path; the error goes to `console.error`. An open issue asks for a message explaining "The request is not allowed by the user agent or the platform in the current context." | `actionExport.tsx@701b901:307-319`; issue #5951 (2022-12-05, open) | P | High |
| No "not saved to a file" marker and no timed reminder. The scene is autosaved to the browser (`LocalData`, debounced, `SAVE_TO_LOCAL_STORAGE_TIMEOUT = 300` ms), flushed on unload, blur and `visibilitychange`; a banner shows when localStorage quota is exceeded. `beforeunload` prevents leaving only while image files are still uploading (`fileStorage.shouldPreventUnload`) or, in collaboration, while the room is not saved to Firebase. | `excalidraw-app/App.tsx@701b901:656-687, 690-712, 1078-1080`; `excalidraw-app/app_constants.ts@701b901:2`; `excalidraw-app/data/LocalData.ts@701b901:73-115`; `excalidraw-app/collab/Collab.tsx@701b901:309-330` | P | High |
| Compression: pako zlib `deflate`/`inflate` (not gzip) for the scene JSON embedded in a PNG `tEXt` chunk and for the encrypted share-link payload, tagged `compression: "pako@1"`. The `.excalidraw` file itself is plain JSON. No `CompressionStream`. | `packages/excalidraw/data/encode.ts@701b901:1, 97-140, 293-410`; `packages/excalidraw/data/image.ts@701b901:30-45` | P | High |
| File type on open: by extension for `.excalidraw`/`.excalidrawlib`; for images by leading bytes (PNG `137 80 78 71 13 10 26 10`, JPEG `255 216 255`, GIF, WebP) read from `file.slice(0, 15)`. This is the same technique as recognising gzip by `1F 8B`. | `packages/excalidraw/data/blob.ts@701b901:84-106, 474-506, 522-545` | P | High |
| Safari is detected by user agent (`isSafari`, `isIOS`) for UI quirks, not in the save path; no private-window detection anywhere searched. | `packages/common/src/editorInterface.ts@701b901:54-55`; grep of `packages/common/src`, `excalidraw-app` for `incognito`/`isPrivate`: none | P | Medium (grep scope limited to the sparse folders) |

## 3. tldraw (tldraw licence: method only)

| Finding | Evidence (path@sha:lines) | Level | Confidence |
|---|---|---|---|
| Format: `.tldr`, MIME `application/vnd.tldraw+json`, JSON with `tldrawFileFormatVersion`; a newer version than the app knows is refused. | `packages/tldraw/src/lib/utils/tldr/file.ts@547f507:53-56, 64, 122-155, 204-255` | P | High |
| tldraw.com does not save to files as its real save: the server is the store. Cmd/Ctrl+S is bound to a do-nothing action (`save-null`, comment "blocks the command+s shortcut"); "Download file" is a one-way export, either a server URL with `a.download = ''` (name from Content-Disposition) or `downloadFile(new File([blob], name))`. No file handle is kept or reused. | `apps/dotcom/client/src/tla/components/TlaEditor/useFileEditorOverrides.ts@547f507:20-33, 72-96` | P | High |
| Open/import uses browser-fs-access `fileOpen({ extensions: ['.tldr', '.tldraw'], multiple: true })`; `.tldraw` (tldraw offline: an archive with a SQLite database) is accepted by the picker only to explain why it cannot be opened. | `apps/dotcom/client/src/tla/components/menu-items/menu-items.tsx@547f507:2, 330-350`; `apps/dotcom/client/src/tla/utils/tldrawOfflineFiles.ts@547f507:5-14` | P | High |
| No unsaved-to-file marker; `beforeunload` only flushes pending sync. | `apps/dotcom/client/src/tla/components/TlaEditor/TlaEditor.tsx@547f507:455-457` | P | Medium (body of `flush` not read) |

## 4. draw.io (Apache-2.0)

| Finding | Evidence (path@sha:lines) | Level | Confidence |
|---|---|---|---|
| Support test: `EditorUi.nativeFileSupport` = not Opera, not Electron, not `extAuth=1`, and both `showSaveFilePicker` and `showOpenFilePicker` are functions. | `src/main/webapp/js/diagramly/EditorUi.js@c72c9a9:249-251` | P | High |
| A device file (`LocalFile`) keeps `fileHandle` and `desc` (the File from `getFile()`); autosave is allowed only with a valid handle. Renaming the file drops the handle. | `LocalFile.js@c72c9a9:8-36, 157-165` | P | High |
| Re-save to the handle: `createWritable()` is called first, "so that the write permission prompt is shown while the transient user activation ... is valid", then the data is generated; a draft copy is saved during the write; before writing, `getFile()` is compared by `lastModified` with the stored `desc`: if the file changed on disk and `overwrite` is false, the save stops with a conflict state and the swap file is aborted (`writable.abort()`); if `getFile()` fails the handle is marked `invalidFileHandle`. On success `desc` is refreshed and the draft removed. A second save while one runs returns `ERROR_BUSY`. | `LocalFile.js@c72c9a9:226-320` | P | High |
| Permission on open: `queryPermission({mode:'readwrite'})` decides whether the file opens editable (`!== 'denied'`); without `queryPermission`, a trial `createWritable()`; else read-only. | `App.js@c72c9a9:5556-5625` | P | High |
| Save picker wrapper ignores `AbortError` (cancel) and reports other errors. | `App.js@c72c9a9:5690-5712` | P | High |
| Without a handle the file is downloaded: `doSaveLocalFile` appends `.drawio` when an XML name has no known extension; on iOS offline it shows the text in a dialog or opens a new window ("Workaround for 'WebKitBlobResource error 1' in mobile Safari"); otherwise `<a download>`, appended to the body, URL revoked after 20 seconds; `target=_blank` when `download` is unsupported; Chromium 65 special case. `isLocalFileSave` is true on iOS. | `EditorUi.js@c72c9a9:8360-8365, 8397-8470`; `LocalFile.js@c72c9a9:326-335` | P | High |
| Unsaved marker: the status bar shows "Unsaved changes. Click here to save" (with "last saved N ago" when over a minute), a clickable `geStatusAlert` that runs Save or Save as. No timed reminder (no 30-minute or similar prompt found). | `DrawioFile.js@c72c9a9:3213-3258` | P | High (marker); Medium (absence of a timer: grep of the five files only) |
| Drafts: while unsaved, a draft (`{type:'draft', modified, data, title}`) is written to the browser database under `.draft_<id>` 1 s after the last change and at least every 30 s while editing; empty diagrams remove the draft; removed after a successful save; offered for recovery after a restart. | `EditorUi.js@c72c9a9:256-264`; `DrawioFile.js@c72c9a9:3125-3180, 3190-3207, 3259-3281` | P | High |
| `beforeunload`: "allChangesLost" when modified; and "ensureDataSaved" for a device file with no handle even when not modified (the app cannot know the download reached the disk). | `App.js@c72c9a9:3450-3482` | P | High |
| Compression: the diagram XML inside the file may be raw-deflate plus Base64 (`pako.deflateRaw`/`inflateRaw`); `Editor.compressXml = true` but `Editor.defaultCompressed = false` (new files uncompressed). Not gzip, not detected by magic bytes. The vendor page states `.drawio` is "an uncompressed file using the XML format". | `Editor.js@c72c9a9:279-286, 2568-2592`; drawio.com/docs/manual/editor/save-file-formats/ (read 2026-11-07) | P | High |
| Safari: `mxClient.IS_SF`/`IS_IOS` user-agent flags for workarounds; no private-window detection found. | `EditorUi.js@c72c9a9:8360-8365, 8414-8425, 23850`; grep of App.js/EditorUi.js for `incognito`: none | P | Medium |

## 5. VS Code for the web (MIT)

| Finding | Evidence (path@sha:lines) | Level | Confidence |
|---|---|---|---|
| Support test: `typeof showDirectoryPicker === 'function'`. | `src/vs/platform/files/browser/webFileSystemAccess.ts@17c503e:13-19` | P | High |
| Each handle is kept in memory and also `put` into IndexedDB (handles are structured-clonable) under an id such as `/name.ext`, de-duplicated with `isSameEntry`. | `htmlFileSystemProvider.ts@17c503e:359-363, 374-398` | P | High |
| On use after a reload: memory first; else the IndexedDB handle, then `queryPermission()`; if not `granted`, `requestPermission()` (which needs a user gesture and "can fail with a DOMException", logged); without permission the file is reported unavailable. | `htmlFileSystemProvider.ts@17c503e:400-501` | P | High |
| `NotAllowedError` becomes "Insufficient permissions. Please retry and allow the operation." | `htmlFileSystemProvider.ts@17c503e:505-517` | P | High |

## 6. Private-window and Safari detection: detectIncognito (MIT)

| Finding | Evidence (path@sha:lines) | Level | Confidence |
|---|---|---|---|
| Engine identified not by user agent but by the length of the error message from `(-1).toFixed(-1)`: 44 or 43 = Safari (JavaScriptCore), 51 = Chromium (V8), 25 = Firefox (SpiderMonkey); `msSaveBlob` = IE; else it rejects "cannot determine the browser". | `src/detectIncognito.ts@04d0412:64-89, 288-304` | P | High |
| Safari (current): `await navigator.storage.getDirectory()`; private if it throws with a message containing "unknown transient reason". Safari 13-18: IndexedDB `put(new Blob())` throws "are not yet supported" in private. Older: `openDatabase` or `localStorage.setItem` throws. | `src/detectIncognito.ts@04d0412:95-163` | P | High |
| Chromium (1.8.1): no longer the storage-quota method. It times sequential IndexedDB commits with `durability: 'strict'` against `'relaxed'` (16 KB payload, 15 writes, 7-15 rounds, about 1 s cap); median ratio below 1.30 = incognito (in-memory LevelDB makes strict fsync free). Abstains (not private) when the durability hint is not honoured. Comment: re-validate if Chromium's IndexedDB moves to its SQLite backend. | `src/detectIncognito.ts@04d0412:169-239` | P | High |
| Firefox: `navigator.storage.getDirectory()` rejects with "Security error" in private; older Firefox: `indexedDB.open` fails with `InvalidStateError` only in private. | `src/detectIncognito.ts@04d0412:245-278` | P | High |
| Stated limits: false positives in some setups and Chrome Guest mode (issue #21); Firefox container tabs not detected; must run over HTTPS ("running locally or via HTTP might fail"); throws if the browser is unidentified; supported Safari up to 26.5, Chromium 83-150, Firefox 44-153. | `README.md@04d0412:50-65` | P | High |
| Known false results reported: #21 (open) quota method also true for Guest mode and "clear cookies on close" settings; #65 (closed 2026-06-20) Chrome Android normal window detected as incognito (the reason for the timing method); #63 (open, 2026-06-02) RAM disk false positive with the new Chromium method; #60 (closed) Firefox 150 normal window reported private. | gh search/issues, Joe12387/detectIncognito #21, #60, #63, #65 | P (reports) | High that they were reported; fix state not read |
| None of Excalidraw, tldraw, draw.io or VS Code detects private mode. Excalidraw and draw.io sniff Safari/iOS by user agent only to work around rendering and download bugs. Why (inferred, not stated): their real save is the file or a server, and the browser copy is only a draft. | sections 2-5 | P (absence, grep-limited); reason S (inference) | Medium |

## 7. Photopea and Figma (vendor pages)

| Finding | Evidence | Level | Confidence |
|---|---|---|---|
| Photopea: "You can save your work as a PSD file (to preserve the whole structure of the document) using File - Save as PSD"; export to JPG/PNG/SVG/PDF through Export As. The page says nothing about browser storage being cleared or a reminder. | photopea.com/learn/opening-saving (read 2026-11-07) | P (vendor page) | High for what it says |
| Figma: a local copy (`.fig`, `.jam`, `.deck`, ...) is for moving between accounts or "to manually back up your files"; it excludes version history and comments; the formats "are proprietary and may change". The cloud is the real save. | help.figma.com/hc/en-us/articles/8403626871063-Save-a-local-copy-of-files (read 2026-11-07) | P (vendor page) | High for what it says |

## Comparison across apps

| App | Unsaved-to-file marker | Timed reminder | Picker + handle reuse | Fallback without the API | Compression | Private / Safari detection |
|---|---|---|---|---|---|---|
| browser-fs-access (library) | none (library) | none | yes: `existingHandle`, checked by `getFile()`; permission left to `createWritable()` | `<a download>`, revoke after 30 s; `<input type=file>` appended, `cancel` event, `showPicker()` | none | none; iframe and API presence only |
| Excalidraw | none; autosave to localStorage; quota banner | none | yes via browser-fs-access; Save only with a handle; Save as drops it | browser-fs-access legacy | pako zlib for PNG-embedded scene and links; `.excalidraw` plain JSON; leading-byte sniffing for images | Safari/iOS by UA for UI only; no private detection |
| tldraw.com | none (server is the store) | none | no; Ctrl+S disabled; download only | download | none for `.tldr` | none found |
| draw.io | "Unsaved changes. Click here to save" in status bar; unload warning even after a download | none found | yes: write permission requested first, `lastModified` conflict check, `invalidFileHandle` | `<a download>` appended, revoke after 20 s; iOS offline shows text/new window | raw deflate + Base64 inside XML, off by default; no magic bytes | Safari/iOS by UA for workarounds; no private detection |
| VS Code web | (editor dirty state, not read here) | none | yes: handles in IndexedDB; `queryPermission` then `requestPermission` on use | n/a (feature absent) | none | none |
| Figma / Photopea | (cloud / not stated) | not stated | n/a | file download | proprietary / PSD | not stated |

Points for V172g taken from this: no app studied has a 30-minute reminder or detects private mode, so these two parts
of V172g have no direct prior art here. draw.io is the closest model for the marker (clickable status text) and for
re-saving (create the writable before the slow work to keep the user activation; check `lastModified`; drop the handle
on rename). browser-fs-access and draw.io agree on the download fallback (blob URL, revoke after a delay of 20-30 s).
Excalidraw's leading-byte sniffing is the pattern for recognising `1F 8B`.

## Counter-evidence

| Report | What it shows | Level |
|---|---|---|
| browser-fs-access #72 (Safari 14 macOS/iPadOS), #88 (iOS Safari 15), #107 (Safari 15.4) | The file input's `change` event sometimes never fires in Safari, so an open promise never settles; the library's answer is appending the input to the body (`legacy/file-open.mjs:36-39`). An app should not block on that promise. | P (reports) |
| browser-fs-access #153, #158 (2025) | Cancel in legacy mode: `cancel` event added; a report that cancelled inputs accumulated. | P (reports) |
| Excalidraw #5100 | `showSaveFilePicker` refused: "Must be handling a user gesture to show a file picker" (save started after async work). Same cause draw.io guards against by creating the writable first. | P (report) |
| Excalidraw #5951 (open) | Permission errors (`The request is not allowed by the user agent...`) reach users with no explanation; can be a policy setting. | P (report) |
| Excalidraw #8817 (open) | An hour of work replaced by an older backup after switching windows (Chrome 130, macOS): browser copy and file can diverge silently. | P (report) |
| Excalidraw #10567 (open) | Accidental overwrite of an existing file, no recovery, asks for a warning before overwriting. | P (report) |
| Excalidraw #1714 (closed) | First save into a Dropbox folder wrote 0 bytes (Firefox, Windows); user lost work. A save should be verified (size or re-read). | P (report) |
| draw.io #3722, #828, #4771 (titles only) | "Unsaved changes. Click here to save (Timeout)" and similar states users could not clear. | U (titles only, bodies not read) |
| drawio #2126 (title only) | "Non empty file filled with zeros using diagrams.net online". | U (title only) |
| detectIncognito #21, #60, #63, #65 | Private-mode detection has repeated false positives in Chromium (Guest, clear-on-close, Android, RAM disk) and Firefox 150; every method relies on undocumented behaviour that browsers change. | P (reports) |

## Still U or open

- Whether any of the draw.io issues above were caused by the device/file-handle path (bodies not read).
- VS Code web's dirty-state indicator and its handling of a handle that lost permission mid-session were not read
  (only the provider).
- Whether Safari (any version) still fails downloads of blob URLs with "WebKitBlobResource error 1" outside iOS
  offline mode: draw.io's comment is the only evidence, undated.
- Figma's and Photopea's handling of browser storage clearing: their pages do not say; not searched further.
- GitHub issue pages and the per-repository REST issue API were refused in this session; issue bodies came from the
  search API only (first 600-900 characters).
