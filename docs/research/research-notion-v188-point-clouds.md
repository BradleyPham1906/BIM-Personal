## V188 — Point-cloud ingestion and ground surface research

**Decision status:** Research synthesis; not approved for implementation. **Evidence date:** 2026-11-13. **Applicability:** World BIM Platform V188, a browser-based CAD/BIM application. This phase proposes LAS/LAZ/PLY ingestion, streamed point clouds, visual coloring and an optional classified-ground path to an existing terrain workflow. Existing app implementation and current provider endpoints were not independently verified in this synthesis. No live USGS request, browser cloud render, device performance test, or app terrain regression was performed.

### Questions and boundaries

The primary question is how to inspect useful subsets of large survey point clouds in the existing application while retaining survey provenance and avoiding a false claim that the visualization is a measured engineering surface. Local file inspection, cloud display, point classification and a separately confirmed conversion of ground points to terrain are distinct operations. LAS and LAZ are survey containers/compression; PLY is a general-purpose geometry format and should not be presumed to contain LAS classification, CRS, vertical datum or equivalent survey metadata. A missing field must be reported as absent, not fabricated. A point-cloud renderer does not by itself produce a survey-ready triangulated surface.

### Evidence and implications

1. [COPC 1.0](https://copc.io/) uses LAZ 1.4 with point-data record formats 6, 7 or 8, a mandatory information VLR and an octree hierarchy. A positive point count locates a data chunk; -1 points to a hierarchy page; zero means no points in that cell, not necessarily no descendant data. A viewport client needs header and hierarchy parsing, byte-range retrieval and LAZ chunk decoding, with explicit errors for unsupported record formats. For a cross-origin browser request, availability, CORS and byte-range behavior must be checked for the actual service, not inferred from the standard.
2. [Entwine Point Tile](https://entwine.io/entwine-point-tile.html) is a different layout: `ept.json`, hierarchy and data nodes. Its hierarchy is additive: child data augments ancestor data rather than replacing it. A renderer that substitutes children for a parent can silently discard points. Parse the dataset schema and its scale/offset; native `bounds` are already in the dataset SRS and must not be scaled twice. Do not call an EPT reader a COPC reader because both use octrees.
3. [laz-perf](https://github.com/hobu/laz-perf) supplies LAZ decoding, including browser-oriented WASM facilities, and declares Apache-2.0 licensing. That is evidence for evaluating a decoder, not proof that this application's dependency rules, delivery size, compatibility, or licensing review are satisfied. LAZ 1.4 is a lossless compression mechanism, not an assurance that coordinates or classifications are correct ([OGC announcement](https://www.ogc.org/announcement/ogc-announces-publication-of-the-laz-1-4-community-standard)).
4. Proposed USGS 3DEP availability and Philadelphia/PA coverage are **unverified for a specific dataset and date**. Locate an authoritative dataset manifest, acquisition date, CRS, vertical datum, classification, license and stable endpoint before using a location as an acceptance fixture. A successful metadata request is not a successful interactive rendering test.

### Architecture options

| Option | Benefit | Cost / boundary |
| --- | --- | --- |
| Local file only | Simplest offline path and explicit user choice | Cannot browse large remote archives; browser memory still needs a cap |
| COPC only | One range-addressed object, useful spatial hierarchy | Depends on compatible servers and LAZ decoder; does not cover EPT |
| EPT only | Established tiled source and additive hierarchy | Separate object fetches and schema; server and CORS still matter |
| Adapter boundary for local LAS/LAZ/PLY, COPC and EPT | Shared display and provenance model, separate parsers | More work; deliver in slices, do not pretend all formats are available before each parser passes |

**Recommendation:** Build a source adapter and a small local-file vertical slice, then add each remote format only after a repeatable test against a real endpoint. This is a proposed direction, not an owner decision. Keep a source record with URI or user-selected file identity, parser/format/version, metadata, horizontal/vertical CRS, acquisition date, transform, point budget and warnings. Store raw coordinates with their original scale and offset when possible. Convert from source CRS and vertical reference using an explicit, auditable operation. Missing CRS or datum should block any operation that would make the cloud appear spatially authoritative until the user selects or confirms it; the visualization may allow an obviously labeled unregistered preview.

### Pipeline and failure cases

1. Identify format from signature and structure, not only filename; validate record lengths, bounds and declared counts before allocating. Reject malformed or excessive allocations gracefully.
2. Parse coordinates and metadata in sufficient precision; compute the local project origin in double precision before float32 GPU upload. Preserve the transform for round-tripping.
3. Separate source loading from LOD selection and drawing. Schedule nodes using view and a configurable point budget; cap simultaneous requests and decoded memory. Abort obsolete requests on camera changes, deduplicate node requests and release GPU buffers on removal.
4. Render by RGB, classification or height only when the respective attribute is actually available. Explain missing values and return to a neutral default. Height coloring needs a declared reference and units.
5. The classified-ground action is a separate, previewable, non-destructive export: select a valid geographic area and classification, inspect gaps/outliers and density, apply a documented thinning policy, then invoke the existing surface path only after its data contract is verified. Do not silently fill gaps, claim an existing V108/V138 interface works, or turn unclassified returns into ground. Retain source references and report transform, class, filtering and user confirmation.
6. Network errors, unsupported byte ranges, incomplete nodes, missing CORS, unavailable codecs, points outside the chosen extent, unknown units and out-of-memory conditions each require a distinguishable failure or partial-load warning.

### Falsification and experiment

Hypothesis: casting large world coordinates directly to float32 can damage survey-scale detail; rebasing in double precision first can reduce this particular error. A single synthetic Python/NumPy test used eastings near 500,000 m and offsets 0, 0.01, 0.02, 0.05, 0.1 and 1 m. Direct float32 lost up to **0.0125 m**; subtracting the origin before the cast produced a maximum offset error of approximately **1.49 × 10⁻⁹ m** for these selected inputs. This is arithmetic evidence only, not a benchmark of the app, projection, survey accuracy or any already-quantized source. The attached script and JSON reproduce the inputs and result. A valid counterexample or regression should test different magnitudes, negative coordinates, datum transformations and any precision already lost upstream.

### Implementation-ready verification gates — proposed, not executed

- Open a small legal LAS, LAZ and PLY fixture separately; compare counts, bounds, supported dimensions and scaled coordinates against an independent trusted reader.
- Test COPC hierarchies with positive, empty and -1 entries, bounds/frustum selection, interrupted requests and range-unsupported responses; compare a complete small dataset with its source count.
- Test an EPT parent and child simultaneously to demonstrate additive coverage, with schema scales/offsets and SRS bounds checked independently.
- Exercise nonexistent attribute, unknown CRS, incompatible vertical datum, canceled download, offline and limited-memory cases; no silent placement or crash.
- Compare rebased GPU display against double-precision reference points, including a 500,000 m origin and sub-centimeter offsets. Establish a real application tolerance with the owner rather than adopting the synthetic result as one.
- Verify a classified ground export back to the actual surface input contract with a held-out sparse/occluded patch, and prove that source geometry and existing project layers remain unchanged.
- Measure initial display latency, p95 interaction time, peak CPU/GPU memory, node count and total bytes for named datasets/devices; set release budgets before asserting feasibility.

### Open decisions and review

Owner choices: priority of local formats versus remote adapters, initial provider and rights, allowed dependency size, unregistered-preview behavior, supported CRS transformations, point and memory budgets, and required surface approval. The task's 24-hour allowance is a planning placeholder, not a validated estimate. An independent research review, actual source-code interface audit, dataset access/rights review and full app tests remain required. Until those gates pass, this document is evidence for specification drafting, not an implementation-ready work order.


---
Research evidence files: [`experiments/notion-lod/`](experiments/notion-lod/). Original scripts and results reflect only the experiments described above.
