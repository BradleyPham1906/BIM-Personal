## V191 — Reviewed facade openings from rectified imagery

**Decision status:** Research synthesis only; not an approved work order. **Evidence date:** 2026-11-13. The proposed task draws or suggests windows and doors on a facade image, regularizes rows and columns and applies approved openings to the wall. This is downstream of V190 registration: an opening's apparent position is only as meaningful as the image-to-wall transform and its uncertainty. No SAM model, browser inference, actual geometry boolean, or app integration was tested. The task's 24-hour allowance is not validated.

### Problem and evidence

A visually plausible set of rectangles is not evidence of actual door/window geometry. Pictures can contain shutters, reflections, signage, recesses, occlusion, inaccessible lower floors or facades modified since capture. Windows may not be rectangular, identically spaced, coplanar with the wall, or visible from the chosen viewpoint. Source image provenance, date, rights, control/check-point error and wall association must travel forward from V190. If a metric facade registration is unverified, restrict the result to a visibly labeled visual proposal rather than automatically altering the model.

[Segment Anything](https://github.com/facebookresearch/segment-anything) is promptable segmentation research, with project code and model under Apache-2.0 according to its repository; dataset terms are separate. Its documented browser example exports a lightweight mask decoder to ONNX; the image encoder/backbone and preprocessing are still needed to produce the inputs. A mask is not automatically a verified semantic `window` or `door`, and the repository does not demonstrate that this app can run the complete selected model on target devices. Confirm the exact model weights, licenses, runtime, asset size, loading and performance before proposing a dependency. A manual path does not depend on a particular ML service and is therefore an essential baseline.

### Alternatives

| Candidate | Suitable use | Key limitation |
| --- | --- | --- |
| Manual rectangles/polygons | Controlled, reviewable initial workflow | Labor and perspective/registration error remain |
| Snap/regularize manually drawn openings | Repeated grids with clear user control | Can force a real irregular facade into a false grid |
| Prompted segmentation as an optional suggestion | Tracing difficult boundaries after runtime validation | Not semantic identification; quality, hardware and license need testing |
| Fully automatic detection and cutting | Potential batch acceleration | No source here establishes adequate precision, geometry validity or approval safety |

**Proposed initial slice:** manual draft in rectified image coordinates, explicit semantic category, optional preview-only row/column alignment, and user-confirmed geometry generation. Keep segmentation an optional research experiment, not a hard dependency or an automatic action.

### Proposed data model and geometry pipeline

1. A draft is associated with one facade/wall ID and one version of the image-to-wall mapping. Save polygon/rectangle coordinates, intended class, user/source, timestamp, source image, confidence/validation status and any regularization applied. The original draft and regularized proposal must be separately inspectable.
2. Transform image points into the wall's local metric coordinate system. Propagate or display upstream registration error; do not report more precision than justified. Refuse or visibly flag points outside the wall boundaries and geometry touching edges where a boolean may create ambiguous topology.
3. Offer alignment as a reversible proposal. Show the before/after deltas and allow individual exceptions; never assume all openings in a row share width, sill height or spacing. For repetitive detection, constrain only parameters that a user selected. Preserving an odd opening may be more correct than minimizing a grid error.
4. Before commit, validate width and height > 0, planarity, non-self-intersection, clear wall bounds, overlaps, minimum margins and compatibility with wall thickness, adjacency and existing openings. Exact tolerances are model- and kernel-specific and must be established empirically, not invented from a screenshot.
5. Preview cuts non-destructively, separately from image annotations. Commit selected proposals only after review; create native opening objects or use the existing wall-edit contract **only once that contract is audited**. Keep identifiers stable and retain dimensions, source and editable relationships. If the actual application has no safe native opening contract, stop at annotated proposals instead of writing fabricated BIM objects.
6. A changed image, registration transform, wall placement or geometry invalidates associated proposals; show staleness and require recheck. Undo/redo must restore geometry and linked metadata consistently. A failed boolean affects only the selected transaction; preserve the original wall.

### Hypotheses and falsification

H1: regularization helps repeated openings without erasing real deviations. **Untested**; use manually measured and intentionally irregular facades, report before/after center and size errors, and include an explicit opt-out. H2: masks can speed tracing. **Untested**; measure correction time and boundary accuracy against manual annotation on a representative rights-cleared set. H3: a proposed cut can be committed safely. **Untested** pending the real geometry kernel and wall contract. V190's single synthetic 3-pixel control perturbation led to up to 0.02871 m error in its nine withheld sample points; that is not a bound for V191 or a real-world tolerance. Its significance here is only that downstream annotations must not hide upstream uncertainty.

### Verification matrix — proposed, not performed

- Transform corners and irregular polygons through a known, invertible wall mapping and back; test outside-wall, mirrored axes, unit changes and degenerate transforms.
- Measure annotations against an independently surveyed, rights-cleared facade and compare manual versus optional assisted proposals, including occluded and reflective cases. Separate precision and recall from correct semantic category.
- A grid with a real nonstandard opening remains nonstandard when the user opts it out. Show original vs adjusted coordinates and permit exact undo.
- Check opening overlap, boundary crossing, tiny/zero dimensions, sloping/nonplanar geometry and wall thickness. No partial geometry mutation on failed commit.
- Verify object IDs, wall association, model and image lineage after save, reload, undo/redo and transform changes; stale dependencies must be visible.
- Test approval on multiple selections, skipped items and one failed item; confirm a proposed rectangle never becomes an opening until explicitly accepted.
- If optional SAM is evaluated, record exact model and runtime versions, full encoder+decoder path, download size, device/peak memory, latency, privacy/offline behavior, licensing and masks for at least diverse accepted fixtures. Distinguish measurement from a promotional model claim.

### Decisions and limitations

Owner must decide whether initial scope includes non-rectangular openings, grid fitting, optional ML, supported wall classes, intended engineering accuracy, acceptance workflow and data retention. Independent review, legal/license checks, real-world benchmark, wall-kernel audit, model runtime experiment and end-to-end regression remain open. The report is not evidence of a working feature and should not be used as a signed work order until those gates close.
