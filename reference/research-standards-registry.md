# Research: standards as data, a registry the app reads (2026-10-17)

The owner: "what i want is building a system based on the industry standards (but flexible enough
when the standards changed)". This note is how the industry keeps rules apart from software, what
this app does today, and a design for a registry every analysis and check reads.

## How the industry does it

- **buildingSMART's IDS (Information Delivery Specification)**, an official standard since 1 June
  2024: requirements written as data (XML against a published schema), each a specification with
  an applicability part (which objects) and a requirements part (the conditions they must meet),
  both made of facets (entity, attribute, property, classification, material, part of). A checker
  reports applicable and passed, applicable and failed, and not applicable; a missing property is
  not a pass. IfcTester (IfcOpenShell) is a reference implementation.
  https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specifications-ids/
- **Automated code checking** has four stages (Eastman and others, 2009): interpreting the rule
  into a machine-readable form, preparing the model, executing the check, reporting. Interpreting is
  the hard part: rules are implicit and sometimes contradictory, and someone has to make them
  explicit. More than 400 research works over four decades; Solibri's parameterised rulesets are the
  commercial example. https://mediatum.ub.tum.de/doc/1455602/document.pdf
- **Codes are adopted, not just published.** A building code edition applies where a state or a
  city adopts it, often with amendments, on its own schedule. Some states skip an edition (Oklahoma
  adopted the 2024 IBC and expressly not the 2021), some leave adoption to each city (Colorado,
  Delaware). ICC's adoption chart says not every jurisdiction tells ICC what it adopts, and sends the
  reader to the jurisdiction for its amendments (read 2026-10-18, below). What applies is the
  adopted edition with its amendments, at the project's place and date, not the newest one
  published.
  https://www.iccsafe.org/wp-content/uploads/Master-I-Code-Adoption-Chart-FEB-22.pdf
