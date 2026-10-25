# Research: animated site analysis (V170)

The owner (2026-10-19), after Archi Diagram: "it allows the analysis layer to be animated"; their choices
that day: a phase of its own, V170, before the traffic simulation (V171, which draws with the same clock
and exports with the same video), and video written by the app's own MP4 writer, no dependency
(`research-archidiagram.md`, `plan-v167-v170.md`). Researched from 2026-10-24 to `research-protocol.md`,
while V169's checks ran. Every source was read as text from its own host and kept in the session's scratch
folder; nothing downloaded was run.

## 1. Practice: how mapping and analysis tools animate

| Fact | Source | Read | Level |
|---|---|---|---|
| A temporal controller with four modes (off, a fixed range, animated navigation in steps, an "animated movie" of a set number of frames); a frame rate in steps a second; cumulative or moving window; play, loop, scrub with the slider or the wheel; export of the frames as numbered images to combine elsewhere | QGIS user manual, Map views, the temporal controller panel, https://github.com/qgis/QGIS-Documentation (docs/user_manual/map_views/map_view.rst) | the section | P |
| Export to MPEG-4 (H.264), AVI (Motion JPEG), GIF or an image sequence (JPEG, TIFF, PNG, BMP); presets for 720p, 1080p and social formats; a draft preset that does not wait for each frame; Stop keeps the frames made; export time depends on the machine | Esri, ArcGIS Pro, Export an animation, https://pro.arcgis.com/en/pro-app/latest/help/mapping/animation/export-an-animation.htm | the page | P |
| A moving trail: each path's points carry a time; the layer draws what lies within a trail length behind the current time, fading; the application advances the current time each frame | deck.gl TripsLayer (MIT), https://github.com/visgl/deck.gl (docs/api-reference/geo-layers/trips-layer.md) | the page | P |
| Flow lines with marching dashes, symbols that draw on and off in a loop (reveal 40%, hold to 50%, erase to 90%), the clock set to each frame's time before it is drawn, 30 frames a second | Archi Diagram's web app, `research-archidiagram.md` | its bundles as text | P (ideas only) |

## 2. The standards

