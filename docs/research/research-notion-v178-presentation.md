# V178 Presentation P3 — report generation, reusable styles and export

Research date: 2026-11-13. Scope: V178, World BIM Platform. This is a research synthesis, not a specification, an approval, or proof that the app implements the proposed features. The repository was read from public `main` without a pinned commit; it can change. This research has not passed the repository's independent-review and data-service exit gates.

## Abstract

How can the app generate editable, traceable Site Analysis and DA reports from its existing model and analysis results, reuse brand and layout assets, present the resulting boards, and export them without misleading the reader or destroying the existing layer architecture? The evidence supports extending the existing paper-space boards, layer table, live fields, map frame, and presentation sequence—not introducing another board scene graph. Preserve all three requested content families: eight Site Analysis boards, six distinct Giraffe-style DA sheets, and the expanded archiMap-style content, each with its own source and coverage requirements. Recommend editable live documents plus an explicit frozen export manifest, per-value provenance and source-availability states, and editable text/vector output with disclosed raster exceptions. These are recommendations, not owner-approved decisions. A small isolated Chromium experiment supports one narrow PDF result, not production readiness.

## 1. Research questions and falsifiable hypotheses

| # | Hypothesis | Finding and confidence |
| --- | --- | --- |
| H1 | Existing presentation mode must be replaced to show ordered boards. | Not established; current `present.js` already has a sequence and navigation. Extend after testing. P, medium. |
| H2 | All requested content is contained in eight boards. | Unsupported: the eight-board task, six observed DA sheets and archiMap reference are separate inventories. P, high on source wording; page mapping remains design work. |
| H3 | Existing live fields provide every metric and an auditable frozen report. | Failed as a general claim: the inspected fixed registry covers selected live fields, not a documented complete source manifest for the expanded scope. P, medium. |
| H4 | A map rendered in the app can always be exported. | Failed as a general claim: cross-origin canvas readback can raise SecurityError; whether a given provider allows it requires a separate test. P, high for browser security rule. |
| H5 | All map legends are necessarily complete. | Not demonstrated: inspected `board-map.js` slices classes to 12 per data layer, and obtains rows from visible data layers. Whether this causes an actual user-visible omission requires an app fixture. P, medium. |
| H6 | Screen blend and mask behavior must always survive printing. | Not established. One locally generated Chromium PDF preserved one Multiply sample and one SVG mask sample. It does not establish all modes, browsers or the app. P experiment, low generality. |
| H7 | Weather data labelled free may be used by a commercial product without additional terms. | Failed for Open-Meteo's free API: its terms restrict it to noncommercial use. P, high as of access. |
| H8 | A geographic buffer estimate is the observed number of people inside that buffer. | Not established: aggregation across source geographies needs a documented allocation or a source natively resolving the area; do not present an inferred count as an exact observation. U for a selected method. |
| H9 | PowerPoint inherently requires every board to be a flat image. | Failed as a file-format claim: Microsoft documents editable shapes, images and tables as possible parts of PresentationML slides. Fidelity of a particular export implementation is untested. P, high for format, low for app. |

## 2. Method and evidence boundaries

Sources inspected: the task and previous V174 owner decisions in Notion; public project source and research/reference notes; the repository's research and work-order protocol; primary vendor and provider documentation from Canva, Microsoft, Open-Meteo, Overture and FEMA; MDN on canvas security. The independent evidence tiers are P = source or direct experiment, S = reliable secondary reproduction, U = unverified proposal. A single author performed this synthesis: no independent researcher has checked the claims. No runtime of the actual BIM app, data-provider HTTP/CORS probe, full regression, licensed standard inspection, or cross-browser/phone test was performed. The test below is an isolated browser fixture, not an app test.

Search and reading log, reproducible by following the URLs in §12: repository `docs/research/research-protocol.md` and `docs/work-orders/README.md` for required process; `research-da-report-reference.md` and `research-archimap-site-report.md` for requested outputs; `live-sources.js`, `live-board.js`, `board-map.js`, `board-figures.js`, and `present.js` for available mechanisms; Canva Components for propagation/overrides; Microsoft PresentationML for editable object packaging; Open-Meteo terms and Overture attribution for counterexamples to unrestricted data reuse; FEMA NFHL for effective versus preliminary/pending data; MDN CORS for the export failure mechanism. This is a reading log, not a complete search-engine query log. Search and contradiction testing for each provider and feature remain required before protocol exit.

