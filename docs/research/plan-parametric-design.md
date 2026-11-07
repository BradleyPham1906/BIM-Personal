# Parametric Design Foundation — SolidCraft-inspired modeling

Status: planned / preparing. Parent: Freeform F1-F7 (Notion V181-V187). Internal sequence, dates and effort: TBD.
Tracking issue: [#44](https://github.com/BradleyPham1906/BIM-Personal/issues/44).

## Intent

Add dependable parametric modeling to BIM-Personal, not full SolidCraft feature parity. A controlling sketch dimension or feature parameter should rebuild the intended dependent geometry predictably, persist through save/reopen, and ultimately remain connected to the BIM model.

## Placement and authorization

Owner decision: place Parametric Design Foundation within the Freeform F1-F7 group, under the Notion task V181-V187 Freeform (F1-F7), not as a separate later phase. Discovery determines the internal sequence and dependencies. The repository currently labels the same group V180-V186; reconcile that numbering mismatch separately without shifting adjacent phases. Dates and effort remain TBD. The existing Notion parent allowance predates this scope addition; decompose and re-estimate the expanded group before scheduling.

Notion parent: https://app.notion.com/p/3fecbfcc3a38811e8e25f016056867ea

Immediate execution scope is discovery and an architecture proposal. Implementation, new dependencies and build-contract changes require an explicit owner decision. Adding or merging this planning document is not approval to implement features, and must not close issue #44.

## 1. Preflight and code audit

- Verify the active branch, build hash, phase status and actual build/offline contract against the current repository.
- Trace sketch constraints and dimensions, Pad/Pocket, persistence, undo/redo, geometry dependencies, BIM type/derived-object behavior and test paths in code, not just documentation.
- Deliver a capability map: working, partial, absent and risky; list concrete files/functions and existing tests.
- Distinguish project/version history from feature history: the latter records how a shape is constructed and how edits propagate.

## 2. SolidCraft research and reuse decision

Follow `reference/reuse-first-integration.md`. First deliverable: a verified `reference/solidcraft-integration-map.md` with pinned source paths, documentation, reuse candidates, adapters, blockers and decisions. Keep source/docs in a local checkout, not in Notion. Prefer unchanged upstream modules and narrow adapters; do not rewrite merely because upstream is Rust. Inspect the existing browser/WASM route before recommending ports. Upstream execution requires explicit approval and isolation under the research protocol; after approval, demonstrate the pinned upstream unchanged before adapting it.

- Inspect relevant upstream source as text: solver, parameter/expression records, feature history, dependency/rebuild logic, persistence and tests.
- Record specific source paths and candidate algorithms; check the license at the source revision actually reviewed and preserve applicable notices for any reused code. Private personal use is the target, not a reason to skip license review.
- Compare extending existing JavaScript, porting a small isolated algorithm and proving a Rust/WASM boundary. SolidCraft's Rust application is not assumed directly compatible with the browser app.
- Evaluate each option against the verified single-file, ES5, zero-dependency and offline constraints; prefer the least-complex solution that passes acceptance tests. Do not introduce a dependency or build step without approval.
- Deliver a recommendation, risks, small proof-of-concept results where useful, effort estimate and unresolved owner decisions. Stop before feature implementation.

## 3. Approval gate

Ask the owner together:
1. Preserve the current delivery contract, or accept a Rust/WASM build if research proves a concrete need?
2. Limit v1 to the existing sketch/Pad/Pocket system, or expand solver capabilities where a demonstrated gap prevents the slice?
3. Confirm project-file feature storage and downstream failure behavior, with the last valid result preserved and stale geometry clearly identified.
4. Confirm the internal F1-F7 sequence, dependencies, effort and dates; reconcile the repository/Notion numbering mismatch without silently shifting adjacent work.

## 4. One vertical slice — after approval

- Editable closed sketch -> parameterized Pad -> Pocket, with dependent geometry updating after controlling dimension/depth edits.
- Stable IDs, persistent feature/parameter records, explicit inputs and dependencies, deterministic recompute order and named failure states.
- Reuse existing constraint/geometry behavior wherever the audit proves it sound. Add only the solver behavior needed for this slice.
- Integrate feature/parameter editing with existing Properties and command patterns. Do not confuse the feature timeline with project commits.
- Detect invalid inputs, missing references, cycles and failed rebuilds; identify the responsible feature and preserve a safe, understandable last-valid model state. Never silently detach or substitute geometry.
- Extend to broader BIM-derived geometry only after the core slice is proven.

## 5. Verification and documentation

- Independently check expected geometry, not just screenshots or implementation-derived answers.
- Cover dimension/depth changes, dependency propagation, save/reopen, old-project compatibility, exact undo/redo, invalid inputs and failure recovery.
- Test offline and device usability across phone, tablet and desktop.
- Falsify the new browser suite against deliberate breaks in evaluation, recompute, persistence, dependency propagation and error handling; run the full regression suite.
- Update user guide, command catalogue and phase log only for behavior that has shipped; update pipeline/build records according to repository rules.

## Acceptance example

Create a 4 m x 3 m rectangle and Pad it 0.3 m. Add an editable Pocket with explicit dimensions, depth and attachment/reference behavior. Change the rectangle width to 5 m; the pad and pocket must rebuild according to those defined dependencies. Save/reopen and undo/redo must preserve feature inputs, ordering, relationships and expected results. An invalid edit must name the failure without silently corrupting the project or discarding the last valid result.

## Out of scope for v1

Full SolidCraft parity, advanced fillets, assemblies, a replacement sketch solver without demonstrated need, and broad BIM propagation before the basic workflow is dependable.

## Sources to audit

- SolidCraft source: https://github.com/tangency-labs/solidcraft
- SolidCraft docs: https://docs.solidcraft.io/
- Parameters: https://docs.solidcraft.io/guide/parameters.html
- Features: https://docs.solidcraft.io/guide/features.html
- Sketching: https://docs.solidcraft.io/guide/sketching.html
- Current app drawing guide: https://bradleypham1906.github.io/BIM-Personal/docs/drawing.html
- Current app BIM guide: https://bradleypham1906.github.io/BIM-Personal/docs/bim.html

These are research inputs, not a claim that the source audit or implementation has already been completed.
