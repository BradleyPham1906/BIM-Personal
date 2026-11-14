# V217 spec: Hub H5, the server's access rules

Notion: Later: Hub H5: the server. Research: `docs/research/research-notion-hub-h5-server.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- The rules are written and tested in the app first, the same code a server later runs: roles viewer, commenter, editor, owner; a project role raised by an element grant and removed by an element denial; unknown actions refused.
- A private check (clashes, codes) returns only the fields the owner allows out, never the geometry: the research's threat model; nothing claimed as zero-knowledge in the viewer.
- Every decision is an audit entry. Which host runs the server is the owner's choice when it is set up (WO-06).

## 2. What it does for the user

Sharing shows each person's role on the project and on chosen elements; a private check returns pass or fail and counts, not the model; the access log lists every decision.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/history/hub-access.js` | new, after `js/engine/history/hub-files.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v217/v217.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/history/hub-access.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimSrvRole(acl, user, elId)`**: with BIM_SRV_RANK {viewer 1, commenter 2, editor 3, owner 4} and BIM_SRV_NEED {read 1, comment 2, edit 3, share 4, delete 4} just above it: among the user's entries that are project-wide (no element) or for this element, a denial for this element gives null at once; else the highest-ranked role, or null.
- **WO-02 `bimSrvCan(acl, user, elId, action)`**: false for an action not in BIM_SRV_NEED; else whether the role's rank reaches the action's need.
- **WO-03 `bimSrvRedact(result, fields)`**: only the listed fields the result has.
- **WO-04 `bimSrvAudit(user, action, elId, allowed, when)`**: {at: when, user, action, element (all as strings), allowed (as a boolean)}.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** the server; **WO-06** the records.

## 7. Not in this phase

Payments (after the server exists); end-to-end encryption; a server before the owner chooses its host.
