# PennDOT engineering programs — official documentation inventory

Source: **https://penndot.engrprograms.com** — PennDOT's official Engineering Programs site
(Bureau of Business Solutions and Services, Engineering Software Section). Compiled 2026-09-15.

## The finding that matters

**PennDOT publishes the user manuals publicly, and those manuals document the input file format
field by field.** No licence, no login. This unblocks Track C2 (the pre/post-processor) completely
— the input-record formats were the only missing piece.

Verified by reading the PDFs directly:

- PSLRFD manual — Ch.5 "Input Description", Ch.6 "Detailed Input Description"
- STLRFD manual — Ch.5 "Input Description", Ch.6 "Detailed Input Description"
- ABLRFD manual — Ch.5 documents command records **"CFG - Configuration Command" through
  "OUI - Output of Intermediate Data Command"**, alphabetically and in recommended order
- BAR7 manual — Ch.5 "Input Data Requirements", with **12 illustrated input forms** giving field
  layouts and **column positions**

**Two different input styles, which matters for the writer's architecture:**

- **The LRFD programs** (PSLRFD, STLRFD, ABLRFD, BXLRFD, BPLRFD, FBLRFD, TRLRFD, SNLRFD) use
  **three-letter named command records** — CFG, OUI and so on. Free-form, order-tolerant,
  self-describing. Straightforward to generate.
- **The older LFD programs** (BAR7, BOX5, PS3, ABUT5, ARCH) use **fixed-column card-image input**
  laid out on numbered input forms. Column-position sensitive, so the writer must pad exactly.

A single writer should target the LRFD command-record style first. It is both easier and the one
used by the programs still being updated.

## Programs, with official descriptions

Versions and dates below are read from the manuals themselves where verified.

### LRFD suite (AASHTO LRFD + PennDOT DM-4)

| Program | What it does | Manual verified |
|---|---|---|
| **PSLRFD** | LRFD Prestressed Concrete Girder Design and Rating | v2.17.0.0, Feb 2026 |
| **STLRFD** | LRFD Steel Girder Design and Rating | v2.10.0.0, Mar 2026 |
| **ABLRFD** | LRFD Abutment and Retaining Wall Analysis and Design | v1.20.0.0, Apr 2025 |
| **BXLRFD** | LRFD Box Culvert Design and Rating | not yet verified |
| **BPLRFD** | LRFD Bearing Pad Design and Analysis | not yet verified |
| **FBLRFD** | LRFD Floorbeam Analysis and Rating | not yet verified |
| **TRLRFD** | LRFD Truss Analysis and Rating | not yet verified |
| **SNLRFD** | LRFD Sign Structure Analysis | not yet verified |
| **SPLRFD** | LRFD Steel Girder Splice Design and Analysis (discontinued) | not yet verified |

### LFD / legacy suite (AASHTO Standard Specifications, Load Factor Design)

| Program | What it does | Manual verified |
|---|---|---|
| **BAR7** | Bridge Analysis and Rating | v7.15.0.0, Feb 2018 |
| **PS3** | Prestressed Concrete Girder Design and Rating (LFD) | not yet verified |
| **BOX5** | Box Culvert Design and Rating (LFD) | not yet verified |
| **ABUT5** | Abutment and Retaining Wall | not yet verified |
| **ARCH** | Analyse and design a reinforced concrete arch culvert to the AASHTO Standard Specifications using Load Factor Design. v1.1.0.0 | URL given by PennDOT |
| **CBA** | Continuous Beam Analysis | not yet verified |
| **BRGEO** | Bridge Geometry | not yet verified |
| **BSP** | Beam Section Properties | not yet verified |
| **CAMBR** | Field Check of Camber | not yet verified |
| **EngAsst** | Engineering Assistant — the GUI front end to the suite | separate PDF |

Discontinued and listed for completeness: HGEO (Horizontal Geometry), GRPRO (Grade Profile),
CLLMR (Comparison of Live Load Moments and Reactions), SIGN.

**Note on ARCH.** PennDOT has its own reinforced concrete arch program, doing the same job as the
firm's in-house `arch5.for` but for culverts and to the AASHTO Standard Specifications under Load
Factor Design. Worth reading its manual alongside the ARCH5 port — it is the closest published
description of the same problem.

## Licensing, in PennDOT's own terms

The programs are licensed per firm, with a fee schedule per program. Taking ARCH as the published
example: **$500 new licence (private), $100 (government/education), free to federal and state
transportation agencies**, and **$50 to update** from a previous version, for all user types.
PennDOT states it does not offer demonstration or evaluation versions.

The **manuals are free and public**; the **programs are not**. That distinction is the whole basis
of the Track C plan: read the published format, generate valid input, parse the output, and let the
licensed program do the code checks it is verified for.

## Direct manual URLs

Pattern: `https://penndot.engrprograms.com/home/Ordering/User Manual/<NAME> Users Manual.pdf`
(the space is URL-encoded as `%20`).

**Verified present — read directly:**

    https://penndot.engrprograms.com/home/Ordering/User%20Manual/PSLRFD%20Users%20Manual.pdf
    https://penndot.engrprograms.com/home/Ordering/User%20Manual/STLRFD%20Users%20Manual.pdf
    https://penndot.engrprograms.com/home/Ordering/User%20Manual/ABLRFD%20Users%20Manual.pdf
    https://penndot.engrprograms.com/home/Ordering/User%20Manual/BAR7%20Users%20Manual.pdf

**Given by PennDOT's own ARCH page:**

    https://penndot.engrprograms.com/home/Ordering/User%20Manual/ARCH%20Users%20Manual.pdf

**Pattern-inferred, NOT yet verified** — these follow the same naming but were not opened:

    BXLRFD, BPLRFD, FBLRFD, TRLRFD, SNLRFD, SPLRFD, PS3, BOX5, ABUT5, CBA, BRGEO, BSP, CAMBR

**Other official documents:**

    https://penndot.engrprograms.com/home/Ordering/OrderForm(2025-08).pdf
    https://penndot.engrprograms.com/home/Ordering/UpdateForm(08-25).pdf
    https://penndot.engrprograms.com/home/Ordering/EngAsst(2025-08).pdf

Per-program ordering pages, each carrying the official description, current version and fee:
`https://penndot.engrprograms.com/home/Ordering/<NAME>.htm`

E-notification archive — release notes and bug fixes per version, useful for tracking format
changes between releases:
`https://penndot.engrprograms.com/home/mailinglist/archive/`

## Why these are not already downloaded here

`penndot.engrprograms.com` is not on this session's network allowlist, so neither the cloud
container nor the desktop workspace could fetch the PDFs. The content above was read through the
web-fetch path, which can read a page but cannot save a file. Run `fetch_manuals.sh` (next to this
file) on any machine with normal internet access to pull them all down.

## Next step for Track C2

Read PSLRFD Ch.5 and Ch.6 and write up the command records as a specification document, the way the
ARCH5 port was scoped. That specification, not the PDF, is what the input writer is built against.
