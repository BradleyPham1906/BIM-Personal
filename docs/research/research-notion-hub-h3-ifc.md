# Hub H3 — IFC exchange and identity research

## 1. Abstract

H3 asks how the platform should exchange IFC 4/4.3 and keep identity for Hub diffs without pretending that a visual mesh import is a semantic round trip. Recommendation: build on the existing V196 cc-ifc import, first make loss and provenance observable, then implement a narrowly specified IFC exchange with round-trip fixtures. Keep the original as an immutable source alongside a typed exchange graph if semantic edit/re-export is required. Do not replace the engine merely because the old task says web-ifc. The import exists; full coverage, export, interoperability, stable identity across revisions and this research's independent check have not been demonstrated. This is an engineering recommendation, not an approved scope or certification.

## 2. Question and hypotheses

Question: Which data, geometry, coordinate, identity and relationships must survive source → app → IFC → independent application for an agreed exchange scenario, and what is already implemented?

- H1: The historical task requires a new web-ifc importer. **Rejected** by current code: V196 uses cc-ifc + optional Manifold; replacing it requires a separately evidenced decision.
- H2: An imported element's source GlobalId is the app object's own permanent identity. **Rejected for the inspected creation path:** it saves `bim.guid` separately from a freshly generated `a3d-...` id. Reimport matching is not established.
- H3: Properties retained for display are lossless typed IFC values. **Rejected for this path:** values are strings, formatted and bounded; sets, values and text have caps. The isolated formatting experiment demonstrates collapse of two different values; it does not measure a project-level round trip.
- H4: Geometry import proves semantic exchange is correct. **Rejected as a test criterion:** shape alone cannot verify units, identity, placement or relationships.
- H5: An exported IFC is exchange-ready if schema validation passes. **Rejected as a sufficiency claim:** schema validity and preservation of a particular project's semantics are separate checks.
- H6: Current exporter produces full round trips. **U:** exact writer and end-to-end behavior were not located or exercised in this session; a directory listing cannot establish repository-wide absence.

## 3. Method and search log

2026-11-13: read the project task and `io/ifc-full.js`, the previous `research-ifc-engine.md`, buildingSMART 4.3 identity and object-placement references and Validation Service user guide. Searches: `buildingSMART IFC GlobalId object placement units`; `site:github.com/BradleyPham1906/BIM-Personal IFC export IfcWall writer`; `site:github.com/BradleyPham1906/BIM-Personal "exportIFC"`. The latter returned no useful result, not proof no writer exists. Inspected the `src/js/engine/io` directory and `export-mappings.js`; that file implements DXF/SVG, not an IFC writer in the inspected content. Read the prior research's engine table rather than presenting it as a new test.

One offline Node experiment reproduces the displayed-property formatting rule; script and raw JSON are attached. Scope is intentionally narrow: no original IFC, app, independent viewer, browser timing or validation service was run. Independent second-reader check: **not performed**. Protocol exit rule is therefore not met, regardless of the detail below. Levels: P = direct source/code, U = unresolved or proposed; confidence concerns the stated limited claim, not the whole system.

## 4. Findings

### Identity and exchange semantics

[P/high] buildingSMART says IFC-GUID is persistent; STEP instance numbers are file-specific and do not guarantee stability between reserializations. `#123`, generated app ID and IFC GlobalId must not be used interchangeably. [Identity concept](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Attributes/Software_Identity/content.html). A proposed key is `(source namespace, IFC GlobalId)` with import instance, file version/hash and app ID as separate attributes. A duplicated GlobalId within a source should be reported and quarantined, not silently merged. Identical GlobalIds across intentionally related revisions are potential correspondence, not proof that geometry or metadata are unchanged.

[P/high] IFC placement can be absolute, relative, grid-based or linear; a product's representation needs an object placement. An import that moves coordinates to a local origin must preserve the transform, units and source georeferencing if restoration is required; visually fitting the camera is not enough. [IfcObjectPlacement](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcObjectPlacement.htm). [U] Actual source CRS restoration and the association between coordination matrix and saved project state remain to be tested.

