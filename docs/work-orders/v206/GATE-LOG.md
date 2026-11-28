# v206 gate log

Written by `tools/gate.py ship`. Claude's audit marks each row (`/audit`).

| Date | Tasks | Checks | Local model | Audit |
|---|---|---|---|---|
| 2026-11-24 | WO-07 | 5 passed, 1 warning(s) | skipped | ok (audited 2026-11-28) |
| 2026-11-28 | WO-01 to WO-06 | not gated: in `io/ifc-review.js` on main; the 7 cases pass | none | WO-03 and WO-04 used BigInt (not ES5, the engine would not parse without it): rewritten by Claude with the same results, tested against 200 round trips and two fixed vectors; WO-01 is right for Z-up input but not used by the import (That Open gives +Y up) |