## 3. Preserve the complete requested output

The task asks for eight Site Analysis boards in order: (1) location and context; (2) zoning summary; (3) landform and water; (4) climate; (5) access; (6) risks; (7) constraints and opportunities; (8) buildable area and yield. These are not a replacement for the observed six Giraffe DA sheets:

| DA sheet | Reference content | Sources and failure conditions |
| --- | --- | --- |
| DA-01 | Context plan, site boundary, sun and winds | Site geometry and CRS; verified source and period for climate; missing weather is not zero wind. |
| DA-02 | Site coverage, GFA/FSR, charts | Polygon areas, model floor areas and explicit jurisdictional denominator; do not assume synonyms have the same legal definition. |
| DA-03 | Axonometric model plus three shadow studies | Saved model, geolocation, true north, date, timezone and three explicit times; three views are not a year-round compliance determination. |
| DA-04 | Building-coloured axonometric, identifiers and building schedule | Stable building IDs, geometry revision, floor area and use definitions; totals only across compatible values. |
| DA-05 | Sections/elevations with key plan | Saved cut/view ID, camera/direction, linked key marker and scale; identify stale views after model changes. |
| DA-06 | Perspectives with camera key | Saved camera ID and location; reproducible view extent and key; unavailable renders must be visible as failures. |

The archiMap investigation documented 20 pages from selected video frames, not necessarily the complete product. Preserve the requested additional capabilities: 1/2/3 km population, views and sections, street context, lots, heights, coverage and FAR within 200 m, vehicle flows, business mix/planned business, page palettes and PowerPoint. Do not silently compress them into the eight boards or promise global completeness. Provide traceable mapping from every requested feature to an output, source adapter and explicit status. Exact layout and page grouping are design decisions.

## 4. Evidence: reusable components and brand styles

Canva documents source components, per-instance text/formatting/media overrides, explicit update/sync, preserved customizations, and detachment. It does not auto-sync; nested components and auto-layout are listed as unsupported. This is prior art, not a requirement to copy its limitations or licensing. P, high for what the vendor documents; actual UX not independently exercised.

Recommended model: a named style token library for color, text and line styles; reusable definitions with stable IDs and version; instances referencing definitions and preserving their existing layer IDs; explicit override maps by property; preview before propagation; update only non-overridden fields; detach by copying the resolved ordinary paper objects. Deleting a definition must not silently destroy its instances: prohibit deletion while referenced or keep resolved content and inform the user. A master board should instantiate existing paper objects rather than a second ownership hierarchy. Validate undo/redo, copy/paste, save/reopen, duplicate-ID remapping, old files and locked/plot-disabled layers. Variants should be a versioned definition choice rather than an untracked visual patch. Whether nested components, shared cross-project libraries, permissions, and default propagation are in the first implementation remains an explicit product decision.

## 5. Data contract and methods

Recommended versioned manifest records report ID, project/model revision, generation timestamp and timezone, site geometry reference and CRS, units, board IDs/order, saved camera/extent/scale and layer visibility. Each displayed datum records value, unit, state (available, unavailable, partial, stale, failed), source/provider, dataset/version/vintage, retrieval time, method/assumptions, coverage, relevant uncertainty, license and attribution. An empty value is not numeric zero. Values calculated from several sources must cite all required inputs and the calculation version. The manifest is a proposal, not an observed existing implementation.

**Live versus frozen:** editable boards can refresh from live fields; an export should be bound to one model revision and a frozen set of data, method and visible source credits. Refresh produces a new revision; changes after capture mark the previous result stale rather than rewriting an already issued report. Source changes during generation should either be captured consistently or cause retry/clear failure. Never claim byte-identical reproducibility unless all assets, fonts and render environment are pinned and licensed for retention.

