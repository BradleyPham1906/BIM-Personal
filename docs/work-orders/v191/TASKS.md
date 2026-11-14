# LOD-D: LOD1.3 and LOD2.2 roofs from LiDAR work orders (outline)

Spec: `SPEC.md` in this folder (an outline). No `[Cline]` task yet: Claude's WO-01 turns the first slice into Cline-ready orders (the file's header in the build order, the tests checked against a reference, one order per function).

---

## [ ] WO-01 [Claude] The first slice's work orders

Claude's: write `src/js/engine/map/roofs-lidar.js`'s header, add it to `src/index.html`, write the tests (Synthetic gabled and hipped roofs sampled with known noise: planes recovered within 1e-6 with no noise, RMSE equal to the added noise within 5%) against an uncommitted reference, and the Cline orders, one per function of SPEC part 3.

---

## [ ] WO-02 [Claude] The phase after its first slice

Claude's: wire the slice into the app (its interface, saving, undo), the one browser check of the new interface, then the next slice's orders.
