# Topic note: splat editing in the browser (LOD-G2) and the device link (H9, H10)

One of four topic notes for `docs/research/research-devices-xr.md`. Researched 2026-11-23 by a Claude research agent,
following `docs/research/research-protocol.md`. Levels: P (primary source read), S (dependable secondary, gap said),
U (search summary or unverified; never reaches the code). No third-party code was run. Two small experiments of our
own were run here (part 6). This note has not yet had the independent second reading the protocol asks for.

## 1. The questions

**A. Interacting with Gaussian splats (a phase "LOD-G2" after v205).** Which open-source browser splat renderers and
editors exist, under what licence, with what editing, how they sort, and what they claim for phones; which file
formats matter and what their status is; what it costs to select part of a 1,000,000-splat capture by a box, a pinch
or "grow by similar colour and position" on a phone; how splats mix with BIM meshes (depth) and with section planes.

**B. Linking the owner's devices** (the iPhone 13 as the headset, the MacBook Air as the editor) without a server of
ours: does WebRTC need a signalling server; can a QR code carry the offer and answer; which STUN servers are free and
on what terms; what happens on one Wi-Fi without STUN; what iOS Safari supports; and the alternatives (GitHub as in
v216, a WebSocket relay, Bluetooth), against the latency the link must meet.

**Hypotheses** (from the main note):

- **H9.** Region edits on a splat (select by a box or a pinch, hide, delete, move) are feasible in the browser for
  1,000,000 splats on a phone. Refuted by measurements or prior art showing it unworkable at that size.
- **H10.** Two of the owner's devices can be linked without a server of ours, by a QR code. Refuted by WebRTC needing
  a signalling server we would have to run, with no workable manual alternative.

## 2. Search log