**Spatial statistics:** define rings as cumulative disks or disjoint annuli and label them. Use a defensible metric/geodesic method; 1 km, 2 km and 3 km totals are cumulative and must not be summed. If disjoint counts are derived by differences, trace each source and treat error dependence appropriately. Area-weighting census polygons assumes within-polygon uniformity; it is an estimate, not a direct headcount, and zero coverage differs from no residents. Do not calculate margins of error by simply summing them or choose an uncertainty formula before consulting the actual dataset's methodology. Geographic boundary, CRS, time period, numerator/denominator and disclosure rules need fixture-specific checks. Business counts from Overture/OSM represent mapped records, not a complete business census; de-duplicate only with an explicit auditable method and never assert absence from incomplete data.

**Hazards and zoning:** FEMA describes NFHL as current effective flood data, while preliminary and pending products have different status and do not become effective just by appearing on a map. Absence of coverage is not proof of no flood risk. Show jurisdiction, status, effective/retrieval dates, source and limitations; do not make regulatory determinations without qualified review. Zoning category and boundaries should link to the applicable local source and the actual adopted text; conflicting records remain unresolved, not synthesized into a legally binding answer.

**Provider terms:** Open-Meteo says its free API is noncommercial and lists per-IP/application rate limits; paid plans permit commercial use subject to their terms. Overture's attribution page identifies upstream source-specific obligations (for example, OSM-derived content). Record the specific dataset, license, attribution, caching and commercial rights; neither a successful request nor an open download proves all uses and redistribution are allowed. API availability, quotas, browser CORS, coverage and terms can change and must be rechecked on the real deployed origin.

## 6. Export and presentation alternatives

Criteria fixed before comparison: preservation of requested appearance and editable content, compatibility with the existing board architecture, document portability, failure visibility, and implementation/maintenance risk.

| Route | Strength | Weakness | Recommendation |
| --- | --- | --- | --- |
| Browser print to PDF | Reuses HTML/SVG and gives selectable text in tested fixture | Browser/print settings and SVG/CSS support differ; maps may be raster; not a guarantee of print fidelity | Primary candidate, validate actual app and target readers. |
| Raster entire board | Predictable single-image appearance if source can be captured | Text, vectors and accessibility/editability are lost; CORS and resolution still matter | Explicit fallback for unsupported effects only, with warning. |
| Native vector serializer for PDF/SVG | Potentially portable, selectable vectors | Requires feature-by-feature translation of masks, blending, fonts and images; unsupported operations need a policy | Candidate after a feature matrix and independent validation. |
| PPTX as slide images | Closest to a rendered board if capture succeeds | Content not independently editable; slide aspect/quality and attribution must be preserved | Offer as labelled fidelity-first mode if approved. |
| PPTX with editable text/shapes plus raster map/effects | Text and common graphics can be edited | More mapping, font/geometry differences, no proof of equivalent blend/mask support | Preferred candidate for editability; explicitly record rasterized items and test PowerPoint/LibreOffice. |

PresentationML supports slide masters, layouts, shapes, pictures and tables; this does not establish that any JavaScript library preserves this app's features or has an acceptable license. Test existing `bimPresSeq` navigation and fullscreen before adding presentation controls. For every export target specify page dimensions, DPI, fonts and licensing, alpha, blend mode, mask, text selection, legend/credit behavior and errors. Do not infer PNG, SVG or PPTX fidelity from a PDF result.

A tainted canvas cannot be read with `toDataURL`/`toBlob`; the observed map-frame function calls `toDataURL`. The correct product response is to identify the blocked asset, fail or visibly substitute only with user choice and permissible assets; never evade provider policy through an unauthorized proxy. Test `crossOrigin` configuration and actual response headers from the deployed origin, including redirects and credentials. A simple image request does not inherently require a CORS preflight; test preflight where the request actually requires one.

## 7. Experiment: small print fixture, not the BIM app

