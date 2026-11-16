# Feature map

Start with the user's goal. The guide groups features in user language; the command reference is
generated from the app's command catalogue. Each new work order records the exact route and proof
for the behavior it changes, so this page stays an index rather than a second command list.

| User goal | Start here | Source area | Proof to follow |
|---|---|---|---|
| Find a tool or keyboard shortcut | [Getting started](../getting-started.html), then the in-app command search or Tools and shortcuts panel | `src/js/engine/commands/`, `src/js/engine/ui/` | The work order's **User path**, **Test**, and **Evidence** fields; browser suites under `tests/e2e/` for visible behavior |
| Draw or edit geometry | [Drawing guide](../drawing.html), command reference, Drafting ribbon | `src/js/engine/drawing/`, `src/js/engine/editing/` | `tests/unit/geometry.test.mjs` for shared geometry; the named phase suite for the changed tool |
| Model building elements | [Building model guide](../bim.html), Architecture ribbon, command search, Properties | `src/js/engine/bim/`, `src/js/engine/properties/` | Unit tests for the affected calculation and the named phase suite for user interaction |
| Work with a site or run an analysis | [Site guide](../site.html), [Analysis guide](../analysis.html), Analyze and Site workspaces | `src/js/engine/site/`, `src/js/engine/map/`, `src/js/engine/terrain/`, `src/js/engine/site-analysis/` | The task's independent calculation/reference test and its named browser suite when the interface changes |
| Make sheets or exchange project files | [Sheets and files guide](../sheets-files.html), Presentation and file commands | `src/js/engine/sheets/`, `src/js/engine/io/` | The relevant import/export unit test plus the task's browser evidence when the user flow changes |

The generated [command reference](../commands.html) is authoritative for exact command names,
aliases, and ribbon locations. Do not infer a feature's test from this broad map: use its work
order's named assertion and proof.
