# Algorithmic design: execution models and the identity of generated objects

One of five parallel research notes for `00-question.md`. Side: how algorithmic-design tools evaluate
(H1), how generated elements keep their identity across re-runs (H3), and text against node graphs (H5).
Started 2026-11-14, continued 2026-11-15. Levels: P = read in the source itself, S = dependable secondary,
U = unverified. STATUS: in progress; parts are filled as each source is read.

## 1. Summary of findings

(In progress; see part 2. Filled at the end.)

## 2. Findings by topic

### 2.1 How the tools evaluate

**Khepri (ADA group, Leitao). P, code read as text.** Repository `aptmcl/KhepriBase.jl`, commit
`a303d45c8b523e9cf452a70c81b4860a4e087d26` (2026-08-02), MIT. `aptmcl/Khepri.jl` (commit
`f76abd96c2eca6ff2f3a1d619203777ddc02575f`, 2026-08-01, MIT) is now a 4-line meta package re-exporting
`KhepriAutoCAD`; the engine is KhepriBase.

- A shape is a `Proxy` held in the program; each backend keeps a dictionary from proxy to the backend's
  native reference. `ref(b, s)` realizes the proxy in the backend the first time it is asked for and
  caches the reference (`src/Shapes.jl` lines 127 to 132). The same program is "portable" because the
  proxy is backend-neutral and each backend supplies `realize`.
- There is no incremental evaluation and no persistent identity of elements across runs. The re-run
  model is: `delete_all_shapes()` then run the whole program again. `b_delete_all_shapes` clears the
  trace table, deletes the backend's shapes and empties the proxy-to-reference dictionary
  (`src/Shapes.jl` lines 529 to 535). Every re-run makes new backend objects.
- "Traceability" is the link Khepri does keep: with `traceability(true)`, each created shape records
  the source locations (file, line) of the stack frames that created it, and a reverse table maps a
  source location to its shapes (`src/Shapes.jl` lines 378 to 472). It links program and model for
  understanding (select a shape, see the code; select a line, highlight the shapes). It is cleared on
  every `delete_all_shapes`, so it is not an identity that outlives a run.

Confidence: high for what the code does (read directly); the conclusion "no identity across runs" is
from the absence of any such mechanism in `Shapes.jl`, `Backend.jl` search to be completed.

## 3. H1, H3, H5

(In progress.)

## 4. Counter-evidence found

(In progress.)

## 5. What a plain-ES5 app should take from this

(In progress.)

## 6. Still open (U)

(In progress.)

## 7. Search log

| When | Where | Query or address | What came back | Kept or set aside |
|---|---|---|---|---|
| 2026-11-14 | GitHub (git clone, shallow) | `aptmcl/Khepri.jl` | Meta package only, 4 lines of source | Kept as pointer to KhepriBase |
| 2026-11-14 | GitHub (git clone, shallow) | `aptmcl/KhepriBase.jl` | 27,398 lines of Julia, MIT | Kept; `src/Shapes.jl` read |
| 2026-11-14 | raw.githubusercontent.com | salsa book `reference/algorithm.md`, `durability.md`; `milomg/reactively` README and `core.ts`; `tc39/proposal-signals` README; `preactjs/signals` core; `janestreet/incremental` `incremental_intf.ml`; `hypar-io/Elements` README | All 200 | Kept, to be read |
| 2026-11-14 | raw.githubusercontent.com | `janestreet/incremental` README.md | 404 | Set aside; the interface file carries the documentation |

## 8. References

(In progress; each entry: what it is, URL, what was read, date, level.)

- KhepriBase.jl, the core of Khepri. https://github.com/aptmcl/KhepriBase.jl , commit a303d45c. Read
  `src/Shapes.jl` lines 60 to 160, 370 to 475, 484 to 535. 2026-11-14. P.
- Khepri.jl. https://github.com/aptmcl/Khepri.jl , commit f76abd96. Read `src/Khepri.jl`, `Project.toml`,
  `README.md`. 2026-11-14. P.
