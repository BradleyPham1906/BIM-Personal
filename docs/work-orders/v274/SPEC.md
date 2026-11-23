# V274 spec: XR-1, the headset view

Research: `docs/research/research-devices-xr.md` and its topic notes (`web-on-iphone.md` part 3, Q2 and Q5, is the
source for every formula here). The owner's decisions, 2026-11-23: D1 to D9 all as the research recommends ("all as
recommended"); D10 approved. Measured on the owner's iPhone 13 (E3): two eyes with lens correction, the camera and the
physics held 35.4 frames a second with the hands on; drawing alone took 1 to 2 ms. Implementation target: local
`main`. Written by Claude, 2026-11-23.

## 1. What it does for the user

The rendered view gains a **Headset** mode for a phone in a cardboard viewer. The screen splits into two eyes placed
on the viewer's lenses, each drawn with the lens correction, and the view turns with the head (the phone's motion
sensors; turning only, not moving). Walking is walk mode's joystick or a tap. The viewer's settings come from its QR
code (the link the phone's Camera app opens, pasted once) or default to Google Cardboard v2. The camera can show
behind the model. It works best from the Home Screen app (full screen, the screen kept awake). On a computer without
motion sensors the view is dragged to look around, so the mode can be checked anywhere.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/render/headset.js` | new, after `js/engine/render/splats.js` in `src/index.html` (header done) | 9 pure functions (part 4) | Cline, WO-01 to WO-09 |
| `docs/work-orders/v274/v274.test.mjs` | new | their tests | Claude (done) |
| the rendered view and walk mode | changed | the mode, drawing the two eyes, the settings, saving them | Claude, WO-10 |

## 3. Data

- **A viewer profile** `P`: `{vendor: string, model: string, sl: screen-to-lens metres, il: lens spacing metres,
  fov: [outer, inner, bottom, top] degrees for the left eye, valign: 'bottom'|'center'|'top', tl: tray-to-lens metres,
  k: [K1, K2, ...], button: 'none'|'magnet'|'touch'|'indirect'}`. Google Cardboard v2, the default:
  `{vendor: '', model: '', sl: 0.039, il: 0.064, fov: [60, 60, 60, 60], valign: 'bottom', tl: 0.035, k: [0.34, 0.55],
  button: 'magnet'}`.
- **A screen** `S`: `{w, h}` in device pixels in landscape (iPhone 13: 2532 x 1170), `ppi` (460), `bezel` metres
  between the screen's bottom edge and the glass edge the tray touches (default 0.004).
- **A layout** `L`: `{mpp: metres per device pixel, lensL: [x, y], lensR: [x, y]}`, the lens centres in device pixels
  from the screen's bottom-left corner.
- **An eye's field** `{left, right, bottom, top}`: tangents of the half-angles, as a three.js off-axis frustum takes them.
- **A quaternion** `[x, y, z, w]`, three.js's order. Y up, the view looking down -Z.

## 4. Functions, `src/js/engine/render/headset.js`

ES5. Every function is pure: it never changes what it is given; it uses no name from another file.

### WO-01 `bimHsUrlBytes(url)`
- **Takes:** a viewer's QR link, e.g. `https://google.com/cardboard/cfg?p=CgxHb29nbGUs...`.
- **Returns:** a `Uint8Array` of the bytes in its `p` parameter, read as URL-safe base64 (`-` is `+`, `_` is `/`,
  `=` padding added to a multiple of 4), as the Cardboard SDK does (`sdk/qrcode/ios/device_params_helper.mm`);
  `null` when there is no `p` parameter, it is empty, or it is not base64. `atob` decodes.
- **Example:** the Cardboard v1 link in the tests gives its 77 bytes, starting `0x0a 0x0c 0x47`.

### WO-02 `bimHsProfileDecode(bytes)`
- **Takes:** the bytes of a Cardboard `DeviceParams` protobuf (`proto/cardboard_device.proto`, proto2).
- **Returns:** a profile `P` (part 3): start from the Cardboard v2 default and replace each field present:
  1 vendor (string), 2 model (string), 3 sl (float), 4 il (float), 5 fov (repeated float, packed or not; used only
  when exactly 4 arrive), 6 tl (float), 7 k (repeated float, packed or not), 11 valign (varint: 0 bottom, 1 center,
  2 top), 12 button (varint: 0 none, 1 magnet, 2 touch, 3 indirect). Floats are little-endian float32, rounded to
  6 decimals. Wire types: 0 varint, 1 skip 8 bytes, 2 length-delimited (fields 1, 2, 5, 7 read; others skipped),
  5 four bytes. An unknown field is skipped; an unknown enum value keeps the default.
- **Errors:** empty or null bytes, a field running past the end, or wire types 3, 4, 6, 7 give
  `{error: 'the viewer settings could not be read'}`.
- **Example:** Cardboard v1's bytes give `{vendor: 'Google, Inc.', model: 'Cardboard v1', sl: 0.042, il: 0.06,
  fov: [40, 40, 40, 40], valign: 'bottom', tl: 0.035, k: [0.441, 0.156], button: 'magnet'}`.

### WO-03 `bimHsDistort(k, t)`
- **Returns:** `t (1 + K1 t^2 + K2 t^4 + ... + Kn t^(2n))` for the coefficients `k` (none: `t`).
- **Example:** `bimHsDistort([0.34, 0.55], 0.5)` is `0.5596875`.

### WO-04 `bimHsLayout(P, S)`
- **Returns:** `L`: `mpp = 0.0254 / S.ppi`; the lenses `S.w / 2 -/+ P.il / 2 / mpp` across; up from the bottom:
  `(P.tl - bezel) / mpp` for 'bottom', `S.h / 2` for 'center', `S.h - (P.tl - bezel) / mpp` for 'top'; `bezel` is
  `S.bezel`, 0.004 when not given.
- **Example:** Cardboard v2 on 2532 x 1170 at 460 ppi: `mpp` 5.5217e-5, `lensL` [686.47, 561.42], `lensR`
  [1845.53, 561.42].

### WO-05 `bimHsEyeTan(P, S, L, eye)`
- **Takes:** `eye` 'left' or 'right'.
- **Returns:** the eye's field: each side is the smaller of the lens's limit and the screen's. The lens: `tan` of
  `P.fov` in degrees, `fov[0]` the outer side (left for the left eye, right for the right eye), `fov[1]` the inner
  side, `fov[2]` bottom, `fov[3]` top. The screen: the distance in metres from the eye's lens centre to that edge of
  the eye's half of the screen (the left eye's half is x from 0 to `S.w / 2`, the right eye's from `S.w / 2` to
  `S.w`; bottom is 0, top `S.h`), divided by `P.sl`, then through `bimHsDistort(P.k, ...)`.
- **Example:** Cardboard v2 on the iPhone 13 above, left eye: `{left: 1.7320508, right: 1.2128752, bottom: 1.1401467,
  top: 1.3403824}`; the right eye has `left` and `right` swapped.
- **Uses:** `bimHsDistort` (this file).

### WO-06 `bimHsHeadQuat(alpha, beta, gamma, screenDeg)`
- **Takes:** a `deviceorientation` event's angles in degrees and the screen's angle (`screen.orientation.angle`,
  0, 90, 180 or 270; missing is 0).
- **Returns:** the camera's quaternion, as three.js's former DeviceOrientationControls made it: the Euler angles
  (x = beta, y = alpha, z = -gamma, in radians, order 'YXZ') as a quaternion `q`, times `[-sqrt(1/2), 0, 0, sqrt(1/2)]`
  (the camera looks out of the back of the phone), times a turn of `-screenDeg` about Z (`[0, 0, sin(-s/2), cos(-s/2)]`).
  For 'YXZ', with `c1, s1` the cosine and sine of x / 2, `c2, s2` of y / 2, `c3, s3` of z / 2:
  `q = [s1 c2 c3 + c1 s2 s3, c1 s2 c3 - s1 c2 s3, c1 c2 s3 - s1 s2 c3, c1 c2 c3 + s1 s2 s3]`.
  Quaternion product `a b`: `[aw bx + ax bw + ay bz - az by, aw by - ax bz + ay bw + az bx, aw bz + ax by - ay bx + az bw,
  aw bw - ax bx - ay by - az bz]`. `null` when alpha, beta or gamma is null or undefined.
- **Example:** `(0, 0, 0, 0)` (flat, face up) gives `[-0.7071068, 0, 0, 0.7071068]` (looking down); `(0, 90, 0, 0)`
  (upright in portrait) gives `[0, 0, 0, 1]` within 1e-12 (looking ahead).

### WO-07 `bimHsYaw(q)`
- **Returns:** the heading of the view in radians: the forward vector `f = q (0, 0, -1)`, so
  `fx = -2 (x z + w y)`, `fz = -(1 - 2 (x x + y y))`; the answer is `atan2(-fx, -fz)`; 0 when both are under 1e-9
  (looking straight up or down).
- **Example:** `bimHsYaw(bimHsHeadQuat(30, 90, 0, 0))` is `30` degrees in radians.

### WO-08 `bimHsRecentre(q, yaw)`
- **Returns:** `q` turned by `-yaw` about the vertical (the quaternion `[0, sin(-yaw/2), 0, cos(-yaw/2)]` times `q`),
  so the view's heading starts at 0 where the user is looking.
- **Example:** `bimHsYaw(bimHsRecentre(q, bimHsYaw(q)))` is 0 within 1e-12 for any q not looking straight up or down.

### WO-09 `bimHsSupport(env)`
- **Takes:** `{secure, webgl2, motion, standalone}` booleans.
- **Returns:** `{ok, notes}`: `ok` is `secure && webgl2`; `notes`, in this order, only for what is false:
  `'Open the app over https to use the headset.'`, `'This browser cannot draw the headset view (no WebGL 2).'`,
  `'This device has no motion sensors the page can read; drag to look around.'`,
  `'Add the app to your Home Screen for a full-screen headset view.'`.

## 5. Order of the work

WO-01 to WO-09 in order (WO-05 uses WO-03; WO-07's and WO-08's tests use WO-06). Then Claude: **WO-10** the mode
(part 1): a Headset command in the rendered view; the motion permission asked in the tap that starts it, before any
wait; the wake lock; each eye drawn to its own target with an off-axis frustum from `bimHsEyeTan`, then one full-screen
pass placing them on `L`'s lens centres with the correction (the measured test page,
`docs/research/experiments/devices-xr/phone-test.html`, is the reference); the viewer settings (paste the QR link, or
the default) saved with the app's settings; drag to look without sensors; the camera behind as an option; exit by a
tap at the edge; walk mode's joystick for moving. **WO-11** the tests moved to `tests/unit/`, `npm run modules`, the
one browser check of the new interface. **WO-12** the records (QUEUE, PIPELINE, Notion).

## 6. Not in this phase

Hands (XR-2), the physics hand (XR-3), the link to a computer and splat edits (XR-4); six-degree tracking (needs the
native shell, D1); the viewer's button; reading a QR code inside the app (the Camera app opens the link, D9).