- **Rules as code** (OpenFisca, the French government's open platform, 2011): every parameter value
  is stored under the date it takes effect, with a reference to its source text, so a change is a new
  dated entry and any date can be computed; when a rule changes its structure, not just a number, a
  new formula is dated from when it applies.
  https://openfisca.readthedocs.io/en/latest/coding-the-legislation/40_legislation_evolutions.html

## What the app does today

- About 90 constants in the site analysis modules carry standards or assumptions, each with its
  citation in a comment beside it: the 2012 stress criteria and the 2016 crossing table (BIM_MV_*),
  PTAL's walk limits, reliability allowances and bands, FHWA's road classes and typical traffic
  (BIM_DG_ROADS), CRTN and ISO 9613-2 for noise, FEMA's zone classes, LEED ND's intersection
  thresholds (BIM_ACC_LEED), the walk at 80 m a minute (BIM_ACC_SPEED), the slope classes and pond
  thresholds (BIM_LAND_*), the Census Bureau's margin-of-error formulas.
- A finding or a layer says its method and source in words, but records neither the edition nor the
  values it used. A revised standard means editing code, and every saved result would change
  silently at its next run.
- Jurisdictions are mixed: US sources (FHWA, FEMA, the ACS, LEED ND) beside British ones (CRTN, PTAL,
  the design guides' 400 and 800 m), each applied wherever the site is.

## The design: a registry

1. **A standard is a record, not code:**
   - its id, name, publisher and edition;
   - when it was published and when it takes effect;
   - where it applies;
   - its status (current, superseded, draft) and what it supersedes;
   - its source, cited to the page;
   - a licence note: numbers and facts, in our own words, never the standard's text;
   - its parameters, each a value with its unit and meaning;
   - its tables, with their row and column labels;
   - the method version that implements it.
2. **One reader.** Every analysis reads its numbers through one function (`bimStd(topic, name)`),
   never a literal: the app's law of one reader per relationship. A suite asks that no standard's
   value is left in code outside the registry.
3. **Profiles by place.** A profile says which edition applies for each topic: for example US
   federal with Pennsylvania's adoptions, or the UK with London's. The project's profile follows the
   site's location by default and can be chosen; a topic with no edition for the place says so
   rather than borrowing another country's.
4. **Overrides, recorded.** A project may change a value for one topic (a city's own walk limit,
   a local amendment), with its reason; every result that used it says "overridden" and shows both.
5. **Provenance on every result.** Each layer and finding records the standards, editions and a
   hash of the values it used. When a profile, an edition or an override changes, the results that
   used it say Out of date (as V148's result layers do), and running again shows what changed.
6. **New editions as data.** A revision is a new record that supersedes the old one, shipped with an
   app version or loaded as a standards pack (a file), with the differences between the editions
   shown before it is applied. Saved results never change without a run.
7. **Methods, versioned.** When a revision changes a method's structure (Furth's 2017 stress tables
   add daily traffic), the code gains a method version, chosen by the edition in force: OpenFisca's
   dated formulas.
8. **Checks as IDS.** The model checks the interiors will need (clearances, door widths) are written
   as specifications in IDS's shape (applicability and requirements), so they can be read from and
   written to IDS files when buildingSMART's format is wanted.
9. **Tested from the source.** Each record's values are checked against its source by a reference
   suite, each method version against the Python references (as V164 to V166's are), and a variant
   per record proves the suites read the registry, not a copy.

## The owner's decisions (2026-10-17)

1. Built now, as V167, before the next analyses.
2. Any country, with fallbacks: profiles as a tree, the most specific edition winning, an
   international standard where a place has none, and where there is none either, said so.
3. Overrides per project, with a reason, shown on every result that used them.
4. New editions with app versions and as standards pack files.

## What it costs

A registry phase before the next analyses: the record format, the reader, profiles by place,
overrides, provenance and Out of date, Properties > Standards, and V164 to V166's constants moved
into records with their citations (the suites unchanged in what they expect, which proves the move).
Then every later phase adds records instead of constants.

## Read at the source (2026-10-18)

Done to `research-protocol.md` while V166b's checks ran. Every source below was read as text from
its own repository on GitHub (`raw.githubusercontent.com`); the published pages are refused here.

| Source | What was read | Level |
|---|---|---|
| buildingSMART, IDS: `README.md`, `Schema/ids.xsd`, the user manual's `README`, `specifications`, `restrictions`, `ids-metadata`, and the implementers' `developer-guide` (repository `buildingSMART/IDS`, branch `development`) | The structure (below), cardinality, restrictions, metadata, the checker's duties, float precision, the limits of version 1, the licence | P |
| OpenFisca, `legislation_parameters.md` and `40_legislation_evolutions.md` (repository `openfisca/openfisca-doc`) | The parameter tree, dated values, references and units, scales, indexed nodes, dated formulas, the licence | P |
| Nominatim, `docs/api/Output.md` and `docs/api/Reverse.md` (repository `osm-search/Nominatim`) | `country_code` and `ISO3166-2-lvl<n>` in `addressdetails`; the reverse search's zoom levels | P |
| Unicode CLDR, `common/validity/subdivision.xml` (repository `unicode-org/cldr`) | 5,027 regular subdivision codes, in CLDR's lower-case form (`uspa` for US-PA); Unicode-3.0 licence | P |
| The app's own code | Every `BIM_` constant (267), classified: `research-standards-inventory.md` | P |

After the owner opened the network the same day, ICC's chart was read too (below). Still not read
at the source: IDS's adoption as a standard on 1 June 2024 and Eastman and others' four stages. The
open network reaches buildingsmart.org and mediatum.ub.tum.de, but both answer a script with a
"not a bot" check page instead of the document. They stay U and shape nothing in the code.

### What ICC's adoption chart says (read 2026-10-18)

"International Codes - Adoption by State (FEB 2022)", ICC's PDF, read as text with each cell's
position:
- A row per state and territory, a column per code (IBC, IRC, IFC, IMC, IPC, IPSDC, IFGC, IgCC,
  IECC residential and commercial, IPMC, IEBC, ISPSC, ICCPC, IWUIC, IZC, ICC 700).
- **A number** is the edition adopted as a mandatory state minimum (15 = 2015).
- **X:** one or more state or local agencies adopted an edition, but not as the standard for all
  buildings.
- **Blank:** no state or local jurisdiction in the state adopted it.
- Pennsylvania's IBC cell reads 15: the 2015 edition was its state minimum in February 2022.
- ICC's own caveats: not all jurisdictions notify ICC, and amendments are to be had from each
  jurisdiction.

For the registry, this has three consequences:
- An edition is a fact about a place and a date, as the design assumed.
- An X means the state has no single answer, so the city decides: the profile tree goes down to
  the city there.
- The chart is a pointer, never the record. A profile's edition cites the jurisdiction's adopting
  act, and the chart may be cited only as the place it was found (S).

### What IDS is, from its schema and manual

- An `.ids` file: `info` (title required; copyright, version, description, author, date, purpose,
  milestone optional) and `specifications`.
- A specification: a `name` and the `ifcVersion` it applies to (IFC2X3, IFC4, IFC4X3_ADD2), both
  required; an optional identifier, description and instructions; `applicability` and optional
  `requirements`, each made of facets: entity (IFC class and predefined type), attribute, property
  (property set, name, value, data type), classification (system, value), material, partOf (an entity
  and a relation).
- Cardinality: of a specification (required: at least one match must exist; optional; prohibited)
  and of each requirement facet (required, optional, prohibited). Only those three minOccurs and
  maxOccurs pairs are allowed.
- A value is a simple value or a restriction: an enumeration, a pattern (XML Schema's regular
  expressions), bounds (inclusive or exclusive), a length. Total and fraction digits are not
  supported.
- **Version 1's limits, in its own words:** no geometry checks, no checks on calculated values, no
  checks against data outside the model. "Walls 3 m from the site boundary" and "the total area of
  offices over 300 m2" are given as examples of what it cannot check.
- A checker must pass buildingSMART's test suite of IFC and IDS pairs
  (`Documentation/ImplementersDocumentation/TestCases`). A float equals x if it lies strictly
  between `x(1 - 1e-6) - 1e-6` and `x(1 + 1e-6) + 1e-6`. An author must write valid files only,
  with no extensions of its own and nothing lost on a round trip.
- Licence: **CC BY-ND 4.0** (attribution, no derivatives). The format can be
  implemented; the schema and the test cases may be used as they are, credited, but not changed.

### What OpenFisca's parameters are

- A tree of nodes, each parameter a file or a node in one, named in lower case with underscores.
- `values` keyed by the date each takes effect; undefined before the first; any date resolves to the
  latest value at or before it. A value may carry its own `reference`; `expected` marks one
  announced but not yet in force. `metadata` holds the unit and the reference.
- Scales: brackets, each with a dated threshold and a dated rate or amount (marginal or single).
- Indexed nodes: a node whose children share one shape can be read by a key at run time (its example
  is a benefit by zone).
- A structural change is a new formula dated from when it applies; the older one stays in force
  up to that date.
- Licence: the documentation is AGPL-3.0. Its ideas are used here, not its text or code.

### Where a site is, without a key

Nominatim's reverse search with `addressdetails=1` returns the country (`country_code`, lower-case
ISO 3166-1) and the region (`ISO3166-2-lvl4`, for example `US-PA`, `GB-ENG`, `DE-BY`). At
`zoom=10` it also names the city. One reverse request per site, inside the usage policy V132
already keeps (one request a second, the app's own Referer), gives the whole path of the profile
tree. The app keeps none of these today (no `country_code` in the build): V132's address search
reads the place's latitude and longitude only. Offline, or where Nominatim answers nothing, the
owner picks the profile. CLDR's list says which region codes exist.

### What the reading changes in the design

1. **Checks: IDS for what it can check, the registry for the rest.** Property and attribute
   requirements (a door's width as an attribute, a fire rating) are written in IDS's shape and can
   go out as IDS. Clearances, distances, slopes and areas are geometry or calculation, which IDS 1
   cannot check: they stay the registry's own rules, with the same three outcomes.
2. **Records take OpenFisca's shape.** A parameter's values are dated, each with its reference; a
   band table (PTAL's bands, the noise and slope classes) is a scale; a table keyed by class (the
   roads by class, the crossing table by speed and lanes) is an indexed node. An edition in force
   is the value at the project's date.
3. **Methods dated.** A method version is chosen by the date in force, as OpenFisca's formulas are:
   the 2012 stress criteria until a profile takes a later edition.
4. **The place path from one request.** Country, region and city from Nominatim's reverse search,
   kept with the site, shown and changeable in Properties.
5. **Values in words.** The analyses say their numbers in sentences too ("8 minutes to a bus, 12 to
   rail", "4.8 km/h (80 m a minute)", "CRTN holds to 300 m"). Moving the constants alone would leave
   those sentences wrong after an override. The registry gives each record a sentence built from
   its values, and the "no literal left" suite looks for a record's values beside their units in the
   strings as well as in the code.
6. **Hidden standards.** The audit found a standard with no citation: the terrain's slope bands
   include 8.33% (1:12, logged that way in V144), which reads as the US accessibility ramp limit. It
   is U until its source is read, and V167 records it as such.

## As built in V167 (2026-10-18)

The owner's four answers of 2026-10-18, all the recommended options:
1. A method applied outside its place (PTAL outside London, CRTN outside the UK, LEED ND and FHWA's
   classes outside the US) still runs, and says "applied outside its place", with where it is in force.
2. Only the assumptions the analyses use become overridable records now: the roads, the context's
   sizes, the climate's base and bands, the walking speed, the slope classes, the terrain's bands.
   The roofs, the survey tolerances and the usages' defaults move later.
3. The US catalogue is read at its sources and listed in Properties > Site > Standards as "In force
   here, not applied by the app yet".
4. Packs show their SHA-256 and the publisher they name, with every difference first, then Apply or
   Cancel. They are marked unsigned.

### The records and where each was read

Every value below was read in its source on 2026-10-17 or 2026-10-18, as text, from a copy in its own
folder; nothing was run.

| Topic | Edition | Read in | Level |
|---|---|---|---|
| `tfl.ptal` | Assessing transport connectivity in London (2015) | TfL's PDF, 2.5 and Table 2.2: 640 m and 960 m at 4.8 km/h, reliability 2 and 0.75 minutes, the bands. The tram walk is not given: rail's is taken (A). Adopted in the City and the 32 boroughs (ISO 3166-2:GB) | P |
| `walk.speed` | The app's, TfL's figure | The same, 2.5: 4.8 km/h, 80 m a minute | P |
| `guides.walk` | Manual for Streets (2007), with North Norfolk's guide | Manual for Streets 4.4.1 (800 m); North Norfolk's 800 m to a school and 400 m to green space from V166's reading, its page since moved | P, S |
| `leed.nd` | LEED v4 ND (updated 2 July 2018) | USGBC's rating system, Connected and Open Community: 400 m, Cases 1 and 2 (90, 140), Table 1 (300 to 400, over 400). Read in the copy GBC Brasil hosts; USGBC's own needs a login | P |
| `fhwa.fc` | Highway Functional Classification, 2023 Edition | Tables 3-5 and 3-6, the AADT ranges by class, rural and urban | P |
| `crtn` | Calculation of Road Traffic Noise (1988) | Its 300 m range, as DataKustik's CadnaA documentation gives it: the memorandum could not be read here | S |
| `lts.2012`, `lts.xing2016` | MTI 11-19 (2012); TRR 2587 (2016) | Princeton's reproduction of the tables: the reports refused | S |
| `who.aqg` | WHO global air quality guidelines (2021) | Table 0.1: PM2.5 annual 5, 24-hour 15; interim targets 35 (annual), 75, 50, 37.5 and 25 (24-hour) | P |
| `who.noise` | Environmental Noise Guidelines for the European Region (2018) | 3.1, road traffic: 53 dB Lden (53.3 rounded), 45 dB Lnight, both strong recommendations. Guidance for the region, adopted nowhere as a rule, so applied outside its place everywhere | P |
| `fema.zones` | 44 CFR 64.3 | eCFR, current to 2026-10-01: the zone symbols | P |
| `land.slope`, `terrain.slope_bands` | The app's | The slope classes are the app's working set (A). The terrain's 2%, 5% and 8.33% are the 2010 ADA Standards' 1:48, 1:20 and 1:12 (403.3, 405.2), read on ada.gov: the hidden 8.33% is P now | A, P |
| `ibc.occupant_load` | IBC 2021 and 2018, Table 1004.5 | The table as V105 read it; 2021 adopted in Pennsylvania from 1 January 2026 by 34 Pa. Code 403.21, read in the Pennsylvania Code | S (the table), P (the adoption) |
| `asce7.combos` | ASCE/SEI 7-22, 2.3.1 | Combinations 1 and 2 as V125 recorded them; ASCE's page names 7-22 current. Its adoption by place is not recorded | S |
| `app.roads`, `app.context`, `app.climate` | The app's | Its own research notes (V133, V157, V159, V164) | A |
| The catalogue | Pennsylvania's UCC (2021 I-Codes from 1 January 2026), the IBC 2021 and 2024, the 2010 ADA Standards, ICC A117.1-2026 (announced), ASHRAE 90.1-2025, the MUTCD 11th Edition with Revision 1, the Green Book's 7th Edition, AASHTO LRFD's 10th and 8th (DM-4 adopts the 8th), PennDOT's DM-4 (December 2019, with its strike-off letters), ASCE/SEI 7-22 with three supplements, FAA AC 150/5300-13B Change 1 | Each at its publisher's page or the adopting act, the date read on each record | P; the IBC 2024 as current S (inferred from ICC's note on A117.1-2026) |
| Not read | ACI 318, AISC 360, PennDOT's DM-2 | concrete.org and aisc.org refuse scripts; PennDOT's publications host did not answer (2026-10-17 and 2026-10-18), and a search summary's "Change No. 11" is not a source | U, listed without values or adoption |

### What the build does

- **The record:** a topic (its title, publisher, kind, area, what uses it, whether it applies anywhere)
  and its editions, each with its published date, status, where it is in force (place key, from, to),
  its source (title, section, link, level, date read), the method that implements it, and its values
  (a number with its unit and words, or a table), each with the source's own phrase and level where it
  differs. 32 topics: 18 applied, 14 in the catalogue; 35 editions (21 read at their source, 7 from a
  secondary source, 4 the app's, 3 not read); 81 values the analyses read (72 numbers, 9 tables).
- **One reader,** `bimStd(topic, name)`: the project's override, or the value of the edition in force.
  Every analysis reads through it or through an accessor in the shape its code had (V164 to V166's
  constants are gone, and the suite asks that none is back). Reading writes nothing to the project.
- **The place:** from the address search's own answer (`addressdetails=1` on the forward search, so no
  second request): the country, ISO 3166-2's region and districts (lvl4, lvl6, lvl8) and the city. The
  path is the city, the districts, the region, the country, then international. The edition in force is
  the one adopted most specifically, on the project's date (today, or a date given), the latest adopted
  where two are; where none is, a topic that applies anywhere takes the newest edition published by
  then, and says "applied outside its place".
- **Profiles** are the editions' adoptions: there is no separate profile object to keep in step.
- **Methods** are named on the editions (`ptal.2015`, `lts.2012`, `crtn.1988`, `fc.midpoint`,
  `fema.nfhl.1`). Each has one implementation; a second version brings the dispatch.
- **Overrides** need a reason, a number, more than zero (a percentage may be zero, a temperature
  anything), and the order of ordered values; a table changes only with a pack. Each is one undo step.
- **Provenance:** a stamp is the topic, the edition, how it applies, the overrides and a hash of the
  values. A stamp may name one value (`leed.nd|radius`), so a threshold applied as a result is drawn
  does not make the data out of date. Runs keep a stamp; so do the access data (the walking speed,
  LEED's radius), the site context (its sizes), the climate (its base, calm and bands, and the values
  themselves, which its findings and board state) and the air quality (WHO's levels). Results from
  before V167 are taken as worked out with the editions' own values. A change works the findings out
  again from the data kept, in the same undo step; a row or finding whose data was worked out with
  other values says so, and that Analyze site fetches it again.
- **Packs:** `bim-standards-pack`, version 1, up to 1 MB, its SHA-256 (the app's own, checked against
  Python's) and its publisher shown with every difference before Apply. A pack never changes an edition
  already in the registry, and an edition of a topic the app applies must carry every value the app
  reads, of the same kind. Packs are unsigned; no export yet.

### What stays in code, and why

Classes as `research-standards-inventory.md` gives them:
- **Methods' own parameters (M):** the 2012 stress criteria and the reach's 25% detour (`lts.2012`),
  ISO 9613-2's 20 dB cap on screening and CRTN's L10 to Lden step (the noise method), PTAL's half
  headway, 30 over the access time, and the best line in full and the rest at half.
- **Definitions (C):** FEMA's 1% and 0.2% annual chance, the Koppen-Geiger zones' names, the ACS's
  90% margins of error.
- **Display (D):** the noise bands' 5 dB steps from 55 dB, the walk bands of 5, 10 and 15 minutes, the
  board's 400 m and 800 m circles, the car parks' 400 m search.
- **Later (A):** the roofs' proportions, the survey tolerances and the usages' defaults (the owner's
  answer 2); AISC's shapes (V126), which need a record per edition of the shapes database.

### Found while building

- **The compass rings never kept their standard.** The analyses' list named them `compass`; their
  analysis is `frame`. Their run kept no stamp, and their row named nothing (167f).
- **Numbers worked out at fetch, said at today's values.** The degree days were summed at 18 degrees;
  with the base overridden to 20, the finding said "base 20". The climate and air data keep the values
  they were worked out with, and their findings and board say those (167f).
- **Findings fixed at Analyze time.** A finding's text is kept with the project, so a new LEED
  threshold or slope class reached no finding until Analyze site ran again. A change works them out
  again from the data (167f).
- **What was typed, lost.** Moving from the country field to the region's redrew Properties and emptied
  the first. The place's and an override's fields keep a draft until Save or Cancel (167g).
- **On a phone, nowhere to be seen.** STANDARDS opened the group in a closed sheet; it opens the sheet
  now, as COMMIT does (V151), and the date field is 36 px on touch, as V149 makes Properties' buttons
  (167f, 167g, 167h: 167f's own rule for the buttons repeated V149's, and went).
- **A pack's edition called the app's assumption,** and the same pack twice refused for the wrong
  reason (167g).
- **Seven numbers left in sentences,** found by the scan the design asked for: WHO's 53 dB, LEED's
  thresholds in the Access board's note, the comfort band twice on the climate board, "the WHO 2021
  guidelines", the relief finding's 15% and its classes, SLOPEMAP's description, and the context radius
  that must reach CRTN's range (167h).
- **A level overstated.** DM-2's entry rested on a search summary and said S; it is U now, with nothing
  claimed (167h).
- **LEED's second point** was taken at 400 and over; Table 1 gives it over 400 (167b).

### Not done

- Checks in IDS's shape: with the interiors (I2), where the clearances and widths are.
- A pack's export, and signed packs.
- The adoption window of the 2018 IBC in Pennsylvania, and ASCE 7's adoption by place: not read.
- CRTN and the stress tables at S; North Norfolk's page moved; ACI 318, AISC 360 and DM-2 unread.
- The roofs, the survey tolerances and the usages' defaults still in code (the owner's answer 2).
- The frame analysis's results are not stamped: they are not saved with the project.
- City-level records: the path reaches the city, but no record is adopted for one yet.
