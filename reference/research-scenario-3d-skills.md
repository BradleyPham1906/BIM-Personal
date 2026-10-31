# Research: Scenario 3D skills for World BIM Platform

Reviewed 2026-10-30. Research only: no application code, phase order, dates, estimates or completion claims changed.

## Scope, provenance and observed result

The request was to review the Scenario 3D skills repository, clone it, update relevant World BIM Platform tasks and document the findings in Notion and this repository.

Upstream: [scenario-labs/skills](https://github.com/scenario-labs/skills), pinned revision **5d68b48b70db3388e1ac3e064810d72d8fc3f7ac**. This is a broader agent-skills repository, not a drop-in BIM geometry engine. Its root license is MIT, copyright 2026 Scenario Inc.; preserve the copyright and permission notice if copying substantial portions.

**Clone result:** the local clone attempt failed because the shell could not resolve `github.com`. There is no successful local clone. Review continued through the GitHub connection's file-reading interface at the pinned revision. No installer, upstream script, build or test was executed, no skills were installed, no service was connected and no credits were spent. This is not a full code audit or runtime demonstration.

Notion summary: [Research: Scenario 3D skills for World BIM Platform](https://app.notion.com/p/63c598ecc6eb405d97b49d5cc183fea2). It is linked to the project and the two relevant planned tasks. GitHub main remains the source of truth; this branch is a proposal until merged.

## Evidence ledger

All upstream links below use the pinned revision. P means the named file was read directly; it establishes what upstream documents, not that its claimed service behavior was independently reproduced. Live catalog, pricing, model names and authoring-time measurements remain unverified here.

| Source actually read | Finding and evidence boundary | Level |
|---|---|---|
| [LICENSE](https://github.com/scenario-labs/skills/blob/5d68b48b70db3388e1ac3e064810d72d8fc3f7ac/LICENSE) | MIT applies to this repository's software and associated documentation; not blanket clearance for third-party services or assets. | P |
| [README.md](https://github.com/scenario-labs/skills/blob/5d68b48b70db3388e1ac3e064810d72d8fc3f7ac/README.md), [INSTALL.md](https://github.com/scenario-labs/skills/blob/5d68b48b70db3388e1ac3e064810d72d8fc3f7ac/INSTALL.md) | Broad Scenario-connected and desktop expert-tool skill groups. Read for repository scope and installation boundaries; installation not attempted. | P |
| [scenario-3d/SKILL.md](https://github.com/scenario-labs/skills/blob/5d68b48b70db3388e1ac3e064810d72d8fc3f7ac/skills/scenario-3d/SKILL.md) | Documents hosted mesh generation, schema discovery, quoting, remesh/retexture/rig stages and downloadable formats. Warns that scale, pivot, topology and material outcomes require checks. No service calls made. | P for documentation; U for live behavior |
| [scenario-blender/SKILL.md](https://github.com/scenario-labs/skills/blob/5d68b48b70db3388e1ac3e064810d72d8fc3f7ac/skills/scenario-blender/SKILL.md) | Describes a separate experimental GPL-3.0-or-later Blender extension, local loopback MCP, credentials and explicit spending/placement gates. Extension repository and licensing not independently audited. | P for description; U for extension verification |
| [scenario-blender-expert/SKILL.md](https://github.com/scenario-labs/skills/blob/5d68b48b70db3388e1ac3e064810d72d8fc3f7ac/skills/dcc/blender/scenario-blender-expert/SKILL.md) | Stage-by-stage numerical and visual checks; named audit/review helpers for normals, scale, floating parts, UVs and topology. Helper implementations and claimed tests not audited or run. | P for workflow; U for helper correctness |
| [scenario-blender-export/SKILL.md](https://github.com/scenario-labs/skills/blob/5d68b48b70db3388e1ac3e064810d72d8fc3f7ac/skills/dcc/blender/scenario-blender-export/SKILL.md) | Export is followed by re-import, dimensions/material comparison and required-extension inspection. The documented web preset uses meshopt/WebP; not a safe default for a loader without those decoders. | P for workflow; U for project compatibility |
| [scenario-blender-geometry-nodes/SKILL.md](https://github.com/scenario-labs/skills/blob/5d68b48b70db3388e1ac3e064810d72d8fc3f7ac/skills/dcc/blender/scenario-blender-geometry-nodes/SKILL.md) | Procedural inputs, fields/domains, evaluated-geometry measurement, coordinate-space and resolution probes. Blender-specific tooling; does not establish a browser NURBS/history integration. | P for scope; integration U |
| [scenario-3d-worlds/SKILL.md](https://github.com/scenario-labs/skills/blob/5d68b48b70db3388e1ac3e064810d72d8fc3f7ac/skills/scenario-3d-worlds/SKILL.md) | Documents Gaussian-splat worlds rather than ordinary editable polygon topology; mentions some mesh exports. Those exports do not establish BIM semantics or survey accuracy. | P for documented distinction; live exports U |

Project basis read on main at **4ca15f952045cea42541f969b4d8b40f2b4e5972**: CLAUDE.md, PIPELINE.md (current sequence and relevant rows), reference/research-protocol.md, reference/reuse-first-integration.md and reference/notion-sync.md. The existing Rhino and valdrada Notion summaries were also read. This review did not inspect application importer/renderer implementation; no claim of a verified module-level adapter is made.

## Applicability and task boundaries

### Later: glTF/GLB model import

Strongest candidate is **external asset preparation and acceptance testing**, not a new runtime service. Retain the existing in-house-first policy and valdrada attribution requirements. An eventual importer should test measured size, parent/node transforms, up-axis conversion, base pivot, normals, mesh/material counts, unsupported required extensions and save/reopen behavior. These are proposed checks, not implemented tests.

Start with an uncompressed, self-contained GLB fixture whose dimensions are independently known. Do not assume a generic 'web' preset is compatible with this zero-runtime-dependency app. Check supported extensions against the actual loader before adding compression; any decoder or runtime-contract exception needs evidence and owner approval. Keep authoritative dimensions separate from generated appearance. No third-party or generated assets were added by this review.

### V181-V187 Freeform (F1-F7)

The procedural-modeling and quality-review approach may inform discovery and test design. Geometry Nodes fields are not demonstrated substitutes for editable NURBS, a constraint solver, persistent sketch -> Pad -> Pocket history or deterministic dependency rebuild/recovery. Preserve the SolidCraft reuse-first workstream and its approval gate; do not rewrite it around Blender on the strength of a skill document.

PIPELINE main now names this group V181-V187 and records the 2026-10-24 numbering reconciliation. The older Notion note saying GitHub still uses V180-V186 is stale; correct that note only, without renumbering any task.

### No scope changes elsewhere

V169 Assets and V163 SketchUp import are completed and are not reopened. V172 remains the current pipeline phase; site-analysis work and later sequence are unaffected. Gaussian splats may be visualization research, but they are not automatically measured site context, editable BIM solids or a replacement for the LOD track. No new splat integration task or runtime renderer is proposed here.

## Alternatives and validation verdict

Criteria: offline/browser delivery, measured correctness, licensing clarity, reproducibility and maintenance burden. No numerical scoring or cost estimate is justified by this inspection.

| Alternative | Benefit | Limit / disposition |
|---|---|---|
| Keep current app; adopt asset-QA ideas as planning references | No new runtime dependency; fits existing import discovery | Recommended bounded next step, nonbinding pending Brad's review |
| Optional external Blender authoring/export | Potentially reusable preparation/audit tooling | Requires desktop setup, script/license inspection and an approved isolated experiment; no proof yet |
| Hosted Scenario generation or live Blender integration | Potential art-directed mesh workflow | Credentials, credits, upload rights, terms and network dependence; outside the current free/keyless/offline path without explicit exception |
| Direct browser reuse or port of Blender tooling | Could expose procedural workflows in-app | No verified isolatable browser module or compatibility evidence in this review; not recommended for implementation now |

**Verdict:** accept as a bounded research reference only. Restrict recommendations to discovery and asset-QA planning. Live service/model claims, helper correctness, performance and project compatibility remain U. No calculations needed independent recalculation; no runtime or regression tests ran because no application code changed. The full phase-research exit gate is not met for implementation.

Repository MIT licensing does not license every model, training input, generated output, service or the separate Blender extension. Verify each applicable license, provenance, commercial-use condition, privacy/upload requirement and attribution before copying code or distributing assets. Version-specific Blender behavior and upstream authoring-time prices/benchmarks must be rechecked in the actual environment, not copied as promises.

## Decision and next bounded checks

Decision owner: Brad Pham. AI-assisted review used GitHub file reads and Notion page reads on 2026-10-30. Human implementation approval: **pending**. The request authorizes research/documentation, not spending, installing a plugin or changing the delivery contract. Alternatives above remain proposals; no dissent or approval outcome is invented.

1. When shell network access is available, complete a pinned sibling clone outside tracked project files; record the actual path and `git rev-parse HEAD`. Never commit a full upstream tree by default.
2. Before any executable reuse, inspect the relevant export/audit scripts, their imports and notices, and the project's actual import/asset/render code. Record exact adapters and incompatibilities rather than assuming compatibility.
3. Present an isolated experiment and its commands/dependencies for approval. Suggested first case: one dimensioned static prop -> plain GLB -> actual project loader -> measure axes, size, pivot/materials -> save/reopen. Add malformed/unsupported-extension and budget-exceeding negative fixtures. Set project-specific tolerances and budgets with the owner; do not inherit upstream game-asset defaults blindly.
4. Only if the owner wants hosted generation: separately verify live schemas, terms, rights, upload privacy and exact quote; obtain approval before a paid job. Never put secrets or private models in this public repository.
5. Keep task statuses, estimates and dates unchanged until an approved scope/implementation change warrants updating them. Merge of this documentation does not ship a feature.