| # | Where | Query or address | What came back | Kept or set aside |
|---|---|---|---|---|
| 1 | npm registry | `npm view` for @sparkjsdev/spark, @mkkellogg/gaussian-splats-3d, gsplat, @playcanvas/supersplat, playcanvas, peerjs | Versions, licences, tarball addresses, dates; SuperSplat is not on npm | Kept; tarballs downloaded into the scratchpad as data |
| 2 | npm tarballs, read as text | spark 2.4.0, gaussian-splats-3d 0.4.7, gsplat 1.2.9, peerjs 1.5.5 | Type declarations, READMEs, bundled sources | Kept (P) |
| 3 | GitHub API | repos/... metadata | Refused: this session's GitHub access is bound to its repositories | Recorded; used raw.githubusercontent.com and a shallow clone instead |
| 4 | raw.githubusercontent.com | READMEs and licences of GaussianSplats3D, antimatter15/splat (and its `main.js`), SuperSplat, nianticlabs/spz | All 200 | Kept (P) |
| 5 | git clone --depth 1 | github.com/playcanvas/supersplat at 7912e1d (3.9.2, 2026-11-19) | Full source | Kept; read `src/tools/*`, `src/data-processor/*`, `src/edit-ops.ts`, `src/main.ts`, `src/index.ts` (P) |
| 6 | raw.githubusercontent.com | KhronosGroup/glTF `extensions/2.0/Khronos/KHR_gaussian_splatting/README.md`, the SPZ compression extension's folder, `extensions/README.md` | Base extension "Complete, Ratified"; compression extension folder 404 on main | Kept (P) |
| 7 | Web search | "KHR_gaussian_splatting_compression_spz_2 Khronos ratified status" | Secondary sites call it a draft; a Cesium-native class exists for it | Pointer only (U) |
| 8 | Web search, then webkit.org | Safari 26 WebGPU | WebKit's own post: WebGPU shipping in Safari 26.0 on iOS | Kept (P) |
| 9 | raw.githubusercontent.com | mdn/browser-compat-data `api/RTCDataChannel.json`, `RTCPeerConnection.json`, `Bluetooth.json`, `GPU.json`, `DecompressionStream.json` | Support tables | Kept (P for the data; it is MDN's record, not a test) |
| 10 | raw.githubusercontent.com | WebKit/standards-positions `summary.json` | Web Bluetooth: "oppose" | Kept (P) |
| 11 | rfc-editor.org, ietf.org | RFC 8829 (JSEP); draft-ietf-mmusic-mdns-ice-candidates-03 | Signalling left to the application; mDNS host candidates | Kept (P) |
| 12 | Web search, then bugs.webkit.org | Safari iOS WebRTC mDNS | WebKit bug 189503, comment 4 (2019) | Kept (P for the comment) |
| 13 | Web search, then magarcia.github.io | serverless WebRTC QR signalling | QWBP draft spec (2026-01-19) read as text; fta2012/serverless-webrtc-qrcode, VDO.Ninja docs as pointers | QWBP kept (P for what it says); others U |
| 14 | peerjs.com; PeerJS bundle | Cloud server terms; default ICE servers | No terms published; defaults read from code | Kept (P) |
| 15 | Web search; developers.cloudflare.com | Google STUN terms; Cloudflare STUN | No Google terms found; Cloudflare's FAQ: free and unlimited | Cloudflare P; Google U |
| 16 | developers.meta.com | Rendering best practices | 20 ms motion-to-photon threshold; variable latency worse | Kept (P) |
| 17 | export.arxiv.org | SAGA (2312.00860), Gaussian Grouping (2312.00732), LangSplat (2312.16084) | Abstracts | Kept (P for the abstracts only) |
| 18 | sparkjs.dev, developer.playcanvas.com | Spark performance page; SOG format page | Vendor splat budgets; SOG layout | Kept (P for the claim, the claim itself unchecked) |
| 19 | docs.github.com; api.github.com | CORS on the REST API | Docs: CORS from any origin; api.github.com refused by this environment's proxy (403) | Docs P; the header not tested here |
| 20 | This repository | v205 SPEC and test, `src/js/engine/render/`, `runtime/MANIFEST.json`, v216 research | What the app has | Kept (P) |

Counter-evidence searches are in part 7.

## 3. Findings A: splats in the browser

### A1. The libraries (all read as text, none run)

| Library | Version read | Licence | Renders with | Editing it offers | How it sorts | Phone claim | State |
|---|---|---|---|---|---|---|---|
| Spark (World Labs) | 2.4.0, npm 2026-10-20 | MIT (P, `LICENSE`, "Copyright 2025 World Labs Technologies") | three.js >= 0.180 (peer dependency), WebGL2 | `SplatEdit` with signed-distance shapes: all, plane, sphere, box, ellipsoid, cylinder, capsule, infinite cone; per shape an opacity, a colour (multiply, set, add) and a displacement; soft edges; `raycast` on a `SplatMesh` (P, `SplatEdit.d.ts`, `SplatMesh.d.ts`). Hand joints for WebXR hands (`hands.d.ts`) | The GPU writes 16- or 32-bit distance keys, read back; a worker sorts them in Rust compiled to WebAssembly (`sort_splats`, `sort32_splats`); radial or Z order (`sortRadial`) (P, `worker.d.ts`, bundle) | "iPhone: 1-3 million splats" (P that the page says so; not checked on a device) | Active (release a month old) |
| SuperSplat (PlayCanvas) | 3.9.2, commit 7912e1d, 2026-11-19 | MIT (P) | PlayCanvas engine 2.24.1, **WebGPU only** (`main.ts`: `deviceTypes: ['webgpu']`; `index.ts`: "SuperSplat requires WebGPU") (P) | The fullest editor: box, sphere, rectangle, lasso, polygon, brush, sphere brush, eyedropper (colour), flood (screen-space, by opacity) selection; hide, unhide, delete (removes instances), move, rotate, scale, colour grade, undo (`src/tools/`, `src/edit-ops.ts`) (P) | Selection by WebGPU compute shaders, results read back as a bit mask (`data-processor/intersect.ts`, `color-match.ts`) (P) | None found | Active; an application, not a library |
| GaussianSplats3D (mkkellogg) | 0.4.7, npm 2025-01 | MIT (P) | three.js | No region editing found in the README | WASM (C++, SIMD) in a worker; optional GPU distance pass; uses SharedArrayBuffer by default, so it needs cross-origin isolation headers unless turned off (P, README) | README lists "Sub-optimal performance on mobile devices" as a known issue (P) | README: "no longer in active development", recommends Spark (P) |
| antimatter15/splat | main, read 2026-11-23 | MIT, Kevin Kwok 2023 (P) | One file, WebGL2 context in the code (`getContext("webgl2")`), README says WebGL 1 (P; the conflict already noted in `research-notion-v192-splats.md`) | None | CPU worker: depth from the view matrix, then a 16-bit single-pass counting sort; skips the sort when the view direction barely changed (P, `main.js` lines 420-470) | None | README now points to Spark (P) |
| gsplat.js (Dylan Ebert, Hugging Face) | 1.2.9, npm 2025-07-12 | MIT (P) | Its own WebGL renderer | A per-splat selection array (`selection: Uint8Array`) and a selected flag on objects (P, type files); an editor demo on Hugging Face (U) | WASM sort worker (`dist/wasm/sort.wasm`) (P) | README: "May not work on all devices" (P) | No release since 2025-07 |

**Reading (confidence high):** Spark is the one maintained library that fits the app's rendered view (three.js,
WebGL2, MIT) and already has the edits LOD-G2 wants as GPU-side shapes. SuperSplat has the richest selection tools and
is the best prior art to read, but it needs WebGPU and is a whole application on another engine; its methods, not its
code, are what to take. GaussianSplats3D and antimatter15 now both point to Spark.