[P/high] The Validation Service checks STEP syntax, schema version and EXPRESS schema rules, and normative rules; it accepts non-zipped STEP IFC up to 256 MB. It reports non-normative practices as warnings. A valid output can still omit information demanded by the project's exchange agreement. [Service guide](https://buildingsmart.github.io/validate/user/index.html). Do not upload confidential models to a third party without permission; use synthetic/public fixtures or a locally controlled validator.

### Import fidelity and evidence disagreement

[P/high] In the inspected V196 path, `COORDINATE_TO_ORIGIN:true`; one locked solid is assembled per drawn element; GlobalId, type, storey and bounded selected property sets are stored. It chooses one dominant opaque color or fallback dominant color and aggregates opacity. It caps at 1,500,000 triangles, 40 sets, 80 rows per set, and 200 text characters. A property-set retrieval rejection returns an empty list. Empty can therefore mean retrieval failure, not only no properties. Openings need the optional geometry runtime; fallback reader is walls/slabs if the runtime fails. [Importer](https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/io/ifc-full.js).

[P/medium] Prior V196 experiment reports 13 files but its general statement of equal element counts conflicts with its own 3,569 versus 3,504 row; the note attributes the 65 difference to zero-area objects after openings. A curved-B-rep example also had a large triangle/time difference. This is prior reported evidence, not an independently repeated benchmark or a semantic comparison. It motivates targeted fixtures instead of claiming all files equal. [Prior engine research](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-ifc-engine.md).

[P/high] Example 205-character display text is shortened to 200, and two distinct numeric values can display identically under the formatting branch. The reproduced function does not establish whether some other subsystem preserves the original value. Never infer full property preservation from a display screenshot.

## 5. Alternatives

Criteria: semantic fidelity, use of existing code, implementation complexity and safe failure.

| Option | Strength | Principal cost or risk |
| --- | --- | --- |
| A. Current mesh-reference import only | Reuses V196; honest view/reference | Not a semantic editing or round-trip guarantee |
| B. Existing importer plus immutable source, provenance and typed exchange graph | Can preserve non-geometric data and distinguish unknown from absent; fits owner-selected engine | Requires source lifecycle, storage, mapping and explicit conflicts |
| C. Replace importer with another IFC engine | Might close measured defects | Duplicates integration; no demonstrated coverage or licensing advantage on this evidence |
| D. Export only app-native objects to a constrained IFC model view | Smaller, testable first exchange | Not lossless for arbitrary imported models; must report omitted entities |

Recommend B for preservation architecture and D for a separately scoped first export, while retaining A as an explicitly limited reference mode. Change recommendation if a fixture comparison shows another engine meets agreed needs better after license, maintenance, size and browser tests.

## 6. Experiment

Run `node experiment.js`; `results.json` records one run. Reproduces the code's six-significant-digit formatting branch, not the app. `0.123456789 → 0.123457`; `1234567.89 → 1234570`; `100.000041` and `100.000049` both become `100`; `0.0000123456789` is not rounded by this branch. 205 characters become 200. This falsifies lossless representation through that display transformation, not necessarily preservation elsewhere. The source can be reviewed against the named function before reuse.

## 7. Exchange and falsification matrix

| Fixture or boundary | Check / proposed acceptance, subject to agreed exchange |
| --- | --- |
| Wall with opening + door, Manifold on/off | Compare hole topology and report fallback; no silent solid wall |
| 1,499,999 / 1,500,000 / over-cap triangles | Expected kept/skipped count per complete element; loss log and no false full-success label |
| 40/41 sets; 80/81 rows; 200/201 chars | Verify warnings and original typed data; distinguish omitted from empty |
| Missing/duplicate GlobalId; same GUID across source revisions | Reject or quarantine duplicates within a source; trace revisions without merging unrelated sources |
| 2x3, 4 and 4.3 fixtures | Exact declared schema and unsupported entities; test supported subset rather than generalize |
| mm/ft/metre plus nested, mapped and georeferenced placements | Check measured world coordinates, handedness, origin transform and units on return |
| Spatial containment and non-geometric objects | Compare project/site/building/storey, relations, types and intentionally invisible data |
| Material/style and multiple colors | Record selected-color simplification vs full source representation |
| Psets/QTOs, numeric units, enums, relations | Compare types and values, not just formatted strings |
| Export then buildingSMART validation and independent reimport | Compare source/app/export semantic manifest plus geometry tolerances; schema validation alone is insufficient |

