# OpenBridge UI enrichment: verified intake and adoption plan

Review date: 2026-10-22 (America/New_York). Project: World BIM Platform / BIMULT.
Status: asset intake staged for review; production integration not performed.

## Decision and boundaries

Reuse OpenBridge's static UI symbols, semantic theme/sizing tokens and interaction
patterns. Do not wholesale install its Lit component runtime or copy the latest
upstream/Figma libraries on the assumption that every resource has the same license.
The current BIM app is a single-file, offline-capable application; upstream Lit,
TypeScript decorators, modules, CSS imports and chart dependencies are not a drop-in
fit. This intake leaves `canvas_v10.html`, model persistence, undo, geometry,
engineering results and existing phase baselines unchanged.

The reviewed material is principally maritime/industrial interface design. No usable
3D people, trees, bikes or cars were found in the sources reviewed. UI symbols are
not dimensional simulation assets. Maritime HMI patterns do not confer BIM,
structural, accessibility, class-society or maritime safety compliance.

## Critical license finding

The website's terms call the guidelines Apache-2.0, but that is NOT evidence that
all current repository commits or Figma assets can be redistributed under Apache.

| Resource | Evidence actually read | Intake decision |
| --- | --- | --- |
| Website guidelines | [Terms](https://www.openbridge.no/terms-of-service) describe Apache-2.0 and identify Google fonts/material icons | Use guidance with attribution; no brand/logo reuse implied |
| Selected code snapshot | [`LICENSE.TXT`](https://github.com/Ocean-Industries-Concept-Lab/openbridge-webcomponents/blob/eb2013003cbb323ded47674576e5b273df0a2566/LICENSE.TXT) and package metadata at `eb2013003cbb323ded47674576e5b273df0a2566` directly say Apache-2.0 | Import ONLY from this pin; retain exact license and provenance |
| Newer reviewed snapshot | [`LICENSE.txt`](https://github.com/Ocean-Industries-Concept-Lab/openbridge-webcomponents/blob/2b24042487f3d112de04a91bcdfa6d33691d84bf/LICENSE.txt) starts under AGPL-3.0-only; Apache becomes an additional option 180 days after each version/commit's first public availability; separate commercial terms available | Not imported; no blanket relicensing or automatic `@latest` updates |
| Figma design system/icon pack | Official landing pages and links read; actual file contents, exports and asset-specific terms NOT inspected | Not imported. Verify file-specific rights, attribution and export provenance first |
| Fonts, logos and certification marks | Website references fonts; no font files/brand rights audited | Not bundled; use system fonts; no partnership/compliance claims |

Selected snapshot metadata: commit dated 2026-04-24; package `2.0.0-next.9` (a
prerelease, not an endorsement of production stability). The older snapshot's direct
Apache grant is the basis for this intake; no reliance on an inferred 180-day change
date. Root/source-directory listings did not show a NOTICE file; this is not an
exhaustive nested audit. Original source and full license appendix are preserved.
Retain any applicable notices when adding further files. This is a documented license
screen, not legal advice or an organization-wide legal approval.

## What is actually included

- 17 curated 24 x 24 static SVGs: aircraft-drone-small, alert-list, camera,
  chart-layers, chart-search, chart-settings, check-google, chevron-down-google,
  close-google, edit-google, expand, file-download-google, file-upload-google,
  filter, help, history-google, home.
- Original 17 TypeScript wrappers retained under `vendor/openbridge/source/icons/`
  as reference data only. The first `private icon = svg` value is extracted
  byte-for-byte; Lit wrappers and CSS-color variants are not executed/bundled.
- 124 scoped token values: 28 semantic color values in each of day, bright, dusk,
  night, plus 3 sizing values in each of regular, medium, large, xl. Original
  `variables.css` (662,349 bytes) is vendored as source reference ONLY. Never add
  that global stylesheet to the live application. Selected CSS selectors are
  scoped under `.bim-ob-preview` and dependencies are literal values.
- ES5 lookup adapter with vetted-name allowlisting, escaped accessible labels,
  decorative SVG defaults, no network requests and no npm runtime dependency.
- Offline `wip/openbridge-ui-preview.html`: search, clear empty state, four themes,
  icon selection and real SVG download. No fake BIM/model/simulation controls.
- Exact pin, per-source Git blob SHA-1/SHA-256, extracted-file hashes,
  transformation notes and license hash in `vendor/openbridge/manifest.json`.
- Existing root third-party notices preserved, with a dedicated OpenBridge section
  appended; full original license at `vendor/openbridge/LICENSE.TXT`.

The official icon landing page advertises 2,000+ icons. That is the publisher's
claim, NOT our inventory or import count. GitHub's icon directory response was capped
at 1,000 alphabetical entries, so it was not an exhaustive catalog. Only the 17
named, fetched and validated sources above are imported. Expanding the catalog is
possible after per-file inspection and license review at the same pin; it is not
represented as complete in this change.

## Source register and access depth

P = primary content actually read. L = linked/discovered, not inspected internally.
No search snippets, metadata-only hits or inaccessible files are treated as proof of
implementation details.

| Level | Source | Evidence and limitations |
| --- | --- | --- |
| P | [Develop](https://www.openbridge.no/develop) | Links webcomponents, Storybook and demo. Access/JIP language conflicts with dates; not a legal grant for latest code |
| P | [Design](https://www.openbridge.no/design) | Core Figma library, icon pack and case-library entry points; older versions archived |
| P | [Terms](https://www.openbridge.no/terms-of-service) | Website guideline license; distinguish from per-commit code licenses |
| P | [Icons](https://www.openbridge.no/cases/openbridge-icons) | Publisher's 2,000+ symbol claim and Figma entry point; no bulk Figma export inspected |
| P | [Application patterns](https://www.openbridge.no/cases/application-pattern) | Navigation/layout/scaling concepts useful for a BIM shell; linked detailed Figma file not read |
| P | [Alerts](https://www.openbridge.no/cases/alerts) | BAM/CAM/history/acknowledgement and shelving concepts; not BIM risk rules |
| P | [Automation](https://www.openbridge.no/cases/automation) | Industrial symbols/patterns potentially useful for later MEP/system views, not simulation solvers |
| P | [Pinned repository](https://github.com/Ocean-Industries-Concept-Lab/openbridge-webcomponents/tree/eb2013003cbb323ded47674576e5b273df0a2566) | Root license, package metadata, README, component directories, button/slider/alert-menu source, full palette and the 17 icon source files |
| P | [Newer license](https://github.com/Ocean-Industries-Concept-Lab/openbridge-webcomponents/blob/2b24042487f3d112de04a91bcdfa6d33691d84bf/LICENSE.txt) | Per-version delayed permissive licensing; newer source excluded from import |
| L | [Stable Storybook](https://openbridge-storybook.web.app/) / [demo](https://openbridge-demo.web.app/) | Discovered entry points, not interactively tested; no inferred behavior from screenshots |
| L | [Figma icons](https://www.figma.com/community/file/1445713209741917748/openbridge-icon-pack) | Contents and terms not inspected |
| L | [Figma core 6.0](https://www.figma.com/community/file/1468161149546275705/openbridge-design-system-6-0-maritime-industrial-ui-ux-components) | Contents and terms not inspected |
| L | [Figma application patterns](https://www.figma.com/community/file/1486350615717873940/openbridge-6-0-application-patterns) | Contents and terms not inspected |

## Fit to existing tasks (no renumbering or rescheduling)

| Workstream | Useful reuse | Explicit limit / next gate |
| --- | --- | --- |
| V169: people, bikes, cars and trees | Category/library UI, search/filter/settings and upload symbols | No replacement for procedural/glTF dimensional geometry. Existing Paused status and baseline preserved |
| V170: animated site analysis/video | Transport/settings/export-control patterns and button/slider design references | No imported animation clock, traffic behavior, encoder, MP4 writer or export integration; no claim that this pin supplies every desired media symbol |
| V173: Contents pane | chart-layers, filter, chart-search, chart-settings, expand, clear controls; consistent selected/focus states | Wire to the existing layer stack, not an independent state store; confirm category/source/selection behavior |
| Cross-cutting UI foundation | Forms, menus, navigation, panels, tables, focus/disabled/busy states, alerts/history concepts | Adopt incrementally after command mapping and app regressions; separate from phase completion |
| Later automation / MEP | Symbols and diagram conventions as reference | No solvers or calibrated engineering instruments imported |

Notion calls the Contents pane V173 and animation V170; main PIPELINE still uses
older numbering (Contents V172, traffic V170). This pre-existing discrepancy is
recorded, NOT silently corrected by this UI intake; identify tasks by title and
Notion link, preserve the existing parametric-planning PR and all adjacent phases.

## Adoption sequence and acceptance gates

1. **Intake (this change):** pin, inspect, license, extract, scope, test and expose
   a real offline asset workbench. No live app behavior change.
2. **Low-risk UI integration:** inventory real toolbar/menu selectors and command
   handlers; replace decorative glyphs and add accessible names while preserving
   shortcuts, hit targets, disabled states and original command calls. Inline
   selected data/helper only in the single-file distribution; relative assets alone
   are not sufficient for its standalone contract.
3. **Panels and Contents:** propose a small before/after layout; translate tokens
   into the app's semantic variables, never global selectors. Test bright/dark,
   keyboard focus, scaling, long names, selected/multi-selected layers, touch input.
4. **Analysis and export controls:** review parameter validation, busy/progress,
   cancellation, history and preview states; retain existing units, algorithms and
   encoder behavior. Do not conflate a new icon with a working feature.
5. **Warnings/history:** separate informational messages from engineering errors.
   Never hide/shelve failed checks or make acknowledgement mean the underlying
   defect is resolved. Preserve provenance and warnings on model reopen/export.
6. **Expansion:** review additional icon categories per-file and Figma rights
   separately. Avoid maritime-specific imagery unless a real BIM need exists.

Before merging any production integration: owner review, per-revision license
screen, original full regression suite, file:// and served operation, standalone
single-file launch, model save/reopen and undo/redo, deterministic engineering
results, keyboard/screen-reader labels, focus/contrast/touch checks, memory/performance
budget and offline/no-unexpected-network tests. The current asset preview is NOT
proof those production gates passed. No dates/hours or engineering approvals invented.

## Verification performed for this intake

Commands from repository root:

```sh
python3 tools/openbridge/verify_assets.py
node tools/openbridge/test_adapter.cjs
node tools/openbridge/test_preview.cjs
```

The first two use stdlib Python/Node; optional locally available `acorn` checks ES5
syntax (explicit skip if absent). The preview test needs an available Playwright
installation and Chromium; no dependencies are auto-installed. Set `CHROMIUM_PATH`
if different from `/usr/local/bin/chromium`.

- Asset suite: 5 unittest methods passed, with per-icon subtests, deterministic
  source extraction/hashes, SVG tag/attribute/reference allowlists, 124 token-value
  comparisons/scoping checks, license and helper checksums.
- Negative checks: script/event/href/remote-URL/declaration/interpolation SVGs
  rejected; altered bytes fail the manifest hash comparison.
- Adapter: 29 checks passed including actual ES5 parsing with locally available
  acorn, unknown/prototype names, escaped hostile labels, decorative/named semantics,
  all 17 icon lookups and defensive list copying.
- Preview: 25 browser assertions passed: search, hostile query/empty state, selection, Reset, exact-byte Blob download, all four themes, dark-mode default, 1200/390px layouts, zero page errors and zero HTTP(S) requests. The first file-link download test failed; the preview was fixed to download a Blob from the verified local registry and rerun successfully. Only asset-workbench behavior is covered.
- Visual inspection: desktop 1200px, mobile 390px mobile dusk/empty and desktop night/selected states rendered
  and inspected. No horizontal overflow, clipped content, console errors or failed
  local resources in those captures. Long names wrap and empty state offers Reset.
- Not run: existing 127 app suites / 6,144 historical checks, full BIM model/UI tests,
  upstream webcomponent tests, Safari/iOS, a full accessibility conformance audit,
  engineering verification or certification.

No claim of live deployment, complete OpenBridge catalog import or app-phase
completion is made. Review branch/PR acceptance does not automatically integrate the
kit into the production HTML.

## Notion-first tracking

The source audit and task annotations were written in Notion before any repository mutation.

- Research record: https://app.notion.com/p/8fd9a7ef32534332a8797ba08a380c0b
- Adoption task: https://app.notion.com/p/95e4ceb76a904213adf2b8a7453885f1
- Project: https://app.notion.com/p/3f0cbfcc3a388044a55ffa8af0adead8
- V169 Assets: https://app.notion.com/p/3fecbfcc3a38813098bfc7c8d9a46ab0
- V170 Animated site analysis/video: https://app.notion.com/p/3fecbfcc3a3881aeb276e581b5d92a82
- V173 Contents pane: https://app.notion.com/p/3fecbfcc3a388141a93be73520d09591