**Fit with the app (P, this repository):** three.js 0.186.1 is vendored as one classic script
(`runtime/three/0.186.1/bim-three.min.js`, `runtime/MANIFEST.json`), so it meets Spark's ">= 0.180" peer range. Spark
ships as an ES module importing `three` and `three/addons/postprocessing/Pass.js`; it would have to be rebuilt against
the app's three.js the way `tools/three` builds it, then pinned under `runtime/` by the library rule. Its worker is
made from an inline `data:` or blob script with WebAssembly inside (P, bundle). The minified module is 2.85 MB,
983 kB gzipped (measured here). The bundle has no `SharedArrayBuffer` (counted: 0), so no cross-origin isolation is
needed (P). The licences of the Rust crates compiled into its WebAssembly were not read (U, to read before approval).

### A2. File formats

| Format | What it is | Status | Level |
|---|---|---|---|
| `.splat` (antimatter15) | 32 bytes a splat, no header, no spherical harmonics | De facto; no specification beyond the viewer's code | P (code) |
| `.ply` (3DGS) | The training output (INRIA), float32 fields, with spherical harmonics, about 248 bytes a splat at degree 3 | De facto | S (layout from readers' code, not INRIA's spec) |
| `.spz` (Niantic) | MIT (P, `LICENSE`, "Copyright 2024 Niantic Labs"). Version 4: a 32-byte plain header ("NGSP"), then independently **ZSTD**-compressed streams; versions 1 to 3 were one gzip stream and are still readable; positions as 24-bit fixed point; rotations as the smallest three components (P, README) | Open, versioned | P |
| `.sog` (PlayCanvas) | `meta.json` and lossless WebP images (means, scales, quaternions, colour, optional SH), or one zip `.sog`; version 3; "~15-20x smaller than an equivalent PLY" | Published by PlayCanvas; no licence stated for the spec | P (page) |
| `.ksplat` | GaussianSplats3D's own | Its library is unmaintained | P (README) |
| glTF `KHR_gaussian_splatting` | Splats as a point primitive: position, rotation, scale, opacity, SH; `kernel` "ellipse", `colorSpace`, `projection` "perspective", `sortingMethod` default `cameraDistance` ("the length of the vector from the splat to the camera origin") | **"Complete, Ratified by the Khronos Group"**, listed in the extensions registry | P (Khronos README on `main`) |
| `KHR_gaussian_splatting_compression_spz_2` | The SPZ payload inside the base extension | **Not on Khronos's `main`** (its folder answers 404); secondary sites call it a draft; Cesium-native already has a class for it | P for the absence on `main`; "draft" U |

Two facts that matter for the code:

- **Browsers cannot decompress ZSTD themselves.** MDN's data has `DecompressionStream` "zstd" unsupported in Safari
  and Chrome; gzip and deflate are supported from Safari 16.4 (P, browser-compat-data). So a SPZ version 4 file needs
  a ZSTD decoder in WebAssembly or JavaScript (a library, under the library rule); SPZ 1 to 3 (gzip) can be read with
  the browser alone. Whether Spark 2.4.0 reads SPZ version 4 was not established: no "zstd" string is in its JS, but
  its decoder is compiled WebAssembly (U).
- **The ratified glTF order is camera distance**, which is what v205's `bimSplatOrder` computes (squared distance,
  farthest first). antimatter15 and Spark's default use view depth instead. Both are recorded; v205 is consistent
  with the standard.

### A3. Selecting part of a splat

**Prior art, read as code (P):**

- *Box and sphere:* SuperSplat tests each splat's centre (optionally its extent, `footprint`) against a unit box or
  sphere transformed to world space, on the GPU (`data-processor/intersect.ts`). Spark does the same as a shape that
  changes opacity, colour or position while drawing, without a selection list (`SplatEdit`).
- *Similar colour:* SuperSplat's eyedropper runs a compute shader comparing every splat's final colour to the picked
  splat's, per channel within a threshold (default 0.2), four splats a word (`color-match.ts`).
- *Flood:* SuperSplat's "flood" is a screen-space fill on the rendered image's opacity, then a mask applied to splat
  centres (`flood-selection.ts`); it is not a 3D neighbourhood growth.
- *Pinch:* Spark exposes WebXR hand joints and sphere shapes, so a pinch can drive a sphere edit (P for the API; how
  its examples use it U). On the owner's iPhone there is no WebXR hand input (the main note's H1); a pinch would come
  from the camera hand tracker of `hands-and-physics.md`, giving a 3D point to centre a sphere on.