Tolerances, supported entity list, sample licensing and expected losses must be fixed in each fixture's manifest **before** the implementation test; results should retain input checksum, software revision and raw diffs.

## 8. Existing app and suggested work-order decomposition

1. Pin and inspect actual IFC exporter/dispatch path and release commit; document generated schema/entities and map it to the existing reader. Unknown today.
2. Add interchange inventory and loss report to existing importer, including fallback and per-field retrieval failure; retain immutable source and coordination transform subject to storage/privacy choice.
3. Define typed semantic manifest and mapping for the agreed exchange scenario, not an unbounded promise of all IFC entities.
4. Implement identity resolution and collision reporting; validate against revision and multi-source fixtures before H1 diff.
5. Implement constrained writer with an explicit unsupported-elements policy, escape/units/placement correctness and stable GUID strategy; do not reuse IFC IDs for unrelated new objects.
6. Automate real browser round trips, independently validate and compare in another viewer; verify undo/save/reopen and licensed fixtures.

The `io` directory lists `ifc-full.js` and `import-ifc.js`; `export-mappings.js` inspected is DXF/SVG. This is not a complete repository-wide exporter audit. Cite actual line numbers in the eventual pinned-commit work order: the web extraction provided snippets, not reliable source line spans.

## 9. Risks and threats to validity

Mutable main branch, no pinned revision in this new inspection; no app execution; display-only experiment; incomplete exporter discovery; no representative public fixture corpus; no independent validator or second reader; engine benchmark came from prior authors; legal and licensing conclusions not independently reviewed. Very large models and off-origin geometry can exhaust memory; silent property failures and coordinate loss can lead to wrong downstream quantities or location. No cost or timeline is inferred from the task's old 40-hour rough estimate.

## 10. Open / completion gates

Pin exact code revision; locate writer and existing tests; establish permitted source corpus and IFC schema/model-view versions; run browser import and writer, reopen, independent viewer and validator; inspect source-side loss on relations/units and source transform; quantify time/memory on target devices; complete independent second-reader check. Until those gates pass, **full H3 research and work-order readiness are not certified**. This report was initially drafted while GitHub was unavailable; the open validation gates remain unchanged.

## 11. Owner decisions, not yet made

Proposed choices: (1) reference-only or semantic authoring; (2) source retention and size/privacy limits; (3) schema/model view and first entity subset; (4) handling duplicate identity and collisions across linked models; (5) coordinate/CRS and tolerance; (6) public vs local validation and unsupported-content behavior. None is represented as decided. Decisions can be bundled after the evidence and end-to-end tests are ready.

## 12. References

Accessed 2026-11-13. [IFC 4.3 software identity](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Attributes/Software_Identity/content.html), P; [IFC placement](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcObjectPlacement.htm), P; [buildingSMART validation guide](https://buildingsmart.github.io/validate/user/index.html), P; [app importer](https://github.com/BradleyPham1906/BIM-Personal/blob/main/src/js/engine/io/ifc-full.js), P; [app engine study](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-ifc-engine.md), P for what it reports; [research protocol](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-protocol.md), P; [I/O directory](https://github.com/BradleyPham1906/BIM-Personal/tree/main/src/js/engine/io), P for listed entries.


---
Research evidence files: [`experiments/notion-h3-ifc/`](experiments/notion-h3-ifc/). Original scripts and results reflect only the experiments described above.