| Fact | Source | Read | Level |
|---|---|---|---|
| Moving content that starts by itself, lasts more than five seconds and sits beside other content needs a way to pause, stop or hide it (Level A) | WCAG 2.2, 2.2.2 Pause, Stop, Hide, Understanding document, https://github.com/w3c/wcag (understanding/20/pause-stop-hide.html) | the intent | P |
| Motion set off by an interaction can be turned off unless essential; `prefers-reduced-motion` is the way the page hears the user's setting; previewing an animation in an authoring tool is essential (Level AAA) | WCAG 2.2, 2.3.3 Animation from Interactions, the same repository (understanding/21/animation-from-interactions.html) | the intent and examples | P |
| VideoEncoder: a config of codec, width, height, bitrate, framerate, latency mode; `isConfigSupported`; `encodeQueueSize` for back-pressure; frames' timestamps in microseconds; a frame encoded as a key frame on request | W3C WebCodecs, editor's draft, https://github.com/w3c/webcodecs (index.src.html) | the IDL and the algorithms | P |
| H.264 ("avc1." codec strings): in `avc` format each chunk is an access unit with length-prefixed NAL units and the decoder config's `description` is the AVCDecoderConfigurationRecord (ISO/IEC 14496-15, 5.3.3.1), which goes into the MP4 as the `avcC` box as it is | W3C, AVC (H.264) WebCodecs Registration, the same repository | the registration | P |
| VP9 in MP4: the `vp09` sample entry with a `vpcC` FullBox, version 1: profile, level, bit depth, chroma subsampling, full-range flag, colour primaries, transfer, matrix, and (empty for VP9) codec initialisation data; the codec string `vp09.PP.LL.DD...` | WebM Project, VP Codec ISO Media File Format Binding, https://www.webmproject.org/vp9/mp4/ | the box and its semantics | P |
| AV1 in MP4: the `av01` sample entry and `av1C` (marker, version 1, profile, level, tier, bit depth, chroma, then the configOBUs: at most one Sequence Header OBU, first); WebCodecs gives no description for AV1, so the app would parse the sequence header from the first key frame: AV1 is left out of V170, said | AOMedia, AV1 Codec ISO Media File Format Binding, https://github.com/AOMediaCodec/av1-isobmff (index.bs); W3C, AV1 WebCodecs Registration ("description is not used for this codec") | the record and the registration | P |
| H.264's levels: a level caps the frame size in macroblocks (MaxFS) and the macroblocks a second (MaxMBPS): 3.1 is 3,600 and 108,000 (1280 by 720 at 30 a second, exactly), 4 is 8,192 and 245,760 (1920 by 1080 at 30: 8,160 and 244,800), 5.1 is 36,864 and 983,040 (3840 by 2160 at 30); level_idc is ten times the level number; profile_idc 66 Baseline, 77 Main, 100 High | ITU-T H.264 (V15, 08/2024), Annex A, Table A-1 and A.2, https://www.itu.int/rec/T-REC-H.264 (free) | the table, pages 296 to 298 | P |
| The MP4 container: ISO/IEC 14496-12 (the ISO base media file format) | ISO; sold. ISO's list of publicly available standards loads by script and was not read; two guessed links to free copies answered with an HTML page | | not read (the box layout from two implementations, below) |
| MediaRecorder: records a stream (a canvas's `captureStream(fps)`) in real time; `isTypeSupported(type)` asks for a container and codec; `start(timeslice)` hands the data over in Blobs through `dataavailable` | W3C MediaStream Recording, https://github.com/w3c/mediacapture-record (MediaRecorder.bs) | the IDL and the start algorithm | P |

## 3. Browser support

| Fact | Source | Level |
|---|---|---|
| VideoEncoder and VideoFrame: Chrome and Edge 94, Firefox 130 (desktop; not Firefox for Android), Safari 16.4 (and iOS) | MDN browser-compat-data, api/VideoEncoder.json, api/VideoFrame.json, https://github.com/mdn/browser-compat-data | P (MDN's data) |
| MediaRecorder: Chrome 47, Firefox 25, Safari 14.1 (iOS 14); a canvas's `captureStream`: Chrome 51, Firefox 43, Safari 11 | the same, api/MediaRecorder.json, api/HTMLCanvasElement.json | P (MDN's data) |
| **Tested here** (headless Chromium 141, the one the suites run in; 2026-10-24): WebCodecs only in a secure context (a `file://` page is one, `about:blank` is not); no H.264 encoder or decoder (`isConfigSupported` false for every avc1 string tried, `canPlayType` empty); VP9, AV1 and VP8 encode at 720p and 1080p; VP9 and AV1 in MP4 play; MediaRecorder takes `video/mp4` (VP9) and `video/webm` (VP8, VP9), not H.264 | a page here, the script in the session's scratch folder | P |

So the app's writer needs two sample entries: `avc1` with `avcC` (H.264: what Chrome, Edge and Safari encode, and
what every player plays) and `vp09` with `vpcC` where H.264 is missing (this Chromium; maybe Firefox on Linux). The
suites can play only the VP9 path back here; the H.264 path is tested by its bytes against a Python reader.

## 4. Open implementations, read as text

| Implementation | Licence | What it shows | Level |
|---|---|---|---|
| mp4-muxer (Vanilagy), `src/box.ts`, `src/muxer.ts` | MIT; deprecated for Mediabunny (MPL-2.0) | the tree for a non-fragmented file: `ftyp` (isom, minor 0x200, isom, avc1, mp41), `mdat`, `moov` (`mvhd`, `trak` (`tkhd`, `mdia` (`mdhd`, `hdlr`, `minf` (`vmhd`, `dinf`/`dref`/`url `, `stbl` (`stsd`, `stts`, `stss`, `stsc`, `stsz`, `stco` or `co64`, `ctts` when needed))))); version 1 boxes when a time passes 32 bits; the `avcC` box is the encoder's description as it is; `vpcC` built from the codec string | S (an implementation) |
| FFmpeg, `libavformat/movenc.c` | LGPL 2.1, read only, nothing taken | the same boxes; in MP4 (not QuickTime) mode `hdlr`'s pre-defined field is zero, where mp4-muxer writes QuickTime's `mhlr`; FFmpeg cites ISO 14496-12 8.4.3.3 for the handler name | S (an independent implementation) |
| valdrada's procedural pedestrians and trees | MIT | not about video: read for the owner's question on generators (2026-10-24, the chat): a walk cycle in the vertex shader about joint pivots, trees grown to a crown envelope | P (its code) |

