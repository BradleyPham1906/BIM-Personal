# LOD-F: LOD3 openings on rectified facades work orders (outline)

Spec: `SPEC.md` in this folder (an outline). No `[Cline]` task yet: Claude's WO-01 turns the first slice into Cline-ready orders (the file's header in the build order, the tests checked against a reference, one order per function).

---

## [ ] WO-01 [Claude] The first slice's work orders

Claude's: write `src/js/engine/bim/facade-openings.js`'s header, add it to `src/index.html`, write the tests (Rectangles placed in known rows and columns with jitter: regularised back within tol; overlaps found) against an uncommitted reference, and the Cline orders, one per function of SPEC part 3.

---

## [ ] WO-02 [Claude] The phase after its first slice

Claude's: wire the slice into the app (its interface, saving, undo), the one browser check of the new interface, then the next slice's orders.
