# PennDOT LRFD input file specification — working skeleton

For Track C2, the pre/post-processor. Compiled from the official public user manuals
(PSLRFD v2.17.0.0 Feb 2026; STLRFD v2.10.0.0 Mar 2026; ABLRFD v1.20.0.0 Apr 2025).

**Status: skeleton, not yet complete.** The command inventory, ordering rules and section/page
references below are extracted and verified. The field-by-field definitions are not — see
"What is still missing" at the end. This document is the frame the detail gets filled into.

## The architectural finding

PSLRFD has **44** commands. STLRFD has **57**. **23 of them are the same command.**

    CDF CFG CLD CTL DLD DPL GEO LDF OAN OIN ORF OSC PLD
    SAL SID SKW SLB SLL SPL SST TTL UDF URF

That shared core covers configuration, titling, control, structure identification, geometry, span
lengths, skew, distribution factors, the slab, applied loads, load factors and every output
selection. ABLRFD uses the same shape (its Chapter 5 runs CFG through OUI).

**So one writer serves all of them.** Build a generic command-record emitter plus a shared-core
module, then a thin per-program module for the member commands. The alternative — a separate
writer per program — would triplicate 23 commands' worth of work and let them drift apart.

What differs is the **member**, which is exactly what you would expect:

- **PSLRFD (21 unique)** — prestressed concrete: beam dimensions, strand configuration for design
  and analysis, strand configuration at the beam end, debonded strands, drape points, tendons,
  stirrups, diaphragms, concrete and prestressing-steel material properties, girder stability.
- **STLRFD (34 unique)** — steel: rolled beam and plate girder design, built-up and plate analysis
  sections, section holes and section loss, transverse/longitudinal/bearing stiffeners, shear
  connectors (stud and channel), brace points, field splice locations, deck pour sequence, wind
  loads, fatigue life and fatigue vehicles.

### A trap to record now

**`DPL` exists in both programs and means different things.**

    PSLRFD  DPL = Drape Point Location
    STLRFD  DPL = Design Plate Location

The writer must never resolve a command code without knowing which program it is emitting for.
A shared code table keyed only on the three letters would silently produce a valid-looking,
wrong input file — the worst possible failure mode for this work.

## Command ordering

PSLRFD Chapter 5 section **5.2 is "ORDER OF COMMANDS"** — order is prescribed, not free. The
writer emits in the manual's order rather than in model-traversal order. The specific sequence is
in that section and still needs extracting.

## PSLRFD — full command inventory (44)

Presented in the manual's own order.

    CFG  Configuration                      MST  Mild Steel Material Properties
    TTL  Title                              DES  Design
    CTL  Control                            SST  Slab Reinforcement Location
    SID  Structure Identification           BDM  Beam Dimensions
    GEO  Geometry                           SCD  Strand Configuration for Design
    CDF  Computed Distribution Factor       SCA  Strand Configuration for Analysis
    UDF  User Distribution Factor           SCE  Strand Configuration at Beam End (Draped)
    URF  User Defined Reaction Dist Factor  STI  Stirrup
    SSI  Span Specific Information          DBS  Debonded Strands
    SPL  Span Length                        SLB  Slab
    SKW  Skew                               DIA  Diaphragm Details
    MCS  Concrete Material Properties       DPL  Drape Point Location
    MCA  Concrete Material Allowable Props  TND  Tendon Location
    MCG  Concrete Material Props (All Gdrs) PLD  Pedestrian Live Load
    MPS  Prestressing Steel Material Props  LDF  Load Factor
    CLD  Concentrated Load                  GSC  Girder Stability (Part 1)
    DLD  Distributed Load                   GS2  Girder Stability (Part 2)
    SLL  Special Live Loading               GS3  Girder Stability (Part 3)
    SAL  Special Axle Load                  OIN  Output of Input Data
    OVH  Overhang                           OAN  Output of Analysis Results
    BDT  Beam Detailing                     OSC  Output of Specification Checking
    ORF  Output of Rating Factors           OSM  Output Summary

Known section references: 5.3 CFG (p5-12), 5.4 TTL (p5-13), 5.7 GEO (p5-22).
Chapter 6 carries the expanded detail, including 6.5 CTL and 6.7 GEO.

## STLRFD — full command inventory (57), with section and page

Chapter 5 runs pages 5-1 to 5-126; Chapter 6 (expanded detail, section numbers matching) runs
6-1 to 6-79.

