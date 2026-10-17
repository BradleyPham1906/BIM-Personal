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