The two implementations agree on the box tree and the fields the app needs, but on `hdlr`'s pre-defined field,
where the app follows FFmpeg's MP4 mode. The box layout is S until ISO 14496-12 is read; the files the app writes
are checked by the browser playing them and by a reader of our own in the suite.

## 5. Edges

- **H.264 wants even sizes**, and its level caps the frame size: 1280 by 720 is level 3.1's limit exactly, 1080p
  needs level 4, 4K level 5.1 (Table A-1); the codec string's level is chosen from the frame size and the frame
  rate, a size between rounded up to whole macroblocks (16 pixels).
- **WebCodecs needs a secure context**: the app opened from `file://` has it; a plain `http://` host would not.
- **The WebGL canvas keeps no buffer** (`preserveDrawingBuffer` is not set): a frame is copied from it in the same
  task it was drawn in, then the 2D overlay over it. The same holds for WebGPU's canvas until it is presented.
- **"Save image" loses the 3D model today** (tested here: a truck in a 3D view drawn by WebGL; the saved overlay
  77% transparent where the truck is): `bimSaveViewportPng` saves only the overlay canvas. The frame copy fixes it.
- **Back-pressure**: frames are encoded faster than real time only while `encodeQueueSize` stays small; the export
  waits when it grows.
- **Time**: every frame at an exact time (frame n at n/fps), whatever the machine's speed; the encoder's
  timestamps in microseconds, the file's in its own timescale (30 fps in 30000 or 90000 units).
- **MediaRecorder records in real time**: a frame slower than 1/fps is a frame lost or stretched; it is the
  fallback only, said.
- **A hidden page** stops `requestAnimationFrame`: the animation clock pauses with it.

## 6. What the app has (read 2026-10-24)

- `paint()` draws a frame on demand (after an edit, a camera move); nothing runs on its own between edits. The 3D
  view is drawn by `bimRender3D` on one of two stacked canvases (`a3d-gpucanvas`, WebGPU; `a3d-glcanvas`, WebGL)
  under the 2D overlay (`a3d-canvas`), which draws the diagram engine's elements, labels and grips.
- The diagram engine (V164) draws each element from its style: `stroke`, `w`, `dash`, `head`, `op`, `fillOver`.
  Marching dashes are `lineDashOffset` moved by the clock; drawing on is a part of the path's length; a ring grows
  by its radius; a layer is revealed by its alpha.
- The sun study's date and time are site settings (V107); the shadows (V164) and the sun path are worked out from
  them, so a day's sweep is the clock setting the time.
- V155's BENCHMARK already draws frames one after another and times them.

## 7. Still open

- ISO/IEC 14496-12 itself (sold; the free list not read).
- Whether Safari plays VP9 in MP4 (it encodes H.264, so it should not need to).

## 8. The owner's decisions (2026-10-24)

1. **When things move:** still until Play, with Pause always there (WCAG 2.2.2); paused at first where the device asks
   for reduced motion.
2. **Which motions:** all four: marching dashes on flows, walks and transit; winds drawn on; walk-time rings growing and
   the layers revealed in turn; the sun and shadows through a day.
3. **Video:** none: "i dont need export motion. just on the app for visual". The MP4 writer chosen on 2026-10-19 is
   dropped; sections 2 to 5 keep what was read about it, should it be wanted later.
4. **Stills:** "just image at the moment it captured no video export": Save image takes the view at that moment, the 3D
   model included (section 5).

## 9. As built (V170, 2026-10-24)

The design follows the decisions above; where they left a choice open, the app's own conventions decided it,
and each such choice is named here for the owner to overrule.