| Cmd | Name | Sec | Page |
|---|---|---|---|
| CFG | Configuration | 5.3 | 5-12 |
| TTL | Title | 5.4 | 5-13 |
| CTL | Control | 5.5 | 5-14 |
| SID | Structure Identification | 5.6 | 5-22 |
| GEO | Geometry | 5.7 | 5-23 |
| CDF | Computed Distribution Factor | 5.8 | 5-26 |
| UDF | User Defined Distribution Factor | 5.9 | 5-31 |
| URF | User Defined Reaction Distribution Factor | 5.10 | 5-33 |
| SKW | Skew Angle | 5.11 | 5-34 |
| SPL | Span Length | 5.12 | 5-36 |
| HNG | Hinge Location | 5.13 | 5-37 |
| UDA | User Defined Analysis Points | 5.14 | 5-38 |
| MAT | Material | 5.15 | 5-39 |
| DRB | Design Rolled Beam | 5.16 | 5-42 |
| DP1 | Design Plate Girder (Part 1) | 5.17 | 5-46 |
| DP2 | Design Plate Girder (Part 2) | 5.18 | 5-50 |
| DPL | Design Plate Location | 5.19 | 5-54 |
| DTS | Design Transverse Stiffener | 5.20 | 5-55 |
| URB | User Defined Rolled Beam | 5.21 | 5-56 |
| ARB | Analysis Rolled Beam | 5.22 | 5-57 |
| ABU | Analysis Built-Up | 5.23 | 5-59 |
| APL | Analysis Plate | 5.24 | 5-62 |
| SHO | Section Hole | 5.25 | 5-65 |
| SLS | Section Loss | 5.26 | 5-67 |
| SLB | Slab | 5.27 | 5-69 |
| SST | Slab Reinforcement Location | 5.28 | 5-71 |
| DPS | Deck Pour Sequence | 5.29 | 5-74 |
| DPC | Deck Pour Concentrated Load | 5.30 | 5-75 |
| DPD | Deck Pour Distributed Load | 5.31 | 5-76 |
| PLD | Pedestrian Live Load | 5.32 | 5-77 |
| LDF | Load Factor | 5.33 | 5-78 |
| CLD | Concentrated Load | 5.34 | 5-81 |
| DLD | Distributed Load | 5.35 | 5-83 |
| WPD | Wind Program Defined | 5.36 | 5-85 |
| WUD | Wind User Defined | 5.37 | 5-87 |
| DOL | Deck Overhang Loads | 5.38 | 5-88 |
| SLL | Special Live Loading | 5.39 | 5-90 |
| SAL | Special Axle Load | 5.40 | 5-91 |
| FTL | Fatigue Life | 5.41 | 5-92 |
| FGV | Fatigue Gross Vehicle | 5.42 | 5-93 |
| FTG | Fatigue | 5.43 | 5-94 |
| BRP | Brace Point | 5.44 | 5-96 |
| CBR | Continuous Brace | 5.45 | 5-98 |
| TST | Transverse Stiffener | 5.46 | 5-99 |
| LST | Longitudinal Stiffener | 5.47 | 5-101 |
| BST | Bearing Stiffener | 5.48 | 5-103 |
| BSD | Bearing Stiffener Design | 5.49 | 5-106 |
| SCS | Shear Connector Stud | 5.50 | 5-108 |
| SCC | Shear Connector Channel | 5.51 | 5-109 |
| FSL | Field Splice Location | 5.52 | 5-110 |
| LAS | Lateral Bending Stress | 5.53 | 5-113 |
| OIN | Output of Input Data | 5.54 | 5-117 |
| OSP | Output of Section Properties | 5.55 | 5-118 |
| ODG | Output of Design Trials | 5.56 | 5-119 |
| OAN | Output of Analysis Results | 5.57 | 5-120 |
| OSC | Output of Specification Checking | 5.58 | 5-123 |
| ORF | Output of Rating Factors | 5.59 | 5-126 |

## What canvas_v10 can supply today, and what Track B must add

Mapping the shared core against the current model. This is the useful part: it says exactly what
the structural object model has to carry for the writer to be possible.

**Already in the model (or trivially derivable):**

    TTL  SID     project and structure identification - the title block already holds this
    GEO             bridge geometry - partially, from the plan model
    SPL             span lengths - derivable once alignment/support objects exist
    SKW             skew angle - a property the model should carry anyway
    SLB             slab thickness and width - the floor/deck object
    SST             slab reinforcement location - needs the rebar gap noted below

**Needs Track B item 1 (the structural object model):**

    CLD  DLD       concentrated and distributed loads - no load objects exist yet
    LDF             load factors and limit-state combinations - no load combination objects
    PLD             pedestrian live load - same
    SLL  SAL       special live loading and axle loads - needs a vehicle/live-load model
    CDF  UDF  URF  distribution factors - computed or user-specified per girder line

**Needs Track B item 2 (the section-profile library):**

    PSLRFD  BDM SCD SCA SCE DBS STI TND    beam shape, strand pattern, stirrups, tendons
    STLRFD  DRB DP1 DP2 URB ARB ABU APL    rolled shapes and built-up plate sections
            TST LST BST SCS SCC            stiffeners and shear connectors

**Pure output selection, no model data needed:**

    CFG CTL OIN OAN OSC ORF OSM OSP ODG

That split is itself a finding: **the writer is blocked on the same two Track B items the ARCH5
port is blocked on.** Loads and sections are the common prerequisite. Build those once and three
separate pieces of work unblock together.

## What is still missing, and how to get it

The field-by-field definitions. The manuals are large (STLRFD Chapter 5 alone is 126 pages) and
the web-fetch path used to read them only surfaces front matter and contents on a document that
size — it returned the command inventory and section/page map reliably, and would not reach into
the body.

**The unblock is one command.** Run `fetch_manuals.sh` (beside this file) on any machine with
normal internet access. Once the PDFs are in the working folder, text extraction locally gives the
full field definitions, and this skeleton gets filled in properly.

Priority order for extraction once the PDFs are here:

1. **PSLRFD section 5.2, ORDER OF COMMANDS** — governs everything the writer emits.
2. **The 23 shared-core commands**, field by field — one pass serves both programs.
3. **The general syntax rules** from 5.1 and Chapter 4.2 "Preparing Input" — column positions
   versus free format, delimiters, units, file extension. Not yet established either way.
4. **PSLRFD member commands**, then STLRFD member commands.

## Recommended build order for the writer

1. **Output parser first.** It needs no format documentation at all, only a sample output file
   from any past run, and it delivers automated rating reports immediately.
2. **Generic command-record emitter** — takes a command code and an ordered field list, handles
   syntax and ordering. Program-agnostic.
3. **Shared-core module** — the 23 commands, keyed per program to avoid the DPL collision.
4. **PSLRFD member module**, validated against a real job's input file.
5. **STLRFD member module**.

Sources: PennDOT Engineering Programs, https://penndot.engrprograms.com
Manuals read: PSLRFD, STLRFD, ABLRFD, BAR7 user manuals (public, no licence required).