**Cost, measured here (part 6, CPU, Node 22 on a 2.1 GHz Xeon, 1,000,000 synthetic splats, median of 5):** a box test
11 ms, a sphere test 7 ms, a colour match 10 ms, a 0.25 m grid built for growing 23 ms; growing by position (0.5 m)
and colour through the whole cloud (the worst case, every splat reached) 2.2 s. An iPhone's JavaScript speed was not
measured (U); the main note's test page should time the same loops on the phone.

**Reading (confidence medium):** box, sphere, colour and hide or delete are single passes over the splats, about 10 ms
each on this CPU and plausibly within a few times that on an A15 (to measure). They need no GPU compute, so they work
in WebGL2 and on iOS before 26. Growing is the only expensive one: bounded by a maximum count or radius and run in a
worker, it stays responsive. Moving a selection is a transform of the selected splats' centres and rotations, then a
re-sort; the sort already runs every frame.

**Segmentation in research, briefly (P for the abstracts):** SAGA segments a 3D-GS scene from a 2D prompt "within
4 ms", but only after training a per-splat affinity feature with SAM masks; Gaussian Grouping adds an identity code to
each Gaussian, supervised by SAM masks during training; LangSplat distils CLIP features into each Gaussian, with a
per-scene autoencoder. All three are trained offline on a CUDA GPU with the capture's photos; none runs in a phone
browser. A browser could at most read an exported per-splat label or feature and select by it (an exported label of
one byte a splat is 1 MB for a million; a 32-value feature in half floats 64 MB; arithmetic, not measured). Out of
scope for LOD-G2.

### A4. Splats with BIM meshes and section planes

- **Depth:** Spark's material defaults to depth test on and depth write off, so opaque meshes drawn first hide the
  splats behind them, and splats do not hide each other through the depth buffer (P, `SparkRenderer.d.ts` lines
  296-307: "most of the Gsplat is transparent"). GaussianSplats3D: "this will only work for objects that write to the
  depth buffer (e.g. standard opaque objects)" (P, README). Same rule for our own renderer: draw BIM opaques, then
  splats with depth test on and write off, then transparent BIM (glass) last; glass over splats is approximate.
- **Splats in front of BIM:** with depth test on, a splat in front of a wall draws over it, correctly.
- **Section planes:** the app's rendered view takes the section cut from the scene description it already builds
  (`src/js/engine/render/rendered-scene.js` header), not from three.js clipping planes, so splats need their own cut:
  in the vertex shader, drop a splat whose centre is on the removed side of the plane (one uniform vec4 per plane).
  Spark's `SplatEditSdf` of type `plane` with opacity 0 does the same (P, types). A splat straddling the plane is
  kept or dropped whole, so the cut edge is soft by about one splat's size (reasoning, U until seen).

## 4. Findings B: the device link

### B1. WebRTC needs signalling, but not a particular server

- JSEP, RFC 8829, section 3.1: "JSEP does not specify a particular signaling model or state machine, other than the
  generic need to exchange session descriptions"; the offer "is finally sent off to the remote side over its
  preferred signaling mechanism (e.g., WebSockets)" (P). Any channel that carries the offer one way and the answer
  the other works: a QR code, a typed code, a file.
- **iOS Safari:** `RTCPeerConnection` and `RTCDataChannel` from Safari 11, iOS mirroring macOS (P, MDN data). WebKit
  bug 189503 ("RTCDataChannel seems broken on iOS 11/12", still NEW): a WebKit engineer, 2019-01-14, "We recently
  enabled MDNS ICE candidates by default in WebKit ToT. This should enable Safari <-> Safari connections in networks
  supporting MDNS" (P for the comment; current behaviour U, to test on the owner's phone).
- **mDNS host candidates:** the IETF draft replaces a private address with a random "UUID.local" name that the other
  side resolves by multicast DNS (P, draft-03, expired June 2022, never an RFC). Measured here: Chromium 153 with no
  ICE servers gives exactly one host candidate, a `.local` name (part 6). On one Wi-Fi the two devices can connect
  with no STUN at all, if the network passes multicast DNS. Guest networks and client isolation block it (U, common
  knowledge, not read).
- **QR payload size, measured here:** a data-channel offer with one mDNS candidate is 587 bytes of SDP, 428 bytes
  after the browser's own `deflate-raw`, 572 characters in base64 (two runs, part 6). A QR code holds that easily (a
  version-40 code holds 2,953 bytes in byte mode at the lowest error correction, from the QR standard via common
  tables, S). QWBP, a 2026 draft by M. Garcia Monterde, shrinks the exchange to 41 to 110 bytes by sending only the
  DTLS fingerprint and the candidates, rebuilding the rest from a template, and deriving the ICE username and
  password from the fingerprint with HKDF; it needs **two scans, one each way** (P, spec text). Rebuilding SDP and
  setting chosen ICE credentials is SDP munging, which browsers may refuse (U). No licence stated for QWBP.
