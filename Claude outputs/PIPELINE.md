# canvas_v10 — the pipeline

**Read this first in a new session.** One page. The detail lives in the docs listed at the bottom.

    canvas_v10.html   1,927,227 bytes
    sha256            c0a7ddade2dc0a764f3a00b248614669c7fc61b516b3dcb60cef163158d4cff9
    markers           __acad3dV60 ... __acad3dV86
    tests             40 suites, 996 checks, 0 failures

Start every session by verifying that hash and taking a backup. Never output the whole file; patch
with anchored Python scripts that assert exact match counts.

---

## NOW — Track A, finish the drafting foundation

All five target disciplines stand on this. Ordered by value per hour.

| # | Phase | Scope | Notes |
|---|---|---|---|
| 87 | Modify toolbox | FILLET CHAMFER EXTEND SCALE STRETCH BREAK BREAKATPOINT JOIN EXPLODE ARRAY ARRAYRECT ARRAYPATH ALIGN LENGTHEN PEDIT MATCHPROP PROPERTIES OOPS OVERKILL | Biggest gap. Geometry ops on data the app already holds. **Start here.** |
| 88 | Draw set | ARC ELLIPSE POLYGON SPLINE POINT XLINE RAY 3DPOLY DIVIDE MEASURE BOUNDARY DONUT WIPEOUT | **Decide arc storage before writing ARC** — bulge factor per vertex vs segment-type array. Four tools depend on it. |
| 89 | Dimension set | DIMORDINATE DIMBASELINE DIMCONTINUE DIMALIGNED DIMARC DIMSTYLE QDIM DIMEDIT DIMTEDIT | DIMORDINATE is station-and-offset — civil and bridge drawings can't be issued without it. |
| 90 | Hatch | HATCH HATCHEDIT GRADIENT | Phase 53 pattern library already built and unconnected. **Depends on Phase 88's BOUNDARY.** |
| 91 | Blocks and data | ATTDEF ATTEDIT BEDIT WBLOCK DATAEXTRACTION TABLESTYLE TABLEDIT TABLEEXPORT | First phase that's about the disciplines, not drafting. |
| 92 | Sheets and plotting | LAYOUT MVIEW MSPACE PSPACE PAGESETUP PLOT PUBLISH EXPORTPDF | Depends on the V84 sheet-as-a-view work. |

**Small, unscheduled, do when convenient:** make F8 ortho constrain the *rubber band*, not just the
snap. Roughly an hour, and it finishes the V86 command line.

---

## NEXT — Track B, the object model

The command audit's central finding: implementing all 902 AutoCAD commands would still leave MEP,
HVAC and civil alignment work **entirely unbuilt**. The object model is where the discipline value
actually is.

1. **Structural object model** — loads, supports, load combinations, results. `TYPE_CATS` still
   covers wall/floor/ceiling/column only.
2. **Section-profile library** — steel sections, reinforcement, bolt patterns.
3. **Alignment / profile objects** — horizontal alignment, vertical profile, station-offset.
4. **Connector-based MEP objects** — ducts and pipe as connected runs with size and flow.

**Items 1 and 2 are the common prerequisite for three separate things**: the ARCH5 port, the
PennDOT input writer, and any real structural work. Build them once, three things unblock.

A linear-elastic 3D frame solver (the STAAD-equivalent) IS item 1 — direct stiffness method,
textbook math, bounded scope, validates against closed-form solutions. Most tractable major piece
on this whole list.

---

## ALSO READY — DXF, no dependencies

**DXF export then import.** R12 ASCII. Published format; both AutoCAD and MicroStation read it.
Days, not weeks, and it stops work being trapped inside the app. Can slot in anywhere.

---

## PARKED — PennDOT bridge engineering (Track C)

**Deliberately later.** Scoped and documented so it can start cold whenever wanted.

- **Blocked on nothing technical.** The input formats are published: PennDOT's official manuals are
  free and public at `penndot.engrprograms.com`, and Chapters 5/6 document the command records
  field by field. 44 commands for PSLRFD, 57 for STLRFD, **23 shared between them**.
- **What's needed to start:** run `reference/penndot/fetch_manuals.sh` to pull the PDFs, then
  extract the field definitions. Also worth grabbing one real `.dat` input file plus its output
  from a past job — that's the validation fixture and settles the format question from the artifact
  rather than the manual.
- **Recorded trap:** `DPL` means "Drape Point Location" in PSLRFD and "Design Plate Location" in
  STLRFD. A code table keyed only on the three letters emits a valid-looking, wrong file.
- **Build order when it starts:** output parser first (needs only a sample output file, no format
  docs, delivers automated rating reports immediately) → generic command emitter → shared core →
  per-program member modules.
- **Depends on Track B items 1 and 2** for the loads and sections it has to write.

**Also parked:** the ARCH5 port. `ENGPROG/in-house/arch5.for`, 1,424 lines of FORTRAN, the firm's
own RC arch rib load-rating program, rights confirmed. `ARCH527.OUT` is a worked example with
published answers (inventory RF 2.52, operating RF 4.20, 207.4 / 346.3 tons) — the port isn't done
until the JS reproduces them. Same Track B dependency.

**Out of scope permanently:** reimplementing or reverse-engineering the licensed programs — PennDOT
suite, STAAD, MicroStation, CSiBridge, AASHTOWare. Confirmed there's no source to copy in any case;
they ship as compiled binaries.

---

## Where the detail lives

| Doc | What's in it |
|---|---|
| `claude/canvas_v10_STATUS.md` | Full phase history V60-V86, every bug and its lesson, per-phase scope. Large — search it, don't read it start to finish. |
| `claude/roadmap-autocad-command-coverage.md` | All 902 AutoCAD commands scored against the five disciplines, with coverage counts. |
| `claude/penndot-official-documentation.md` | PennDOT program inventory, licensing, verified manual URLs. |
| `claude/penndot-input-spec.md` | The input command inventory for PSLRFD and STLRFD, shared-core analysis, model-data mapping. |
| `reference/penndot/fetch_manuals.sh` | Pulls the public manuals down. Run on any machine with normal internet. |

## Standing rules

- Every phase ships with a browser test suite, **falsified against a deliberately broken build**
  carrying the phase marker before it's trusted.
- Assert on the **model**, not on appearance. The V86 lesson: a palette that looked perfect and did
  nothing passed every appearance check for as long as it existed.
- **Claim a control only after driving it** (the V85 lesson — a whitelist entry taken on faith is
  worse than no whitelist).
- Never hand-list what can be derived (V74; applied again in V86 to prompt strings).
- Full regression before shipping; commit to the Mac and verify by hash.