**The clock.** One clock, `A3D_ANIM`, for every animated element. It runs by `requestAnimationFrame` while
playing, so it stops by itself while the page is hidden; a frame is painted at most 30 times a second; the time
it keeps is the frames' own timestamps, a slow frame moving it a tenth of a second at most, never a jump.
- **Play** from still starts the clock at nothing; **Pause** keeps the moment drawn (Save image takes it);
  **Play** again goes on from it; **Stop** gives the still drawing back, pixel for pixel. Pause keeping the moment
  and a Stop beside it is the app's choice: a pause that snapped back to the still drawing would lose the moment.
- The app always opens still. A device asking for reduced motion while it plays pauses it (WCAG 2.3.3); Play
  pressed then plays, being asked for.
- Nothing the clock does is saved or undone. While the sun plays, its time stands in for the study's in the sun's
  one reader (`bimSunNow`); the project's date and time do not change, and Properties shows the study's own.
- Sheets, prints and exports are drawn still.

**Where the buttons are.** Play, Pause and Stop sit in the status bar after the view's own buttons (V109: nothing
floats over the drawing), shown only when something can move: an analysis shown, or the sun study on in plan. On a
phone or a tablet (up to 1024 px, where V169's bar already ran past the screen) they come first, as icons named
for screen readers, the level's caption giving them its room. `PLAY` (`ANIMATE`, `PAUSE`, `MOTION`) toggles.

**Motion is a style.** Each element carries `s.anim`: unset, its analysis's own; `none`, still; or another its
shape can take (a line or a polyline can march; a line or a closed shape can be drawn on; a closed shape can grow
as a ring). Properties offers them as **Motion**; a change is one undo step and, like any change of style, is
kept when the analysis runs again. Each analysis's own:

| Analysis, elements | Motion | Way |
|---|---|---|
| Water flow: the flow lines and where the site drains; Views: the view lines; Vehicle access: the entries | marching dashes | as drawn (they carry arrowheads) |
| Transit: the bus and tram routes | marching dashes | as drawn |
| Walk times; Daily needs; Transit: the ways to the stops and the streets within a walk of them | marching dashes | away from the site's centre, each line, pair of segments and polyline turned |
| Winds: the prevailing winds | drawn on, tail to tip, held, faded, one after another | |
| Compass and distance: the 100 m rings | growing outward | |
| Sun paths: the sun now; Shadows: each shadow | through the day | |

The owner named flows, walks and transit; the view lines and the vehicle entries are counted as flows (of sight,
of vehicles), the app's reading.

**The numbers** (`BIM_ANIM`, read by the suite's reference): a march moves 28 px a second; a solid line's moving
dashes are 6 px plus twice its width, with 14 px plus twice its width between, in its colour 60% toward white (50%
toward black on a pale line); a dashed line's own dashes move. A wind grows over 1.6 s (smoothstep), holds 1.8 s,
fades over 0.6 s and rests 0.5 s, the next one 0.35 s behind. The ripple moves out 150 m a second of play, each ring
left as the front passes it, the front drawn by the smallest ring not yet reached, held 2.2 s at the outermost; a
ring's words wait until it is whole. At each Play from still, the shown analyses come in in Analyze's order, 0.45 s
apart, each over 0.5 s. The sun sweeps from sunrise to sunset of the study's day (all day under the midnight sun;
not at all in the polar night or without the site's place) in 24 s, held 1.2 s at sunset; it moves on the sun
paths' dome, now kept with the run, with its time beside it, and stands in for the sun now. The shadows through the
day are one shadow, the model's, at the sun's moment on the study's day, in the shadows' colour; the V107 sun study
in plan follows the same clock.

**Save image.** The model is on a canvas of its own under the overlay (WebGPU or WebGL), which keeps no picture
once its frame is shown (`preserveDrawingBuffer` unset). Save image draws the view and copies that canvas in the
same task, then lays the overlay over it, so the image has the model, the drawing and the motion as it stands.
Headless Chromium here has no WebGPU; the copy is the same from its canvas (`drawImage` of a WebGPU canvas before
it is presented), checked on WebGL here.

**Checked by** `tests/bim_phase170_animation_browser_tests.py` (104 checks) against `tests/animation_reference.py`,
the design written out again in Python, and the canvas's own pixels; broken 83 ways by `Phase/falsify_phase170.py`.
