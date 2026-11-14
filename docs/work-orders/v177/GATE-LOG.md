# v177 gate log

Written by `tools/gate.py ship`. Claude's audit marks each row (`/audit`).

| Date | Tasks | Checks | Local model | Audit |
|---|---|---|---|---|
| 2026-11-13 | WO-01 | 4 passed | pass | ok |
| 2026-11-13 | WO-02 | 4 passed | pass | fixed (audit commit: try in begin, names optional) |
| 2026-11-13 | WO-03 | 4 passed | pass | fixed (audit commit: try in begin, names optional) |
| 2026-11-13 | WO-04 | 4 passed, 1 warning(s) | concern:  / Line 220:** The function does not handle the case where the `pts` list is not a valid polygon (e.g., self-intersecting or not closed). This is an ed | fixed (audit commit: try in begin, names optional); the concern is outside the spec |
| 2026-11-13 | WO-05 | 4 passed, 1 warning(s) | concern:  / Line 270:** The code checks if the host is an `IfcWall`, but the SPEC allows for other types of hosts. The code should be modified to handle other v | ok; the concern is wrong (the spec asks for IfcWall hosts) |
| 2026-11-13 | WO-06 | 4 passed | pass | ok |
| 2026-11-13 | WO-07 | 4 passed | pass | ok |