- **Two scans** suit the owner: the phone shows a code the MacBook's camera reads, or the laptop shows one the phone
  reads, then the reverse. A one-scan alternative: the phone scans the laptop's offer, then shows its answer as a
  code the laptop's webcam scans. Both directions need a camera on the receiving side (the MacBook Air has one).
- **STUN, only when not on one Wi-Fi:** Cloudflare's FAQ: "Cloudflare's STUN service at `stun.cloudflare.com` is
  free and unlimited" (P). Google's `stun.l.google.com:19302` is PeerJS's default (P, code) but Google publishes no
  terms for it that were found, and a 2025 discuss-webrtc thread reports 401 answers from it (U). STUN alone fails
  behind symmetric NATs (mobile networks); then only TURN, which relays and costs (Cloudflare: $0.05 a GB after
  1,000 GB free, P). For the owner's own two devices at home, none is needed.
- **PeerJS** (MIT, 1.5.5): its default broker `0.peerjs.com` is "our free cloud server" with no published terms,
  limits or uptime (P, peerjs.com, bundle constant `CLOUD_HOST`), and its defaults include PeerJS's own TURN servers
  with a shared password (P, `DEFAULT_CONFIG`). Using it would send the owner's session through a third party's
  service on undeclared terms; it is prior art, not a dependency to take.

### B2. The alternatives

