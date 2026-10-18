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
  Delaware). ICC's adoption chart says it is informational only. What applies is the adopted edition
  with its amendments, at the project's place and date, not the newest one published.
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

Still not read at the source: IDS's adoption as a standard on 1 June 2024 (buildingsmart.org
refused), Eastman and others' four stages (mediatum.ub.tum.de refused), ICC's adoption chart
(iccsafe.org refused). They stay U and shape nothing in the code.

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
