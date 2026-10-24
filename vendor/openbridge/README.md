# OpenBridge: pinned, offline UI asset kit

Staged for review, not wired into `canvas_v10.html`.

- Upstream: Ocean-Industries-Concept-Lab/openbridge-webcomponents
- Commit: `eb2013003cbb323ded47674576e5b273df0a2566` (`2.0.0-next.9`)
- License: Apache-2.0 directly at this pin; original `LICENSE.TXT` retained verbatim.
- 17 static SVG icons, ES5 lookup adapter, 124 selected/scoped token values.
- Full upstream palette and icon wrappers are reference source only, NOT runtime.
- Per-file source URLs, blob/hash verification and changes: `manifest.json`.
- Full evidence, license differences, limitations and integration gates:
  `../../reference/research-openbridge.md`.

Open `../../wip/openbridge-ui-preview.html` locally from the repository tree. No
server, CDN, web font or package installation required for that preview.

```html
<script src="vendor/openbridge/icons.es5.js"></script>
```

```js
// Vetted SVG data only. Decorative when beside a visible action label:
BIMOpenBridgeIcons.svg('chart-layers');
// Named graphic (labels are escaped):
BIMOpenBridgeIcons.svg('home', 'Home');
// Unknown names return an empty string. A new array is returned each time:
BIMOpenBridgeIcons.names();
```

In an icon-only button, name the BUTTON for its action and use a decorative icon.
Do not treat SVG text interpolation as safe for arbitrary caller markup. This helper
accepts a vetted icon name and an escaped plain-text label, not uploaded SVGs.

`tokens.scoped.css` has no global selectors; values apply only inside
`.bim-ob-preview[data-obc-theme="day|bright|dusk|night"]` (one actual value at a time).
Size classes: `.obc-component-size-regular|medium|large|xl`. Do not load
`source/variables.css`: it contains upstream global rules. Production adoption must
map reviewed values into existing app semantics and inline the selected assets to
preserve the standalone single-file/offline contract.

Tests from repository root:

```sh
python3 tools/openbridge/verify_assets.py
node tools/openbridge/test_adapter.cjs
node tools/openbridge/test_preview.cjs
```

Python stdlib/Node for asset and adapter checks; optional acorn for ES5 parser.
Browser test requires preinstalled Playwright/Chromium; it installs nothing.
Do not replace the upstream pin automatically: newer reviewed commits have different
initial licensing. Figma exports, logos, fonts and 3D simulation geometry are not
included. Retain this attribution, manifest and license when redistributing assets.
