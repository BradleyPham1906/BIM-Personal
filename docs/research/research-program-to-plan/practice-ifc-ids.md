# Practice, IFC spaces and IDS: sources behind V233 to V238

Research for `docs/research/research-program-to-plan.md`, hypotheses H5 and H6 (`00-question.md`).
Started 2026-11-16. Status: in progress (saved after each part).

Evidence levels: P read in the source itself; S dependable secondary source or a vendor's own claim;
U search summary only. Confidence: high, medium, low.

## 1. Summary

(pending)

## 2. Part A: the owner's claims checked against their sources

All read 2026-11-16. "P" means the source text itself was read (PDF converted to text with pdftotext,
or the page fetched).

| # | Claim in the owner's pages | Source read, and where | Verdict | Correction or precision |
|---|---|---|---|---|
| A1a | WBDG names six programming steps: research the project type, establish goals, gather information, identify strategies, determine quantitative requirements, summarize the program | WBDG "Architectural Programming", legacy.wbdg.org, section Description (P). Page carries no author or date; footer copyright NIBS 2026 | Confirmed | Exact step names: "Research the project type", "Establish goals and objectives", "Gather relevant information", "Identify strategies", "Determine quantitative requirements", "Summarize the program" |
| A1b | Relationship or bubble diagrams are a programmatic strategy | Same page, step 4 (P) | Confirmed | The page says they show which functions sit near each other and can also show circulation links and security or acoustic privacy needs: that is, the diagram already carries more than one relation kind |
| A1c | Net-to-gross calculations | Same page, step 5 (P) | Confirmed with a precision | Efficiency is NASF/GSF; "tare" (circulation, walls, mechanical, electrical, telephone, public toilets) is added as a percentage to total NASF. No figure is given; the typical ratio for the building type is to be researched in step 1, and an existing facility's ratio can inform the target. For tenant work, an "internal gross" is set instead |
| A1d | Client sign-off | Same page, step 6 and "Emerging issues" (P) | Confirmed | Decision-makers sign off the scope of work as described in the program; clients increasingly require verification that the design complies with the program |
| A1e | Site analysis as part of programming | Same page, step 3 (P) | Confirmed | Listed: legal description, zoning and deed restrictions, traffic, utilities, topography, views, built features, climate, vegetation and wildlife |
| A2a | RIBA Stage 1 Project Brief with Spatial Requirements | RIBA Plan of Work 2020 Overview, 146 pp., RIBA 2020, downloaded from riba.org/media/.../2020ribaplanofworkoverviewpdf.pdf (P). The architecture.com copy returned a script page | Confirmed with a correction | The stage is named "Preparation and Briefing" (outcome: "Project Brief approved by the client, and confirmed that it can be accommodated on the site"). Spatial Requirements must be tested against the Project Budget. Feasibility options at Stage 1 "should not be vetted and appraised at this stage": appraisal of options belongs to Stage 2 |
| A2b | Stage 2 Architectural Concept aligned to the brief and adjacency requirements | Same, Stage 2 (P) | Confirmed | Outcome: "Architectural Concept approved by the client and aligned to the Project Brief"; proposals "should demonstrate that the Spatial Requirements are being achieved, along with any adjacency requirements"; the brief may be adjusted to the concept; non-briefed areas (cores) must be developed. The overview also says the project should not go to Stage 3 while any Spatial Requirements or room adjacencies remain inconclusive, and the concept and brief are signed off at Stage 2 |
| A2c | Stage 3 Spatial Coordination tests rather than reinvents | Same, Stage 3 (P) | Confirmed | Stage 3 "is fundamentally about testing and validating the Architectural Concept"; it "is not about adjusting the Architectural Concept"; changes go through the Change Control Procedure |
| A3a | GSA P100 2024: area checked at every design phase against the approved program | PBS-P100 2024 (May 2024), gsa.gov/system/files/P100 2024 Final_0.pdf, section 1.8.2 (P); 2024 P100 Submittal Matrix v2.0 (P) | Confirmed with a precision | 1.8.2: design to the area in the approved prospectus and the program of requirements; "The area must be confirmed at each phase of design", measured per GSA's National Business Space Assignment Policy (May 2009 or current), which builds on ANSI/BOMA Z65.1 with a PBS-specific category; projects over the prospectus area "will need to be redesigned". Target usable-to-gross ratio for new buildings: 80 percent. The Submittal Matrix asks "Compare net, usable and gross SF of design concepts to program" at each concept submittal (preliminary, development, final), and at later phases asks for BIM spaces with "correct areas for ANSI/BOMA validation" |
| A3b | At least three distinctly different concept schemes | P100 2024 Appendix A.3.1 "Submittal definitions" (P); Submittal Matrix (P) | Confirmed | "Three or more distinctly different architectural design schemes at a working level", with massing models, site context and narrative "to allow comparison and selection of a design direction"; the matrix also asks to highlight "relative merits or challenges" of the concepts, and the "Concept" submittal must show the space program is accomplished "including any adjacency and functional requirements" |
| A4 | RAIC chapter 6.2: functional requirements and adjacencies; alternatives compared by program, adjacency, sustainability, net-to-gross, circulation ratio; block models for sun, shade, wind | RAIC Canadian Handbook of Practice, chapter 6.2 "Schematic Design", chop.raic.ca (P). No edition date on the page; cites RAIC Document Six (2018) | Confirmed | Comparison list also includes wall-to-floor ratio and capital, operating and maintenance cost (said to be speculative at this stage). The sun, shade, wind claim also covers snow and rain, "on the project and its surrounding environment" |
| A5 | AIA schematic design checklist (12.03.01): what it expects | AIA Best Practices 12.03.01, aia.org/sites/default/files/2024-12/... (7 pp.; pages marked "AIA 2017") (P) | Confirmed (content summarised here) | Objectives: documents showing scale and relationships of components "in conformance with program"; building areas and volumes demarcated. Tasks include: update project area and use summaries; review the program and agree program requirements with the owner (keyed to B101-2007 3.2.1 to 3.2.4); verify all program requirements, including support areas, are in the plans; discuss alternative approaches with the owner; prepare an approval letter for phase completion; peer review. Keyed to AIA B101-2007 |
| A6a | IfcSpace's place in the spatial structure | IFC 4.3 documentation source, github.com/buildingSMART/IFC4.3.x-development, branch master, `docs/schemas/core/IfcProductExtension/Entities/IfcSpace.md`, read raw (P). standards.buildingsmart.org answered 403 and ifc43-docs redirects there | Confirmed | A space is associated to a building storey (or, for exterior spaces, to a site) through IfcRelAggregates (the "Spatial Decomposition" concept: relating object IfcSite, IfcBuildingStorey or IfcSpace). CompositionType: COMPLEX = space group, ELEMENT = space, PARTIAL = partial space. A space is also a spatial container for furniture and other elements (IfcRelContainedInSpatialStructure). Grouping of spaces that need not be adjacent (an apartment, a department) is IfcZone through IfcRelAssignsToGroup, non-hierarchical (IfcZone.md, P) |
| A6b | Name versus LongName | Same file (P); Pset_SpaceCommon.md (P) | Confirmed | Name holds "the unique name (or space number) from the plan"; LongName holds the full descriptive name; ObjectType "usually the functional category of the space"; Description free text. Classification by national code goes through IfcClassificationReference |
| A6c | Predefined types | `Types/IfcSpaceTypeEnum.md` (P) | Confirmed with a correction | SPACE, PARKING, GFA (a per-storey gross floor area space), INTERNAL, EXTERNAL, BERTH, USERDEFINED, NOTDEFINED. INTERNAL and EXTERNAL are deprecated as of IFC 4.3.2.0 in favour of Pset_SpaceCommon.IsExternal. The predefined types do not name room functions (office, kitchen): function goes in ObjectType, LongName, a type object or a classification |
| A6d | Space boundaries, physical or virtual | `Entities/IfcRelSpaceBoundary.md` (P) | Confirmed | Objectified one-to-one relation between a space and an element; PhysicalOrVirtualBoundary = PHYSICAL (RelatedBuildingElement is the wall, slab ...) or VIRTUAL (RelatedBuildingElement must be an IfcVirtualElement, mandatory since IFC4). 1st-level (from inside the space) versus 2nd-level type A (a space on the other side) and type B (an element on the other side); the IfcSpace geometry takes priority over the boundaries when they disagree |
| A6e | Base quantities | `QuantitySets/Qto_SpaceBaseQuantities.md` (P) and bSDD API class IfcSpace, IFC 4.3 (S, buildingSMART's own service) | Confirmed | Qto_SpaceBaseQuantities: Height, FinishCeilingHeight, FinishFloorHeight, GrossPerimeter, NetPerimeter, GrossFloorArea, NetFloorArea, GrossWallArea, NetWallArea, GrossCeilingArea, NetCeilingArea, GrossVolume, NetVolume. GrossFloorArea includes area under columns and inner walls inside the space; NetFloorArea excludes them, slab openings and protrusions |
| A6f | Common property sets, occupancy requirements | `PropertySets/Pset_SpaceCommon.md`, `Pset_SpaceOccupancyRequirements.md` (P for the definitions); property lists from bSDD (S) | Confirmed, with an addition the owner's pages miss | Pset_SpaceCommon: IsExternal, GrossPlannedArea, NetPlannedArea, PubliclyAccessible, HandicapAccessible (bSDD list; the IFC4 "Reference" property was not in that list). GrossPlannedArea is defined as "Total planned gross area ... Used for programming"; NetPlannedArea likewise (`docs/properties/g/GrossPlannedArea.md`, `n/NetPlannedArea.md`, P). So IFC already carries the programme's required area on the designed space, beside the measured quantity. Pset_SpaceOccupancyRequirements: OccupancyType, OccupancyNumber, OccupancyNumberPeak, OccupancyTimePerDay, AreaPerOccupant, MinimumHeadroom, IsOutlookDesirable |
| A7a | IDS facets: entity, attribute, classification, property, material, partOf | github.com/buildingSMART/IDS, default branch (last commit 2026-09-25), `Documentation/UserManual/README.md`, `specifications.md`, `partof-facet.md` (P) | Confirmed | "There are six different Facets"; a specification has a description, an applicability and requirements, both built from facets; values may be simple or "complex restrictions" (pick lists, patterns, numeric ranges, lengths). Supported schemas: IFC2X3, IFC4, IFC4X3_ADD2 |
| A7b | IDS does not check geometry | `specifications.md`, "Limitations" (P) | Confirmed, and wider than stated | Out of scope: geometry checks, "checks that rely on calculated or dynamic values", data outside the model, domain-specific relationships. Its own counter-example is directly ours: "The total area of all office spaces must be more than 300m2" cannot be checked by IDS. Per-space attribute or property values (for example NetPlannedArea within a range) can be |
| A7c | What partOf can express about spaces and storeys | `partof-facet.md` (P) | Confirmed | partOf names an entity (for example IFCBUILDINGSTOREY or IFCSPACE) and optionally one relation, followed recursively: IFCRELAGGREGATES, IFCRELASSIGNSTOGROUP, IFCRELCONTAINEDINSPATIALSTRUCTURE, IFCRELNESTS, IFCRELVOIDSELEMENT / IFCRELFILLSELEMENT. So "every IfcSpace is part of an IfcBuildingStorey by aggregation" and "every space belongs to some IfcZone" are expressible. The partOf entity takes only an IFC class and a predefined type (the entity facet's two parameters, `entity-facet.md`, P), so "space 1.04 is on the storey named Level 2" cannot be written: the storey's own Name cannot be restricted inside partOf (inference from the facet's parameters, high confidence). It cannot express adjacency between spaces or a required area total |

## 3. Findings

### B. Area measurement standards

Question: which definitions of net and gross area a programme tool should let a project choose, and how each treats
circulation. Read 2026-11-16.

| Standard | Publisher, edition, date | Text free or sold | Categories (names as the standard uses them) | Circulation | Level |
|---|---|---|---|---|---|
| IPMS: All Buildings | International Property Measurement Standards Coalition (IPMSC; RICS hosts the PDF), effective 15 January 2023, replaces all earlier IPMS asset standards; copyright 2022 IPMSC | Free PDF (copies allowed with acknowledgement) | IPMS 1 (external, whole building), IPMS 2 (internal, to the Internal Dominant Face), IPMS 3.1 / 3.2 (exclusive occupation, external / internal), IPMS 4.1 / 4.2 (selected areas). Optional Component Areas summing to IPMS 1: A columns, walls, notional boundaries (A1 to A5); B vertical penetrations (B1 vertical circulation: stairs, lift shafts, escalators; B2 vertical technical shafts at or over 0.1 m2); C technical areas (plant rooms); D sanitary areas; E horizontal circulation areas; F primary areas; G secondary areas (G1 amenity, G2 ancillary); H other areas | Two components: B1 (vertical) and E (horizontal, "whether or not enclosed"); horizontal circulation that forms part of an occupant's fit-out may stay in F | P |
| DIN 277 | DIN (sold by DIN Media, formerly Beuth), edition 2021-08, replacing DIN 277-1:2016-01 | Sold | BGF (Brutto-Grundfläche, gross) = NRF (Netto-Raumfläche, net room area) + KGF (Konstruktions-Grundfläche: outer, inner and partition wall areas). NRF = NUF (Nutzungsfläche, usage area, groups NUF 1 to 7) + TF (Technikfläche, technical area) + VF (Verkehrsfläche, circulation area). 2021 renamed Nutzfläche to Nutzungsfläche, Netto-Grundfläche to Netto-Raumfläche, Technische Funktionsfläche to Technikfläche; NUF 7 gained "rooms whose purpose cannot yet be determined" | VF is the part of NRF for horizontal and vertical circulation or circulation safety: corridors, stairwells, ramps, escape balconies, escalators, lift shafts, garage driveways | S: weka.de and bauprofessor.de (two independent secondary sources, consistent); the text itself not read. The names of NUF groups 1 to 7 were not confirmed here |
| ANSI/BOMA Z65.1-2017 (office) | BOMA International, 2017 (with ANSI) | Sold | Boundary Area, Rentable Exclusions, Floor Rentable Area, Tenant Area, Tenant Ancillary Area, Occupant Area, Building Amenity Area, Building Service Area, Floor Service Area, Floor Usable Area, BOMA Rentable Area; Method A (load factors by floor and building: Floor Allocation Ratio, Building Allocation Ratio, renamed from R/U and R/O) or Method B (one Load Factor B) | Method B measures Base Building Circulation, "the minimum, necessary path" for access and egress on a multi-occupant floor, as its own category; Method A has no such category: shared circulation falls into floor and building service area, and corridors giving exclusive passage are Tenant Ancillary Area | S: Archibus help (vendor documentation) and Extreme Measures help desk (a measurement consultancy); the text itself not read |
| ISO 9836:2017 | ISO/TC 59/SC 15, edition 3, 2017 | Sold | Measurement concepts: intra-muros and extra-muros, the wall-centre method, national variants; indicators of area and volume for planning and performance | Not read | S/U: ISO's catalogue lists it as withdrawn (search summary; iso.org refuses scripts, 403); a New Zealand and an Irish retailer report it withdrawn without replacement, the Irish one on 2024-03-22. **Not a standard to offer as current** |
| GSA (PBS) | P100 2024 section 1.8.2 points to GSA's National Business Space Assignment Policy (May 2009 or current) | Free (P100 read) | Usable and gross area as defined in that policy; ANSI/BOMA Z65.1 as the foundation with a PBS-specific category; the Submittal Matrix asks for net, usable and gross square feet | Inside the BOMA framework; the policy itself not read | P for P100; the policy not read |
| FICM (US postsecondary) | NCES 2006-160, May 2006 (Postsecondary Education Facilities Inventory and Classification Manual) | Free (nces.ed.gov) | Gross area (outside faces of exterior walls) = net usable area + structural area; net usable = net assignable area (NASF: 10 assignable major space-use categories: classrooms, laboratories, offices, study, special use, general use, support, health care, residential, unclassified) + nonassignable area (building service, circulation, mechanical). NASF measured to the inside faces of bounding walls; spaces under 3 ft clear height excluded | Circulation Area: areas "required for physical access to some subdivision of space", walled or not: corridors, elevator lobbies, fire towers, stair, elevator and escalator footprints on each floor, loading docks. Private aisles used only inside one unit's suite are **not** circulation | P (NCES pages 3.2.1, 3.2.2, 3.2.5) |

Findings:

- **The standards disagree on where circulation inside a department goes** (P for IPMS and FICM, S for BOMA): IPMS
  lets an occupant's fit-out circulation stay in primary area; FICM excludes intra-suite aisles from circulation;
  BOMA Method B counts a minimum notional corridor whether or not it is built. So "circulation ratio" is not one number
  across standards: a programme tool that reports it must say which standard it measured by (inference, high
  confidence).
- **Every standard has the same three-level shape**: a gross area at the outer (or inner) face, a structural or
  construction deduction, and a net area split into a primary or assignable part and non-primary parts (technical,
  circulation, sanitary or service). The names differ. A programme tool can carry one internal set of categories
  (primary, circulation horizontal, circulation vertical, technical, sanitary, structural) and map each to the
  standard chosen (inference from the table, medium confidence: the mapping of sanitary areas differs: IPMS D,
  FICM building service, DIN NUF or TF depending on use, not checked).
- **Free texts a tool could cite directly**: IPMS All Buildings 2023 and FICM 2006. DIN 277 and BOMA 2017 are sold:
  their category names may be used (they are facts), their definitions only in our own words.
- **Typical ratios, with their source only**: GSA P100 2024 sets a usable-to-gross target of 80 percent for new
  buildings (P). WBDG says the ratio for the building type is to be researched and gives none (P). No other ratio was
  read in a primary source here; none is recorded.

Confidence: high for IPMS, FICM and GSA (P); medium for DIN 277 and BOMA (two consistent secondary sources each);
low for ISO 9836's exact withdrawal date.

### C. IDS and IfcSpace in the worker

**C1. ifctester, the package (P: PyPI JSON API and the wheel itself, listed as a zip, nothing run; 2026-11-16).**

- Current release 0.9.0 (wheel uploaded 2026-09-29; 28 releases). Licence: the classifier says LGPL-3.0-or-later;
  the `license` field is empty. Pure Python itself (`py3-none-any`): `ids.py`, `facet.py`, `reporter.py`, `ids.xsd`,
  under 200 KB of code.
- The wheel is 25.4 MB because it carries a web app (`ifctester/webapp/`, 33 MB unpacked): its own Pyodide
  (pyodide.asm.wasm 8.6 MB), numpy, shapely, and an `ifcopenshell-0.8.5+a51b2c5 ... pyodide_2025_0_wasm32` wheel
  (14.7 MB). Its worker script loads Pyodide, then numpy, then micropip-installs that IfcOpenShell wheel and odfpy,
  then shapely, then ifctester itself (read in `worker-*.js` and `worker/api.py`). So **IfcOpenShell's own project
  already runs ifctester in a browser on Pyodide**, with the same IfcOpenShell version the app vendors (0.8.5), though
  a different build (14,705,521 bytes against the app's 14,654,346).
- Declared dependencies (Requires-Dist, none marked optional): ifcopenshell, python-dateutil, xmlschema, elementpath,
  numpy, odfpy, pystache, bcf-client, flask, typing_extensions. Read in the source: `ids.py` imports `xmlschema` at
  module level; `facet.py` imports `elementpath.regex`; `reporter.py` imports typing_extensions at module level and
  the ODS, HTML (pystache) and BCF (bcf.v2.bcfxml) pieces for their own reporters. Flask is for the local web server.
  So the checker's core needs ifcopenshell, xmlschema, elementpath, typing_extensions, python-dateutil; odfpy,
  pystache, bcf-client and flask are needed only for some reports or the server (inference from the imports; a
  `micropip.install(..., deps=False)` or a hand-picked set of wheels would be needed, untested).
- xmlschema 4.3.2 (MIT, pure Python, 505 KB wheel, Python 3.10 or later, needs elementpath 5.1.3 to below 6) and
  elementpath 5.1.4 (MIT, pure Python, 262 KB wheel, no runtime dependencies) (P, PyPI JSON).
- Licences to note: bcf-client 0.9.0 is GPL-3.0 (classifier); odfpy is Apache-2.0 or GPL; pystache MIT. Under the
  owner's 2026-11-13 rule a GPL wheel may ship only as its own file run in the worker, which the BCF reporter would
  be; the core checker does not need it.
- Documentation (docs.ifcopenshell.org, IfcOpenShell 0.9.0.post1, P): ifctester "works from the command line, as a
  web app, or as a library"; reporters Console, JSON, SQLite, ODS, HTML, BCF; validation is `ids.validate(model)` on
  an `ifcopenshell.open()` model.

**C2. What the repository already carries (P: `runtime/MANIFEST.json`, the files, the V177 note).**

- `runtime/pyodide/0.29.5/`: Pyodide 0.29.5, numpy 2.2.5 (pyemscripten_2025_0 wasm32), stdlib.
- `runtime/ifcos/0.8.5/`: ifcopenshell 0.8.5 (cp313 pyodide_2025_0 wasm32, 14,654,346 bytes; LGPL-3.0-or-later,
  GPL-3.0 in effect as a file because of CGAL), isodate 0.7.2, lark 1.3.1, python_dateutil 2.9.0.post0, shapely
  2.0.7, six 1.17.0, typing_extensions 4.15.0.
- `runtime/wheels/`: click 8.3.3, ladybug_comfort 0.19.13, ladybug_core 0.44.63, ladybug_geometry 1.35.7,
  ladybug_radiance 0.2.12 (AGPL).
- Also radiance, three.js 0.186.1 with Draco, cc-ifc (cfbd948) with Manifold, Jolt 1.1.1.
- **Not there:** ifctester, xmlschema, elementpath, odfpy, pystache, bcf-client. The vendored IfcOpenShell wheel
  (514 files) does not contain ifctester. Already there of ifctester's core needs: ifcopenshell, python-dateutil,
  typing_extensions. To add: ifctester (pure Python), xmlschema and elementpath (pure Python, MIT, about 0.77 MB as
  wheels), and their pinning in MANIFEST.json.
- research-ifcopenshell-app.md, decision D1 (a), the owner 2026-11-13: GPL and AGPL libraries are allowed as separate
  files run only in the Python worker. The V177 experiment e05 already proved, in the wasm build, "a kept GlobalId"
  (`wall.GlobalId = "<22 chars>"`), and `src/py/bim_ifcos.py` has `bim_ifcos_keep_guid(product, guid)` that checks the
  22-character IFC alphabet and uniqueness before assigning. No mention of IfcSpace or IDS in that note or adapter.

**C3. The calls that write a space (P: docstrings and examples in the vendored 0.8.5 wheel's source, read as text;
consistent with docs.ifcopenshell.org).**

| Step | Call |
|---|---|
| Create the space | `ifcopenshell.api.root.create_entity(model, ifc_class="IfcSpace", predefined_type="SPACE", name="1.04")`: generates a GlobalId (`ifcopenshell.guid.new()`) and ownership history |
| Put it on its storey | `ifcopenshell.api.aggregate.assign_object(model, products=[space], relating_object=storey)`: the docstring's own example aggregates site to project, building to site, storey to building and space to storey; `spatial.assign_container` is for elements (furniture) in a space, and the docstring notes an object is either aggregated or contained, not both |
| Long name, object type | `ifcopenshell.api.attribute.edit_attributes(model, product=space, attributes={"LongName": "Meeting room", "ObjectType": "..."})`, or direct assignment |
| Property set | `pset = ifcopenshell.api.pset.add_pset(model, product=space, name="Pset_SpaceCommon")` then `ifcopenshell.api.pset.edit_pset(model, pset=pset, properties={"NetPlannedArea": 24.0, "IsExternal": False})`: types come from the buildingSMART template when the pset is standard |
| Quantities | `qto = ifcopenshell.api.pset.add_qto(model, product=space, name="Qto_SpaceBaseQuantities")` then `ifcopenshell.api.pset.edit_qto(model, qto=qto, properties={"NetFloorArea": ..., "Height": ...})`; a blank quantity set is invalid; None quantities are purged |
| Zone (department) | `ifcopenshell.api.group.assign_group(model, products=[...], group=zone)` with an IfcZone created by `root.create_entity` (the documented example uses `group.add_group`, which makes an IfcGroup) |
| GlobalId from an existing id | `ifcopenshell.guid.compress(uuid_hex)` turns a 32-hex UUID (dashes removed) into the 22-character IFC form; `guid.expand` is the inverse; then `space.GlobalId = g`, as `bim_ifcos_keep_guid` already does |

Geometry for the space (a footprint extruded, the "Body SweptSolid" concept: IfcExtrudedAreaSolid of an
IfcArbitraryClosedProfileDef) exists in the wheel (`api/geometry/add_profile_representation.py`,
`add_footprint_representation.py`); its use for spaces was not read here.

Confidence: high that the calls exist and are documented (P); medium that the full chain runs in the app's worker
for IfcSpace (not run here; V177's e05 ran the neighbouring calls for walls and psets).

### D. Programming tools as prior art

Vendor claims are level S at best; where only a search summary or a listing site was available, U. Read
2026-11-16. Several hosts were unreachable or empty to scripts (briefbuilder.com 503; drofus.atlassian.net
"Project Log" page returned no text).

| Tool | What a requirement record holds | How a requirement links to a model room | Revisions and approval | Required against designed |
|---|---|---|---|---|
| dRofus | A "room function" (a programme line, with a room function number) and rooms under it; programmed area and designed area; room data sheets for functional and engineering requirements; room data status: not created, from room template, derived from template, unique (S: help.drofus.com "Area overview and functional analysis"; dRofus wiki, search summaries for the status list, U) | **By a key attribute, the room function number**, set in the IFC or Revit attribute configuration; the number can be synced into the Revit room or space parameter before IFC export; Revit Areas can be linked many-to-one to a function, whose designed gross area takes their values (S) | All changes to project information are logged in a project log; the change list covers function programme, rooms, room data and finishes (U, search summary of the wiki). No approval or locking feature was found | The Area panel lists, per function, the count of IfcSpaces against the count of dRofus rooms ("Diff") and the "BIM area": the sum of the IfcSpaces' areas in that function, including spaces whose number is incomplete. No tolerance or colour rule was stated on the page read (S) |
| BriefBuilder | Requirements in one online model; space requirements; adjacency diagrams; compliance matrices; verification plans (U: Capterra, G2 and GetApp listings via search) | IFC models are uploaded and requirements checked against them (U) | "Change management", "versioning" listed as features (U) | Compliance checking listed (U). Nothing read at level S: the vendor's site refused (503) |
| Trelligence Affinity | Client programme requirements in a spreadsheet form, distributed into 2D and 3D schematic designs; target and actual area and cost (S/U: Architect magazine article and vendor press releases, via search) | Spaces laid out in Affinity's own schematic design; a script can derive an "as-designed" programme from them (U) | Reports include requirements "and their change history" (U) | Flags where schematic design and programme disagree; target against actual square footage (U) |
| Codebook | A room library from templates; room data sheets; schedule of accommodation (U: vendor FAQ and a slide deck, via search) | Room library items linked to Revit rooms, with two-way sync (U) | Its Project Room Data Manager "can track reasons for changes" to room data sheets (U) | "Design model validation" against requirements (U) |
| Onuma Planning System | Space programme ideas turned into shapes sized by area, with name and type; reusable space templates (Program2BIM, from the SEPS2BIM programme criteria of the US DoD and VA) (S: Onuma's help site on Google Sites, via search summary) | The space shape is the record: programme and design are one object (S, inference) | Not found | Reports of area, content and cost from the first placed objects (S) |
| Archicad | A Zone: name, number, category; the Zone Category sets the stamp; area by Inner Edge or Reference Line; walls' and columns' "Relation to Zones" decides boundary and deduction; an "Offset Edge - Fixed Area" command keeps a zone's area while reshaping it, "useful if you are doing space planning based on defined areas" (S: Graphisoft help, Archicad 21 to 28, via search) | Zones are the model rooms themselves; no external requirement link in the core tool | Not covered | Through schedules of zone area (not read) |
| Revit | Rooms (architectural, occupied areas), Spaces (MEP, measured from finish faces, for loads), Areas in Area Plans per Area Scheme (built-in Gross Building and Rentable, "loosely based on BOMA"; custom schemes allowed) (S: Autodesk help pages "About Spaces", "About Area Type Rules", via search) | Spaces take names and numbers from architectural rooms through the Space Naming utility: **matching by room number and name** (S). No built-in required-area field: add-ins (dRofus, Codebook, Ideate BIMLink) add it (S/U) | Not native | Not native; add-ins compare a programmed area parameter with the computed area (U) |

Findings (inference from the table, medium confidence because most rows are S or U):

1. **The requirement and the designed room are separate records joined by a human-readable key** (dRofus: the room
   function number; Revit add-ins: room number), not by an internal id. The key is synced into the model room's
   parameters before export so that an IFC can be checked later. One requirement may be met by several model
   rooms (dRofus counts IfcSpaces per function and reports the difference).
2. **Report per requirement line: count required against count designed, area required against area designed.**
   dRofus sums the designed spaces under each function; the tolerance is a project setting, not a published rule.
3. **History is a change log on the programme records**, not a separate approval engine, in the tools whose
   documentation was reached. Approval appears as a process around the tool (AIA's approval letter, RIBA's sign-off,
   WBDG's client sign-off, part A), not as a feature that was documented at level S.
4. **IFC already has the slot**: Pset_SpaceCommon.NetPlannedArea / GrossPlannedArea (part A6f) carry the programmed
   area on the designed IfcSpace, so a file can be checked per space by anyone, and IDS can require the property
   (part A7).

### E. Relationship vocabularies

Read 2026-11-16.

| Source | Scale | What is rated, and what else is recorded | Level |
|---|---|---|---|
| Muther, Systematic Layout Planning: RMA Planning Guide 1111 "Procedure for Making Relationship Diagrams" (Richard Muther & Associates, 2002, excerpted from Muther and Hales, *Systematic Planning of Industrial Facilities*) | Vowel letters A, E, I, O, U and X; in the diagram A = four lines, E = three, I = two, O = one, U ignored, X = a zigzag "likened to a compressed spring pushing the symbols apart"; standard colour code | Closeness between pairs of activity-areas on a relationship chart; the diagram is then redrawn to scale as a space relationship diagram (blocks of grid squares from the space specification) before a layout | P (the guide). The letter meanings (A absolutely necessary, E especially important, I important, O ordinary closeness, U unimportant, X undesirable) and the practice of a numbered reason code per rating (for example 1 material flow, 2 communications), with no reason needed for U: S/U (study guides and a university course page via search; the guide read does not list them) |
| US VA PG-18-9 Space Planning Criteria (chapters 110 and 204, both dated 1 March 2022), wbdg.org | Numeric 1, 2, 3 with the legend "1. High, 2. Moderate, 3. Minimal" | A "Functional Relationship Matrix" from the department to other services (external relations), followed by functional diagrams; internal relations are written as prose: "shall be located adjacent", "close to", "nearby, but not adjacent", "directly adjacent to or very close to" | P |
| Australasian Health Facility Guidelines, Part B, HPU 0190 (Revision 7.0, August 2022), via a third-party copy (the official S3 copy refused the script) | Graded wording: "direct horizontal or vertical adjacency", "ready access", "easy access" | External relations by those grades; internal relations as requirements: physical separation of clean and dirty, unidirectional workflow, access control, separate entries for soiled goods, staff and clean exit | P (text of the guideline, copy not the publisher's host) |
| WBDG Architectural Programming (part A1) | None stated | The relationship or bubble diagram shows functions that should be near each other, and can show circulation links and security or acoustic privacy needs | P |
| RIBA Plan of Work 2020 (part A2) | None | "adjacency requirements" and "room adjacencies" as part of the brief, to be settled before Stage 3 | P |
| GSA P100 2024 Submittal Matrix (part A3) | None | "All major spaces are identified with appropriate adjacencies"; concept submittal shows adjacency and functional requirements are met | P |
| Owner's pages: essential / desirable / neutral / undesirable | Four grades | Not traced to a published standard in this search; it is a common office-practice form (U) | U |
| UK Health Building Notes; FGI Guidelines | Not reached in this pass | | open |

Findings:

1. **There is no single standard scale.** Practice uses at least three forms: Muther's six letters (with a
   "keep apart" grade, X), VA's three numeric grades of positive relation, and graded prose (adjacent, ready access,
   easy access). All have positive grades of decreasing strength; Muther's and the owner's include a negative grade;
   VA's matrix has none (separation is written in prose) (P). A tool should therefore store a **grade on an ordered
   scale with a named scale**, not a fixed enum (inference, high confidence).
2. **The kind of relation recurs separately from its strength** (P across the sources): proximity or adjacency;
   **direct access** (a door or a direct route: AusHFG "direct ... adjacency", VA "directly adjacent"); **horizontal
   or vertical** (AusHFG); **visual** link or supervision (not found in the texts read here: open); **acoustic**
   privacy (WBDG); **security** and access control (WBDG, AusHFG); **separation** of flows (clean and dirty,
   AusHFG; Muther's X); **sequence** or one-way flow (AusHFG "unidirectional workflow"; Muther's flow of materials).
3. **A reason is recorded with the rating** in SLP practice (S/U for the codes): the matrix carries why, not only how
   much. VA and AusHFG give reasons as prose next to the matrix (P).
4. **External and internal relations are kept apart** in health planning (VA, AusHFG: department to other services
   versus room to room inside the department) (P). For a programme tool: relations between departments (zones) and
   between rooms are both needed.

### F. Options appraisal and decision records (H6)

Read 2026-11-16.

**F1. RIBA Plan of Work 2020 Overview (P).** Stage 2 has regular Design Reviews with the client and stakeholders.
The **Stage Report** "records all of the relevant decision making during the stage": what decisions were made,
"why they were made and who was party to them, recording what options that were examined and why one was chosen
over another"; when sign-off includes a formal Design Review, it records the comments made and the design team's
responses. Stage 1 options "should not be vetted and appraised"; appraisal starts at Stage 2. After Stage 2, changes
go through Change Control Procedures.

**F2. GSA P100 2024 (P).** Three or more distinctly different schemes, with narrative "to allow comparison and
selection of a design direction"; the matrix asks to "highlight relative merits or challenges" of the concepts and to
compare net, usable and gross area of each with the programme. Concept Design Reviews "verify that concept options
are compelling and viable from the perspectives of siting, design, programming, engineering systems, performance,
budget, and schedule" and "document how design choices may affect building functionality"; comments must be
addressed before the next review, and outstanding ones are listed on a readiness checklist. So the record has:
options, criteria (seven named perspectives), comments, responses, open items.

**F3. HM Treasury, The Green Book (P).** The copy reached at the 2022 "updated links" address is now the **2026
edition** (Crown copyright 2026, Open Government Licence v3.0). Summary level:
- Longlist: generate a wide variety of options; define SMART objectives and **critical success factors**; assess the
  longlist against them; an option that does not meet the objectives is not taken forward, except **business as
  usual**, always kept as the benchmark. The shortlist holds BAU, a do minimum, a **preferred way forward**, a more
  ambitious and a less ambitious version of it, and optionally options with different design choices that still meet
  the critical success factors.
- The **options framework filter**: five categories (scope, solution, delivery, implementation, funding), option choices per category, each
  choice rated against the critical success factors: red (discarded), amber, green (best); options are combinations
  of amber and green choices. Structured facilitated workshops and "explicit deliberation": participants explain the
  evidence and assumptions behind each judgement.
- Shortlist: social cost-benefit analysis (recommended) or cost-effectiveness analysis; rank by summary metrics,
  but the ranking "is not sufficient to make a decision": a balanced judgement also weighs unmonetisable effects,
  risks, public cost and distribution. Results go in an **appraisal summary table**.
- Weighting: multi-criteria decision analysis (MCDA, with swing weighting and an expert facilitator) is allowed at
  the longlist stage; the Green Book **"recommends against the use of multi-criteria analysis (MCA)"**, simple
  "weighting and scoring" that "lacks an objective basis and can reduce transparency".

**F4. Choosing by Advantages against weighted scores.** Arroyo, Tommelein and Ballard, "Comparing Weighting Rating and
Calculating vs. Choosing By Advantages to Make Design Choices", Proceedings IGLC-22, Oslo, **June 2014** (not 2015),
pp. 401-412, read in full from iglc.net (P). One case study (the structural system of a campus building, two
alternatives, 11 factors): both methods chose the same alternative. CBA's vocabulary as the paper applies it:
**factors**, **criteria** per factor ("must" or "want"), **attributes** of each alternative, **advantages** (the
difference between an alternative's attribute and the least preferred one), and **importance of advantages** (IofA),
anchored on the paramount advantage; **cost is kept out of the factors** and judged afterwards against the total
importance. What the authors say goes wrong with weighted rating and calculating (WRC):
1. it assumes every increment of performance inside a factor is equally valuable;
2. it may assume linear trade-offs between factors;
3. it does not focus on the differences between alternatives;
4. it mixes cost with value (cost counted as one more factor);
5. rank order can change when an irrelevant (non-differentiating) factor is removed, when weights must sum to a fixed
   total;
6. it asks people to agree on the importance of abstract factors before looking at the facts, which invites
   "premature argument about value judgments".
They also say no method is entirely objective and more research is needed. Suhr's 1999 book (*The Choosing By
Advantages Decisionmaking System*, Quorum) was not read: it is sold; the paper is the secondary source (S for CBA's
definitions).

Findings for H6 (inference, medium-high confidence):
- What practice asks of an options comparison is **records**: the options (at least three distinct, GSA; a BAU or do
  minimum benchmark, Green Book), the criteria or critical success factors with must-have gates, each option's
  measured attributes (area against programme, net-to-gross, circulation ratio, adjacency met: RAIC and GSA, part A),
  reviewers' comments and responses, the decision, who made it, why, and what was rejected and why (RIBA Stage
  Report). None of these sources asks for a search or optimisation engine.
- Two of the sources warn against a single weighted score (Green Book 2026, Arroyo et al. 2014). A comparison view
  that shows the differences per criterion, keeps cost separate, and asks the team to record the importance of each
  advantage is closer to practice than an automatic total.

## 4. What bears on H5 and H6

(pending)

## 5. What a programme and relationship data model should carry (inference)

(pending)

## 6. Counter-evidence

(pending)

## 7. Still open

(pending)

## 8. Search log

(pending)

## 9. References

(pending)
