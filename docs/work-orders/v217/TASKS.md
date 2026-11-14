# V217 work orders: Hub H5, the server's access rules

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/history/hub-access.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v217/v217.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v217/v217.test.mjs
    node --check src/js/engine/history/hub-access.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimSrvRole(acl, user, elId)`

- **It must:** SPEC 5 WO-01: with BIM_SRV_RANK {viewer 1, commenter 2, editor 3, owner 4} and BIM_SRV_NEED {read 1, comment 2, edit 3, share 4, delete 4} just above it: among the user's entries that are project-wide (no element) or for this element, a denial for this element gives null at once; else the highest-ranked role, or null.
- **May use:** BIM_SRV_RANK, BIM_SRV_NEED (this task).
- **Files:** `src/js/engine/history/hub-access.js`, `docs/work-orders/v217/v217.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v217/v217.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimSrvCan(acl, user, elId, action)`

- **It must:** SPEC 5 WO-02: false for an action not in BIM_SRV_NEED; else whether the role's rank reaches the action's need.
- **May use:** bimSrvRole (WO-01).
- **Files:** `src/js/engine/history/hub-access.js`, `docs/work-orders/v217/v217.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v217/v217.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimSrvRedact(result, fields)`

- **It must:** SPEC 5 WO-03: only the listed fields the result has.
- **May use:** nothing.
- **Files:** `src/js/engine/history/hub-access.js`, `docs/work-orders/v217/v217.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v217/v217.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimSrvAudit(user, action, elId, allowed, when)`

- **It must:** SPEC 5 WO-04: {at: when, user, action, element (all as strings), allowed (as a boolean)}.
- **May use:** nothing.
- **Files:** `src/js/engine/history/hub-access.js`, `docs/work-orders/v217/v217.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v217/v217.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] The server

Claude's: the owner chooses a host and the account system; the same rules run there; the app's sharing panel and the access log; a security review before anything is public. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 217, Notion.