Environment: local HTML on Linux, Chromium 153.0.8010.12 headless, GPU disabled; one render/print. Fixture: two A4 pages, `@page` A4 with zero margins, a blue-on-red CSS Multiply example, and an SVG black/white mask. The output PDF had 2 pages, A4 594.96 × 841.92 points; `pdftotext` returned the first- and second-page labels in order. At 96 dpi the sampled Multiply intersection was RGB (0,0,0) in both the screenshot and the rasterized PDF. For the mask a sampled visible green pixel was screenshot (0,128,0) versus PDF (1,128,1); a masked-out sample was white (255,255,255) in both. The PDF contained one `/BM /Multiply` and one `/BM /Normal` marker. These are raw point samples, not a pixel-diff threshold across the page or a proof of vector preservation for every object. A single engine, font, version, print route and fixture cannot establish cross-browser fidelity, production pagination, all 16 blend modes, antialiasing tolerance, CORS behavior, PPTX or responsive layouts. The local fixture was retained separately; no independent replication or app test was performed.

## 8. Current code and concrete implications

- `src/js/engine/sheets/live-sources.js`: a fixed registry, memoization based on revision, units and day, and `ok`, `none`, `gone`, `stale` outcomes. Some model and analysis values exist; a complete frozen provenance manifest was not established by this inspection.
- `src/js/engine/sheets/live-board.js`: schedule, KPI and table logic offers reuse, not proof all required report sources exist.
- `src/js/engine/sheets/board-figures.js`: catalogs several analysis figures and missing-data hints; verify actual data hookups for each output, not just a catalog name.
- `src/js/engine/sheets/board-map.js`: renders to an image data URL at `96/25.4*2` pixels/mm (approximately 192 px/in), catches draw failures, and limits a data-layer legend to the first 12 rows. Its cache key includes the count of successful map tiles; it does not visibly include individual tile identities in the inspected key. If tiles change but the count remains the same, an incorrect cache hit is a plausible risk to test, not a confirmed defect. Per-frame legend correspondence also needs a runtime test.
- `src/js/engine/sheets/present.js`: existing ordered sequence and navigation should be extended and regression-tested before replacement.
- V174's later owner decision uses a single AutoCAD-like layer table: paper objects on existing layers, layer ordering on boards and per-object overrides. New component/report support must honor on/freeze/lock/plot and not introduce a separate board-layer system. This is a prior owner decision, not a new recommendation.

Public `main` was not pinned; line numbers and the current commit must be checked immediately before specification. Do not assume that the inspected source reflects unmerged work.

## 9. Failure cases and acceptance evidence

| Area | Required fixture or check | Expected observable outcome |
| --- | --- | --- |
| Data state | Available zero, missing, stale, failed, partial coverage | Zero remains zero; other states are explicitly distinguished in board and export; no invented total. |
| Geometry | Site straddles two jurisdictions; buffer intersects source polygons | Both jurisdictions and assumptions visible; only covered geometry counted; metric unit conversions checked independently. |
| Climate | Missing weather, mixed periods, north offset and daylight-saving transition | Timezone, period, source and north convention shown; undefined or ambiguous time not silently converted. |
| Flood | Effective, pending, preliminary, absent coverage | Distinct labels and dates; absent coverage is not a negative hazard finding. |
| Components | Override text, update source, detach, undo, save/reopen | Only unoverridden values refresh; overrides remain; detached object is independent; edits retain layer ownership. |
| Layers | Hidden, frozen, locked, non-plot layers and different frame visibility | Drawing, editing and export follow the existing semantics; legend/credits reflect actual frame; no extra layer table. |
| Cache | Replace one successful tile with another while successful count is unchanged | Frame reflects the new tile; test may expose or disprove the suspected cache risk. |
| Legend | 0, 12 and 13+ classes | Every visible class is represented or explicit continuation/overflow warning appears; no silent truncation. |
| CORS | Approved and blocked sources on deployed origin; offline | Approved readback succeeds; blocked item and reason are surfaced; no unannounced omission. |
| Output | PDF/PNG/SVG/PPTX at target sizes; complex masks/blends, fonts and map imagery | Assert dimensions, order, clipping, visible attribution and per-format fidelity; document unsupported effects or intentional rasterization. |
| Regression | Saved V174/V175 boards, undo, print, existing documents and tests | Open unchanged; compare against frozen baseline, run repository checks, report actual commands/counts. |