- **GitHub as a mailbox (v216's transport):** the offer and answer written to a small file in the owner's repository
  and polled. The REST API "supports cross-origin resource sharing (CORS) for AJAX requests from any origin" (P,
  GitHub docs); api.github.com itself was refused by this environment's proxy, so the header was not tested here. It
  works across networks, needs the owner's token on both devices, and polls in seconds: fine for the one-time
  exchange, too slow and too costly in requests for a pose stream (reasoning).
- **A WebSocket relay:** needs a server; ours is excluded by H10, a third party's (PeerJS cloud) has no terms.
- **Web Bluetooth:** not in Safari on any platform, `version_added: false` (P, MDN data); WebKit's position is
  "oppose" (P, standards-positions). Refuted as a path for the iPhone.

### B3. What latency the link must meet

Meta: "We believe the threshold for compelling VR to be at or below 20ms of latency", and latency "will be more
uncomfortable the more variable it is" (P). That bound is for the **head pose to the picture**, so the phone must draw
from its own orientation sensor, never wait for the link. What crosses the link is (a) the phone's pose to the laptop
for a mirror view, where 100 ms or so only delays the mirror, and (b) model edits from the laptop to the phone, where
a fraction of a second is acceptable (reasoning, U: no study read for edit latency). A data channel on one Wi-Fi is
well inside both (the latency of a LAN data channel was not measured here; U).

## 5. The alternatives compared

**LOD-G2's renderer and edits.** Criteria stated first: fits the rendered view (three.js, WebGL2); runs on iOS
Safari before and after 26; licence under the library rule; maintained; edits wanted (box, sphere, colour, hide,
delete, move); cost to the app.

| Option | Fits three.js | iOS without WebGPU | Licence | Maintained | Edits | Cost |
|---|---|---|---|---|---|---|
| Our own, from v205 (antimatter15's method, MIT) | Yes (ours) | Yes | Ours | Ours | Ours to write: each a pass over the arrays | No download; we write the sort worker and the shader |
| Spark 2.4.0 | Yes (>= 0.180) | Yes (WebGL2) | MIT; Rust crates unread | Yes | Shapes (box, sphere, plane...), colour, displacement, raycast | 983 kB gzipped; rebuild against our three.js; a second research and the owner's approval |
| SuperSplat's code | No (PlayCanvas) | No (WebGPU only) | MIT | Yes | All of them | A second engine; not usable inside the rendered view |
| GaussianSplats3D | Yes | Yes | MIT | No | None found | SharedArrayBuffer by default |
| gsplat.js | No (own renderer) | Yes | MIT | No releases since 2025-07 | A selection array | A second renderer |

**Recommendation:** keep v205's own path (no new library) and add LOD-G2's edits as pure functions over its arrays,
taking SuperSplat's and Spark's methods with credit. Revisit Spark only if the owner's phone shows our renderer too
slow at 1,000,000 splats or the owner wants SPZ or SOG files; that would be a library research of its own. What would
change it: a phone measurement where our sort plus draw cannot hold the main note's frame rate.

**The link.** Criteria: no server of ours; works on the owner's iPhone and MacBook at home; no third-party service on
undeclared terms; effort.

| Option | Server of ours | Third party | Works where | Effort |
|---|---|---|---|---|
| WebRTC, QR codes both ways, no ICE servers | No | None | One Wi-Fi with multicast DNS | Small: two codes, a scanner |
| The same with Cloudflare STUN | No | Cloudflare STUN, free per its FAQ | Most networks; not symmetric NAT | Same |
| WebRTC signalled through GitHub (v216) | No | GitHub, the owner's own account | Anywhere both are online | Medium; needs a token on the phone |
| PeerJS cloud | No | 0.peerjs.com, no terms | Anywhere | Small, but undeclared terms |
| Web Bluetooth | No | None | Not on iPhone | Impossible |

**Recommendation:** WebRTC data channel, signalled by QR codes, no ICE servers by default, Cloudflare STUN as an
opt-in for "not on the same Wi-Fi", GitHub signalling later with v216. A QR scanner needs a decoder: MDN's data
has `BarcodeDetector` in Safari 17 only behind the "Shape Detection API" flag, iOS mirroring macOS, and in desktop
Chrome on macOS and ChromeOS only (P, browser-compat-data `api/BarcodeDetector.json`). So the iPhone needs a small
vetted QR decoding library, or the laptop scans the phone's code and the phone receives the laptop's by its camera
through that library: a decision.

## 6. The experiments (scripts kept in the session scratchpad, not committed: this research task allowed no file but
this note; they belong in `docs/research/experiments/` if the owner wants them kept)

**E1. SDP size.** A page of our own (`sdp.html`) made an offer with one data channel and no ICE servers, waited for
gathering, compressed the SDP with `CompressionStream('deflate-raw')`, and logged sizes. Environment: Chrome for
Testing 153.0.8010.12 headless, Linux container. Two runs: 587 and 586 bytes of SDP, 428 bytes compressed, 572
base64 characters, one host candidate named `<uuid>.local` each time. Shows: one QR code carries a full offer;
Chromium hides the local address behind mDNS. Not tested: Safari's SDP (likely similar in size, U), two real devices.

**E2. CPU cost of splat operations.** A Node script of our own (`splat_cost.js`) on 1,000,000 uniformly random splats
in a 40 x 10 x 40 m box, medians of 5 runs, Node 22.23.5 on an Intel Xeon at 2.1 GHz:

| Operation | Median | Min | Max |
|---|---|---|---|
| 16-bit counting sort by squared distance | 24.5 ms | 23.6 | 36.4 |
| `Array.prototype.sort` by squared distance, ties by index (as v205's WO-05 states it) | 595 ms | 557 | 927 |
| Box selection | 10.9 ms | 10.7 | 13.4 |
| Sphere selection (r 0.5 m) | 6.9 ms | 6.7 | 9.2 |
| Colour match to one splat (0.2 per channel) | 9.5 ms | 9.5 | 11.3 |
| Grid for growing (0.25 m cells) | 22.9 ms | 20.9 | 40.3 |
| Grow by 0.5 m and colour, worst case (all 1,000,000 reached), 3 runs | 2,200 ms | 2,131 | 2,296 |

(A first run with a poor random generator gave smaller numbers and a degenerate cloud; it was discarded and the
generator replaced.) Shows: the per-frame sort must be a counting or radix sort, not a comparison sort; edits are
about one frame's worth of CPU each. **A finding for v205:** WO-05 as specified is a correct test oracle but, run on
every view change, about 25 times slower than antimatter15's counting sort at 1,000,000 splats; WO-06's wiring
should sort with a counting sort in a worker, checked against `bimSplatOrder` on small inputs (a counting sort
quantises distance to 16 bits, so its order can differ from the exact order for near ties). Not measured: the A15.

## 7. Counter-evidence sought

- *Against H9:* looked for statements that browser splat editing fails on phones. Found GaussianSplats3D's
  "sub-optimal performance on mobile devices" and gsplat.js's "may not work on all devices"; SuperSplat refuses
  browsers without WebGPU (so iPhones before iOS 26). None says box or sphere selection is unworkable; Spark claims
  1 to 3 million splats on an iPhone (vendor's own, unchecked). WebKit bug 301627 reports WebGPU canvas flicker on
  iOS 26 (U, from a search summary), a reason not to depend on WebGPU for this.
- *Against H10:* looked for WebRTC failing between iPhone and Mac without a server. Found: data channels broken on
  iOS 11 and 12 (bug 189503, old); mDNS needing a network that passes multicast; iOS 14's local network permission
  for apps, with a 2020 report that Mobile Safari seemed exempt (U); Google STUN 401 reports (U). None makes a server
  of ours necessary; each has a fallback (STUN, GitHub signalling).
- *Against the format table:* checked Khronos's `main` for the SPZ compression extension and found it absent, so it is
  not called ratified here, against secondary sites that blur the two.

## 8. Outcome for H9 and H10

- **H9: holds, with conditions (confidence medium).** Box, sphere, colour select, hide, delete and move are one pass
  over a million splats, about 10 ms each on this machine; SuperSplat and Spark do the same on the GPU. Conditions:
  the sort is a counting or radix sort in a worker; growing is bounded; the iPhone's speed is measured before the
  limit is set (the main note's test page). Refuted only for SuperSplat's own approach on iPhones without iOS 26.
- **H10: holds (confidence medium-high).** WebRTC needs signalling but not a server (RFC 8829); an offer fits one QR
  code (587 bytes, measured); on one Wi-Fi no STUN is needed (mDNS candidates, measured in Chromium; Safari to test).
  Not refuted, but untested on the owner's two devices; Web Bluetooth is refuted as an alternative.

## 9. Recommended scope

**LOD-G2, after v205** (pure functions in a new file beside `splats.js`, each with a unit test; wiring by Claude):

1. Selection as a `Uint8Array` mask: by box (a centre, half sizes and a turn about the vertical, in project
   coordinates through v205's placement), by sphere (a centre and radius: a click, or the pinch point from the hand
   tracker), by colour similarity to one splat (threshold), and grow from a seed by distance and colour with a
   maximum count; add, remove, intersect, invert.
2. Edits: hide and unhide (a flag the shader reads), delete (compacting the arrays, with undo keeping the removed
   rows), move and turn the selected splats (centres and rotations), tint.
3. Drawing: the counting sort in a worker; depth test on and write off after the BIM opaques; section planes as a
   per-splat discard on the centre.
4. Saving: the edited splats written back as `.splat` (v205's format), the original kept until the owner confirms.
5. Not in LOD-G2: SPZ version 4 and SOG (need a ZSTD decoder or WebP decoding: a library decision); glTF
   `KHR_gaussian_splatting` reading (ratified, a good next format, P); segmentation from research models; WebGPU.

**The device link** (its own phase, after the stereo view):

1. A data channel between two copies of the app, offer and answer by QR code (shown with a QR encoder, read by the
   camera), no ICE servers by default, Cloudflare STUN as an option the owner turns on.
2. Messages: the phone's pose (unordered, no retransmits, about 30 a second), model edits (ordered, reliable, as
   the history records them), a heartbeat.
3. The phone draws from its own sensor; the link never sits in the head-to-picture path.
4. Later: signalling through the owner's GitHub repository with v216.

## 10. Still open (U)

- The iPhone 13's JavaScript speed for E2's loops, and the frame rate of our renderer at 1,000,000 splats.
- Safari's SDP and mDNS behaviour between the owner's iPhone and MacBook on their Wi-Fi, today.
- Which QR decoding library for the iPhone (licence, size), since `BarcodeDetector` is behind a flag in Safari.
- `KHR_gaussian_splatting_compression_spz_2`'s exact status (only its absence from Khronos `main` is P).
- Whether Spark's WebAssembly decodes SPZ version 4 (ZSTD), and the licences of its compiled Rust crates.
- Google STUN's terms; whether browsers accept munged ICE credentials as QWBP needs.
- How a straddling splat looks at a section cut.

## 11. Decisions for the owner (asked with the main note's)

1. LOD-G2 on v205's own renderer (recommended) or on Spark (a library research and approval first)?
2. Which edits first: hide and delete by box and sphere (recommended), then colour and grow, then move?
3. The link: QR codes on one Wi-Fi only, or also Cloudflare's STUN as an option?
4. A QR library for scanning on the iPhone if `BarcodeDetector` is missing (a library research).

## 12. References (all read 2026-11-23)

| Source | URL | What was read | Level |
|---|---|---|---|
| Spark 2.4.0, npm tarball | https://registry.npmjs.org/@sparkjsdev/spark/-/spark-2.4.0.tgz | `LICENSE`, `README.md`, `package.json`, `dist/types/SplatEdit.d.ts`, `SplatLoader.d.ts`, `defines.d.ts`, `SparkRenderer.d.ts`, `worker.d.ts`, `hands.d.ts`, `SplatMesh.d.ts`, `PackedSplats.d.ts`; `dist/spark.module.js` (imports, worker creation, sort functions) | P |
| Spark performance page | https://sparkjs.dev/docs/performance/ | Splat budgets by device | P (claim unchecked) |
| SuperSplat, commit 7912e1d | https://github.com/playcanvas/supersplat | `README.md`, `LICENSE`, `package.json`, `src/main.ts` 125-140, `src/index.ts` 15-30, `src/tools/` list, `flood-selection.ts`, `src/data-processor/color-match.ts`, `index.ts`, `intersect.ts` 1-60, `src/edit-ops.ts` op list, `src/splat-state.ts` | P |
| GaussianSplats3D 0.4.7 and main README | https://github.com/mkkellogg/GaussianSplats3D | README (status, sort, SharedArrayBuffer, depth note, known issues) | P |
| antimatter15/splat | https://github.com/antimatter15/splat | `LICENSE`, `README.md`, `main.js` 298, 415-470, 768-782 | P |
| gsplat.js 1.2.9 | https://registry.npmjs.org/gsplat/-/gsplat-1.2.9.tgz | `LICENSE`, `README.md`, type files, `dist/wasm` | P |
| SPZ | https://github.com/nianticlabs/spz | `LICENSE`, `README.md` (version 4 layout, header, positions, rotations) | P |
| KHR_gaussian_splatting | https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_gaussian_splatting/README.md | Status, properties, sorting method, attributes; `extensions/README.md` | P |
| SPZ compression extension | https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_gaussian_splatting_compression_spz_2 | 404 on `main` | P (absence) |
| radiancefields.com; cgchannel.com | https://radiancefields.com/platforms/the-khronos-group ; https://www.cgchannel.com/2026/02/3d-gaussian-splats-are-being-added-to-the-gltf-standard/ | Search summaries only | U |
| SOG format | https://developer.playcanvas.com/user-manual/gaussian-splatting/formats/sog/ | Layout, version 3, size claim | P |
| WebKit features in Safari 26.0 | https://webkit.org/blog/17333/webkit-features-in-safari-26-0/ | WebGPU shipping on iOS; WebRTC items | P |
| MDN browser-compat-data | https://github.com/mdn/browser-compat-data (api/RTCDataChannel, RTCPeerConnection, Bluetooth, GPU, DecompressionStream, BarcodeDetector) | Support entries | P (MDN's record) |
| WebKit standards positions | https://github.com/WebKit/standards-positions (summary.json) | Web Bluetooth, WebUSB, Web NFC: oppose | P |
| RFC 8829, JSEP | https://www.rfc-editor.org/rfc/rfc8829.txt | Sections 1 and 3.1 | P |
| mDNS ICE candidates draft-03 | https://www.ietf.org/archive/id/draft-ietf-mmusic-mdns-ice-candidates-03.txt | Abstract, resolution rules | P (expired draft) |
| WebKit bug 189503 | https://bugs.webkit.org/show_bug.cgi?id=189503 | Title, status, comment 4 | P |
| WebKit bug 301627 | https://bugs.webkit.org/show_bug.cgi?id=301627 | Not opened; search summary only | U |
| QWBP draft 01 | https://magarcia.github.io/qwbp/spec.txt | Whole text skimmed: sizes, fields, HKDF, two scans | P |
| fta2012/serverless-webrtc-qrcode; VDO.Ninja serverless guide | https://github.com/fta2012/serverless-webrtc-qrcode ; https://docs.vdo.ninja/guides/serverless-connections | Search summaries only | U |
| PeerJS 1.5.5 and site | https://registry.npmjs.org/peerjs/-/peerjs-1.5.5.tgz ; https://peerjs.com/ | `LICENSE`, `README.md`, `dist/bundler.mjs` 125-145, 164; site text | P |
| Cloudflare Realtime TURN and FAQ | https://developers.cloudflare.com/realtime/turn/ ; https://developers.cloudflare.com/realtime/turn/faq/index.md | STUN address; "free and unlimited"; TURN price | P |
| Google STUN terms | (none found); https://groups.google.com/g/discuss-webrtc/c/0E_B-ijPZiU | Search summary only | U |
| GitHub REST CORS | https://docs.github.com/en/rest/using-the-rest-api/using-cors-and-jsonp-to-make-cross-origin-requests | CORS sentence | P |
| Meta rendering best practices | https://developers.meta.com/vr/resources/bp-rendering/ | Latency sentences | P |
| SAGA; Gaussian Grouping; LangSplat | https://arxiv.org/abs/2312.00860 ; https://arxiv.org/abs/2312.00732 ; https://arxiv.org/abs/2312.16084 | Abstracts only | P (abstracts) |
| This repository | `docs/work-orders/v205/SPEC.md`, `v205.test.mjs` line 56, `src/js/engine/render/splats.js`, `rendered-scene.js` header, `runtime/MANIFEST.json`, `docs/research/research-notion-v192-splats.md`, `research-notion-hub-h4-sharing.md`, v216 and v217 specs | As cited | P |
