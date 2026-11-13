## V192 — Gaussian splats as a visual context layer

**Decision status:** Research synthesis; not an approved implementation. **Evidence date:** 2026-11-13. The proposed phase adds `.splat` imagery as a backdrop for a BIM environment. A Gaussian splat is a learned visual representation, not a measured semantic building model, watertight surface, authoritative surface for quantity takeoff, or reliable collision mesh. No viewer has been integrated or profiled in the app; the task's 12-hour allowance remains unvalidated.

### What the sources actually show

The [original 3D Gaussian Splatting research project](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) describes anisotropic Gaussians and visibility-aware rendering for scene synthesis. A paper's reported rendering speed and reconstruction quality apply to its experiment, hardware, datasets and pipeline; they do not establish this app's browser performance or geometric accuracy. Appearance, pose, occlusion, lighting and missing training views can create visual artifacts.

The [antimatter15/splat repository](https://github.com/antimatter15/splat) presents a minimal viewer and declares MIT licensing. Its README describes simplifications and says WebGL1, but the inspected unpinned [`main.js`](https://github.com/antimatter15/splat/blob/main/main.js) requests `webgl2` and uses a `#version 300 es` shader. This is a source conflict: the inspected code is evidence about that version only, not every version or device. Pin and audit a chosen commit and test the actual browser/context. Code's row length is `3*4 + 3*4 + 4 + 4 = 32` bytes for position, scale, color and encoded orientation in that viewer's format. At that layout, one million rows require **32,000,000 bytes** of raw row storage (~30.52 MiB); decoded buffers, transferred copies, sort indices, GPU allocations, texture padding and source/model data add overhead. That arithmetic is not a runtime benchmark. `.splat` is not established by these sources as a universal interchange standard; reject incompatible variants instead of guessing.

### Options and recommendation

| Approach | Advantage | Boundary |
| --- | --- | --- |
| Visual-only isolated layer | Clear purpose and potentially reusable context | Needs registration, rendering/compositing and memory measurements |
| Convert splat to a BIM mesh automatically | Appears to unify the model | Source does not support trustworthy semantic or metric conversion; not recommended without separate reconstruction research |
| Link to an external viewer | Reduces integration surface | Loses integrated camera/layer workflow; provider and privacy obligations apply |
| Port or wrap a minimal open-source viewer | Practical starting reference | License, dependencies, graphics context, sorting and integration require code-level audit |

**Proposed approach:** isolated visual-only layer, explicit user-supplied transform, point/splat budget, per-layer show/hide and opacity if demonstrated, plus an obvious indication that the backdrop is not selectable or measurable engineering geometry. Align with the existing shared layer system; do not create a second competing project layer tree. Selection or picking may identify the backdrop layer but must not fabricate semantic BIM objects.

### Integration contract and algorithm concerns

- Ingest the selected format only after verifying magic/version or, for a raw headerless layout, through an explicit user-selected format and strict byte-length validation. Validate all decoded values, file size, finite positions, scale and quaternion representation before GPU allocation. Do not assume every raw file is compatible solely due to the extension.
- Record file hash, source/creator and license, coordinate system if supplied, model transform, unit scaling, creation date, renderer/version, controls and a visual-only status. A raw format may contain no georeferencing; never claim alignment based on its mere appearance.
- Register using named landmarks and a reversible transform in project coordinates. Display residuals and independent check-points if measurable, noting any scale ambiguity; otherwise label alignment visual-only. Avoid float32 world-coordinate loss by carrying a double-precision project origin and converting to local render positions, but verify the app's actual render architecture first.
- Gaussian transparency and sort order can conflict with depth-tested solid geometry. A renderer must define behavior with opaque geometry, transparent layers, clipping, camera movement and screenshots; incorrect compositing can put an apparent facade in front of a real wall. Do not claim physically correct depth solely because it looks acceptable from one viewpoint.
- The inspected viewer uses a worker and depth sorting. Sorting cost, transferred arrays, copy behavior and stale frames require actual performance measurement. A zero or nearly zero depth range deserves a degeneracy test; source inspection alone does not establish a user-visible bug. Define cancellation, disposal and context-loss recovery.
- Integrate with the existing render lifecycle without creating an unsupported second WebGL context or resetting shared GL state. Test view navigation, resize, project save/reload, layer visibility, resource cleanup and context restoration. A separate canvas overlay may be simpler to prototype but must prove camera, depth and transparency alignment; it is an alternative, not a validated solution.

### Hypotheses and discriminating tests

H1: 32-byte rows can be parsed accurately for the specific audited viewer layout. **Source inspection and arithmetic only; no independent parser comparison.** Construct small fixtures with known positions, scales and colors, then compare output byte-for-byte with a pinned reference. H2: a million-splat scene fits target devices. **Unknown** until measured; raw size alone excludes working memory and GPU overhead. H3: a backdrop can share camera/depth correctly with BIM solids. **Unknown** until integrated with actual rendering. H4: a splat can be converted directly into trustworthy BIM elements. **Unsupported and excluded** from this phase. H5: a user can place an unreferenced splat visually. **Plausible, not tested**; visual registration must not be represented as survey registration.

### Acceptance matrix — proposed, not executed

1. Audit the pinned format and license; exercise valid small fixture, empty file, truncated record, oversized file, invalid values and unsupported variant. No unbounded allocation or crash.
2. Check registration and scale with known control landmarks, including a nonzero world origin and independent check-points; label unverified coordinate systems and prohibit misleading measurement.
3. Exercise orbit, pan, zoom, resize, orthographic/perspective modes if supported, occlusion with BIM geometry, transparent objects and clipping. Capture reproducible screenshots from multiple views, not just a hero shot.
4. Measure load duration, time-to-first-frame, p50/p95 frame time, sort time, total raw/decoded/GPU memory and peak memory, across small, medium and target-size datasets on named browsers/devices. Set the owner-approved budget before a pass/fail claim.
5. Save/reload, hide/show, remove, cancel loading and repeatedly open/close a scene; check worker/GPU disposal and graphics context loss. No modification of existing BIM geometry or the shared layer semantics.
6. Verify project export and sharing behavior does not redistribute third-party source assets contrary to their terms; enforce the selected license/rights policy.

### Owner choices and unresolved gates

Target browsers and devices, input format/version, maximum scene size, local vs remote storage, rights, permitted placement methods, whether layer opacity/clipping is required, and whether visual-only context can appear in exports. Independent review, source-code integration audit, pinned dependency/license review, real device tests and actual rendering validation remain outstanding. This report is not proof of a deployable viewer or a completed engineering work order.