These are proposed acceptance criteria, not executed tests. Set numeric image tolerances, source-coverage thresholds, supported reader/browser list and performance budgets from experiments before issuing work orders.

## 10. Dependencies, risks and remaining work

Recommended sequence: (1) pin main and inventory existing SA1–SA5 source records, project persistence and current test commands; (2) map each of the eight boards, six DA sheets and added archiMap features to concrete data and render dependencies; (3) test provider sample requests, deployed-origin CORS, usage terms, geographic coverage and observed failure paths; (4) research and independently verify allocation/statistical methods; (5) prototype component update/override, single-layer ownership and frozen provenance; (6) run real application export and reopen tests for each format and target; (7) resolve owner decisions; (8) write SPEC, runnable tests and narrowly scoped TASKS in repository order.

Research is not at the repository's completion gate: no independent check, no pinned commit, no service request/CORS measurements, no full data-source/license matrix, no current standards/adoption analysis per jurisdiction, no complete query log, and no app-level export/regression experiments. U claims are for planning only. Commercial rights, accessibility, regulated interpretations and output fidelity need subject-matter review. The original 20-hour task allowance is an unverified planning assumption, not a validated estimate for this expanded scope.

## 11. Owner decisions — recommendations, not recorded approvals

1. Preserve all three output families and allow shared figures between them; decide final report grouping and which pages are always emitted.
2. Prefer live editing plus explicit frozen issue/export; decide retention and reissue policy.
3. Prefer explicit component sync with per-field overrides and safe detach; decide cross-project sharing and versioning.
4. Choose between whole-slide raster and mixed editable/raster PPTX, or expose both honestly.
5. Decide whether partial data produces a marked report or blocks issuance, by feature and severity; never display unavailable values as zero.
6. Decide supported browsers/readers, minimum acceptable export resolution, font policy and tolerances only after measurements.

## 12. References, read 2026-11-13

1. Project task: https://app.notion.com/p/3fecbfcc3a38811e932ed521acc186e9 — scope and requested archiMap expansion, P.
2. V174 research: https://app.notion.com/p/412cbfcc3a388164935aca3df068e036 — later owner decisions on the single layer table, P.
3. Research protocol: https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-protocol.md — exit rule and research structure, P.
4. Work orders: https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/work-orders/README.md — research to spec/tests/tasks/gate, P.
5. DA reference: https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-da-report-reference.md — six observed sheets and 17 feature inventory, P for reference record.
6. archiMap report: https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-archimap-site-report.md — sampled frames, 20 pages, missing-source questions, P for reference record.
7. App sources: https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/sheets/live-sources.js ; https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/sheets/live-board.js ; https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/sheets/board-figures.js ; https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/sheets/board-map.js ; https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/sheets/present.js — code read as text, P.
8. Canva components: https://www.canva.com/help/create-manage-components/ — sync, overrides and limitations, P.
9. Microsoft PresentationML: https://learn.microsoft.com/en-us/office/open-xml/presentation/structure-of-a-presentationml-document — slide parts and editable object types, P.
10. MDN cross-origin images: https://developer.mozilla.org/en-US/docs/Web/HTML/CORS_enabled_image — canvas taint and SecurityError, secondary documentation of browser behavior.
11. Open-Meteo terms: https://open-meteo.com/en/terms — commercial restrictions and limits, P.
12. Overture attribution: https://docs.overturemaps.org/attribution/ — upstream attribution and license differences, P.
13. FEMA NFHL: https://www.fema.gov/flood-maps/national-flood-hazard-layer — effective, preliminary, pending and coverage, P.
14. ArcGIS map-series documentation: https://pro.arcgis.com/en/pro-app/latest/help/layouts/thematic-map-series-and-dynamic-elements.htm — dynamic text and map series, P.


---
Research evidence files: [`experiments/notion-v178/`](experiments/notion-v178/). Original scripts and results reflect only the experiments described above.
