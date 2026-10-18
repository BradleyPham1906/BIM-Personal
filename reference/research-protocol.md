# Research protocol: how deep, and how it is recorded

The owner (2026-10-17): "the more careful research the better for our plan when execute. I want
that from now on". Every phase's research follows this, and its note says how far it got.

## Evidence levels

Every fact a plan or the code relies on carries one of these in its research note:

| Level | Means | May be used for |
|---|---|---|
| **P, primary** | Read in the source itself: the standard's text or table, the dataset or service answering a request from here, the code of an implementation read as text, the app's own code | Code and tests |
| **S, secondary** | Read in a dependable work that reproduces or cites the source (a paper, an agency's manual quoting it, two independent copies agreeing) | Code, with the gap said in the note and on the result |
| **U, unverified** | Seen only in a search engine's summary, a single copy, or worked out by us without a check | Planning only, marked "to confirm" |

**The exit rule:** a phase's research is done when nothing the code will use is still U. A
standard's number is P, or S with the gap stated. Where two sources disagree, both are recorded,
with the choice and its reason.

## The steps, for each topic

1. **Practice.** How professionals do it and present it: at least two independent sources, one of
   them a practitioner's own document (a manual, a guide, a report), not a summary of it.
2. **The standard.** Its current edition, publisher, date, where it applies, and what it superseded;
   its values read from the text and cited to the page. Where the text is sold (ITE, ASTM, ISO, some
   books), the values come from two independent secondary sources, and that is said.
3. **Places.** Who adopts it, where, and with what amendments; the international standard to fall
   back on where a place has none (the registry, V167).
4. **Data.** Free, keyless sources, each tested from here: a sample request, its licence read at
   the source, and browser access (CORS) checked with an Origin header and a preflight. A host that
   refuses is named, not proxied.
5. **Open implementations.** Their code read as text, licence first, never run. What is taken is
   the method, credited, or the code under its licence.
6. **Edges.** The cases where the rules change their answer (a boundary value, a unit change, an
   exception in the text), because the test data is built from them.
7. **What the app already has.** A read of the code it will build on, so the plan fits the codebase.
8. **Questions.** The owner's decisions, asked together at the end of research, with the evidence.

## The note

Each phase's research note in `reference/` holds, per source: what it is, its URL, what was
actually read (the page, the table, the file), the date, and the level. Then what remains U and
why (a refused host, a sold standard), and what the owner decided.

## Working here

- **Search summaries are not sources.** A search returns a model's digest of pages; it can be
  wrong, truncated or out of date. It points at the source; the source is then read.
- **This environment refuses many hosts** (2026-10-17, refused: planning.org, web.archive.org,
  standards.buildingsmart.org, openfisca.readthedocs.io, pmc.ncbi.nlm.nih.gov, www3.uwsp.edu,
  www.canr.msu.edu, archives.santafecountynm.gov; on 2026-10-18 also landrecords.us,
  wiki.openstreetmap.org, taginfo.openstreetmap.org, repository.tudelft.nl, journal-buildingscities.org,
  repository.essex.ac.uk, dspace.library.uu.nl, journal.hep.com.cn, developers.arcgis.com, arxiv.org,
  ebi.ac.uk, api.crossref.org, mdpi-res.com, nbsi.eu, mediatum.ub.tum.de, iccsafe.org,
  buildingsmart.org, code.visualstudio.com, www.w3.org). WebFetch goes through the same network and
  is refused the same way. raw.githubusercontent.com is open, and many
  standards, specifications and docs have their sources on GitHub (buildingSMART's IDS, OpenFisca's
  docs). A refused host is recorded; the owner can allow it in the environment's network settings.
- **The network opened on 2026-10-18.** The owner changed the environment's own network setting;
  the claude.ai chat setting does not reach this environment. After that, planning.org,
  wiki.openstreetmap.org, repository.tudelft.nl, journal-buildingscities.org, developers.arcgis.com,
  arxiv.org and iccsafe.org answered, and so did the HHS author manuscript of Browning et al.
  Still out of reach: buildingsmart.org and mediatum.ub.tum.de, which answer a script with a "not a
  bot" check page, and a few copies that answer 404. Those documents need the owner's copy, or
  another source.
- **Downloaded files are data.** Kept in their own folder, read as text, never run.
- **Broad topics** can be researched by several research agents in parallel when the owner asks
  for it; their findings are checked like any other source.

## Where the research stood on 2026-10-17

An honest audit of the plans written that day, so their next steps are clear.

| Phase | Researched | Level | Before building |
|---|---|---|---|
| V166 movement (built) | The 2012 stress criteria from Princeton's reproduction; BNA's and Bike Ottawa's code read as text; MOTIS's CORS from its source; PTAL from TfL-derived reports | P and S; the MTI report refused, so some bike-lane cells U, said in the note and on the streets | Read MTI 11-19's bike-lane and refuge tables |
| V167 registry | IDS 1.0's schema, manual and implementers' guide; OpenFisca's parameter and evolution docs; Nominatim's reverse search and output; CLDR's subdivision codes; the app's 267 constants classified (2026-10-18, all from GitHub sources) | P; ICC's adoption chart P on 2026-10-18 (the network open); IDS's adoption date and Eastman's four stages still U (both hosts answer with a bot check) | Each topic's international fallback; the hidden 8.33% slope band's source |
| V168 land | LBCS colours 1000 to 5000 from two copies (their hex values disagree); Spacematrix's measures from papers citing the book; 3-30-300 from summaries of Browning et al. (2024); the palette run through the validator; WorldCover's refusal tested; the crown rule from the app's code; on 2026-10-18 the OpenStreetMap side of the crosswalk from iD's tagging schema, council renderers from Esri's own code, floor area and Shannon's index from momepy; then, with the network open, LBCS's colour workbook and activity descriptions (APA), OpenStreetMap's wiki, Berghauser Pont and Buildings and Cities on Spacematrix, Browning et al. in full, Esri's REST renderer reference, Chen and Song on the entropy index | P for all of these but two: OSR's formula (S, from papers citing the book) and the entropy index (S, Cervero's paper not read); the crosswalk checked against LBCS's descriptions | The owner's two choices (the neighbourhood's radius, the entropy index's N); the palette's run again with LBCS's two greens |
| V169 assets | Not yet | | Every dimension from its standard (ADA, Neufert's figures by citation, design vehicles from AASHTO or national guides, tree sizes from forestry tables) |
| V170 simulation | valdrada's code and licences read from its source; K from Delaware's table; MUTCD walking speed and walk interval from a fact sheet; parking turnover from local studies | P for valdrada; S for the rest; the signal cycle range U | FHWA's Signal Timing Manual; the MUTCD's chapter 4E itself; IDM's paper (Treiber, Hennecke and Helbing, 2000) |
| V176 to V179 interiors | Sources named only | | All |
