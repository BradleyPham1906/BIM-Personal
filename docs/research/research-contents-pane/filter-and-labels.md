# V173 research: the layer filter language and labels

Part of the V173 contents-pane research (definition query and field labels for data and analysis
layers). This note covers the filter expression language and label placement only. Written
2026-11-07 to 2026-11-08 by a research agent; every source read on those dates.

Levels: P = the primary source read itself (standard text, code, the vendor's own manual page);
S = a dependable secondary source, gap said; U = a search summary only (never used for code).

## 1. Question and hypotheses

Question: which filter grammar should the app use so a user can type, or build from menus, a
filter such as `ZONE IN ('R1','R2') AND POP > 1000`, evaluated in ES5 with no `eval`, no
dependency, safely when the expression comes from a project file opened from elsewhere?

Hypotheses (each tested below):

- H1. The OGC CQL2 Text Basic plus Advanced Comparison subset is, for a definition query, the same
  language a user of ArcGIS types (SQL WHERE subset). Result: largely true; differences listed in 5.
- H2. A hand-written recursive-descent parser and evaluator for that subset fits in under 15 KB of
  ES5 and evaluates 10,000 features in well under 100 ms. Result: true (13.7 KB, 16 to 18 ms).
- H3. Building a JavaScript RegExp from a LIKE pattern is safe. Result: false (falsified, 7).
- H4. Open implementations avoid `eval`. Result: false for at least one (pygeofilter's native
  backend compiles to Python source and calls `eval`), true for MapLibre, cql2-rs and jsep.
- H5. Three-valued logic (NULL excludes a feature) is what the standards and ArcGIS do. Result:
  true for CQL2 and the ArcGIS documentation; MapLibre is two-valued.

## 2. Search log

| Date | Where | What | Outcome |
|---|---|---|---|
| 11-07 | docs.ogc.org/is/21-065r2/21-065r2.html | CQL2 standard, full HTML | read, P |
| 11-07 | raw.githubusercontent.com opengeospatial/cql2 (main, master) | BNF file, README | 404 both; GitHub API 403; the BNF annex in the standard used instead |
| 11-07 | raw.githubusercontent.com geopython/pygeofilter main | cql2_text/grammar.lark, backends/native/evaluate.py, LICENSE | read, P |
| 11-07 | raw.githubusercontent.com developmentseed/cql2-rs main | src/cql2.pest, src/expr.rs, LICENSE, Cargo.toml | read, P |
| 11-07 | raw.githubusercontent.com maplibre/maplibre-style-spec main | src/reference/v8.json, src/feature_filter/index.ts, LICENSE.txt, package.json | read, P |
| 11-07 | raw.githubusercontent.com mapbox/polylabel master | polylabel.js, LICENSE, package.json | read, P |
| 11-07 | raw.githubusercontent.com EricSmekens/jsep master | src/jsep.js, LICENSE | read, P |
| 11-07 | registry.npmjs.org | sql-where-parser, jsep, cql2-wasm, cql2-filters-parser metadata | read (metadata only, S for what the code does) |
| 11-07 | pro.arcgis.com (latest) | SQL reference for query expressions; definition queries; query builder intro; construct and modify queries; order of operations; specify text for labels | read, P |
| 11-07 | doc.arcgis.com ArcGIS Online | apply filters in Map Viewer | read, P |
| 11-07 | docs.qgis.org 3.40 | vector properties (Query Builder), expressions, functions list (operators), label settings | read, P |
| 11-07 | src/ of this app | `bimGeoCleanProps`, data-layers.js, any eval / new Function | read, P |

Counter-evidence searched for deliberately: an approved CQL2 rule that would let field names carry
spaces (none in the BNF, found only in cql2-rs); a published claim that `NOT IN` with a null item
behaves differently (none; our experiment confirms the SQL trap); a JS evaluator using `eval`
(pygeofilter's Python backend is the closest case).

Not reached: the ArcGIS query-builder clause operator names in Pro are in screenshots, not text
(the Map Viewer page names them in text: is, is not, includes, excludes, contains, in the last).
Esri's "Arcade" language reference was not read: labels here need only a field or concatenation.

## 3. Findings

### 3.1 OGC CQL2 (P, high confidence)

- Edition: OGC 21-065r2, "Common Query Language (CQL2)", version 1.0.0, OGC Standard (Interface),
  submitted 2024-03-26, approved 2024-05-23, published 2024-07-26; editors P. Vretanos and
  C. Portele. Free licence to implement, notice to be kept. URI `http://www.opengis.net/doc/IS/cql2/1.0`.
- Requirements classes: Basic CQL2 (AND, OR, NOT, =, <>, <, <=, >, >=, IS NULL); Advanced
  Comparison Operators (LIKE, BETWEEN, IN); Case-insensitive Comparison (CASEI); Accent-insensitive
  (ACCENTI); Basic Spatial, Spatial, Temporal, Array Functions; Property-Property Comparisons;
  Functions; Arithmetic Expressions; encodings CQL2 Text and CQL2 JSON.
- Basic CQL2 may restrict a comparison to property on the left, literal on the right (Permission 1);
  the Property-Property class lifts that.
- Grammar (annex BNF): `booleanExpression = booleanTerm {OR booleanTerm}`, `booleanTerm =
  booleanFactor {AND booleanFactor}`, `booleanFactor = [NOT] booleanPrimary`, primary is a
  predicate, a boolean literal, a function or a parenthesised expression. So precedence is
  NOT > AND > OR, left to right. Not equal is `<>` only (no `!=`).
- `isInListPredicate = scalarExpression [NOT] IN "(" inList ")"`, the list has at least one item.
  `isBetweenPredicate = numericExpression [NOT] BETWEEN numericExpression AND numericExpression`,
  inclusive (Req 6). `isNullPredicate = operand IS [NOT] NULL`.
- Keywords are case-insensitive (ABNF rule cited in 8.2). A property whose name is a keyword is
  written in double quotes.
- Identifiers: start with a letter, `_` or `:`, then letters, digits, `.`; the quoted form in the
  BNF is `"\"" identifier "\""`, so even quoted names cannot hold spaces under the strict BNF.
- Strings: single quotes; an embedded quote is `''` or `\'`; `\` is the escape character, with
  `\a \b \t \n \v \f \r` (Req 21).
- LIKE (Req 5): `%` any run of zero or more characters, `_` exactly one, escape `\`; NULL operand
  gives NULL. LIKE is case-sensitive unless both sides are wrapped in `CASEI(...)`, which must do
  full Unicode 15 case folding (Req 8); the standard advises applying it to both sides.
- Nulls: a predicate is TRUE, FALSE or NULL; AND/OR use the SQL truth table (FALSE AND NULL =
  FALSE, TRUE OR NULL = TRUE, otherwise NULL); NOT NULL = NULL. A missing property reads as NULL
  (Req 2B). An item is kept only when the whole filter is TRUE; FALSE or NULL drop it.
- Type casts (Permission 2): with incompatible types a server may error or cast; how is not
  prescribed (`'5' > 4` may error, compare as text or as numbers). So the app chooses and documents.
- Unicode normalisation NFD is recommended for string comparison (Rec 1).

### 3.2 ArcGIS SQL for definition queries (P, high confidence)

- Definition queries are one or more clauses in SQL (attribute clauses, at most one spatial
  clause); a layer may hold several named queries, at most one active; they limit drawing, the
  table, selection, labels and tools. Display filters only limit drawing.
- File-based data (shapefile, file geodatabase, CSV, feature services with standardised queries)
  uses the "ArcGIS SQL dialect", a subset; databases pass SQL to the RDBMS.
- Strings in single quotes, embedded quote doubled (`'Tim O''Brien'`). Strings are case-sensitive
  except on SQL Server; for insensitive use `UPPER(F) = 'X'`.
- LIKE with `%` and `_`, `ESCAPE 'c'` names an escape character. IN, BETWEEN (inclusive), IS [NOT]
  NULL, `<>`, arithmetic `+ - * /`, `||` concatenation, functions (UPPER, LOWER, LEFT, ROUND,
  CAST, EXTRACT, CURRENT_DATE).
- Nulls: the operator table states `<=` "will not return null values", `<>` and `NOT IN` "exclude
  fields with null values": the SQL three-valued behaviour.
- Decimal point is always `.`, never a comma, regardless of locale.
- Dates: `timestamp 'yyyy-mm-dd hh:mm:ss'` (file geodatabase), `date 'yyyy-mm-dd'` (shapefile).
- Precedence: AND before OR (order-of-operations page); grouping = parentheses; the builder has
  Group and Ungroup.
- Field names: the editor mode page says fields need not be delimited; how a name with a space is
  written is not stated for the file dialect (gap; QGIS and CQL2 use double quotes).
- Builder: designer mode (menus of field, operator, value, filtered by field type; Add Clause;
  grouping) and editor mode (SQL text, autocomplete, verify). Map Viewer's operators by name:
  is, is not, includes, excludes, contains, and for dates in the last / not in the last; a group
  matches "All of the following are true" or any.

### 3.3 QGIS, for contrast (P, high confidence)

- The provider filter (Query Builder) is a SQL-like WHERE passed to the data provider, so its
  syntax depends on the source (GeoPackage, PostgreSQL...).
- QGIS expressions: strings in single quotes, fields in double quotes (`"myfield"`) or bare;
  LIKE case-sensitive, ILIKE case-insensitive, both with `%`, `_`, `\` escape; `IS`/`IS NOT`
  compare values including NULL; most operators return NULL when an operand is NULL
  (`5 + NULL`, `'a' || NULL`); `concat()` treats NULL as empty.

### 3.4 MapLibre style specification filters (P, high confidence)

- Package `@maplibre/maplibre-style-spec` 26.5.1, BSD-3-Clause (MapLibre contributors, 2020).
- A filter is a JSON array expression: `["all", ["==", ["get","zone"], "R2"], [">", ["get","pop"], 1000]]`;
  `any`, `!`, `in`, `match`, `case`, `has`, `coalesce`, `to-number`.
- `==` is strictly typed: different runtime types are always unequal; `<` needs two strings or two
  numbers, otherwise an evaluation error. `get` returns null for a missing property. No LIKE; no
  three-valued logic (a feature passes when the result is `true`).
- Legacy filters `["==", key, value]`, `["in", key, v...]`, `["!in"...]`, `["has", key]`,
  `["none"...]` are converted to expressions by `convertFilter` (read in feature_filter/index.ts).
- Evaluation: the array is compiled into a tree of expression objects and run by `evaluate`; no
  `eval`. The JSON needs no parser but is not what a user types.

### 3.5 Open implementations (P unless said)

| Project | Licence | Language, size | Approach | Avoids eval? |
|---|---|---|---|---|
| pygeofilter (geopython) | MIT | Python, Lark grammar 8 KB | Lark LALR grammar; native backend turns the tree into Python source and calls `eval` | No (native backend) |
| cql2-rs (Development Seed) 0.6.1 | MIT | Rust, pest grammar 7 KB; npm `cql2-wasm` 0.5.6, 3.8 MB unpacked (S) | PEG; folds NULL with the CQL2 truth table; quoted identifiers allow any character with `""` | Yes |
| MapLibre style-spec | BSD-3 | TypeScript | JSON expression compiled to objects | Yes |
| jsep 1.6.0 | MIT | JS, 24.5 KB source, 390 KB unpacked package | precedence-climbing (stack) for binary operators, recursive descent otherwise; parses only, no evaluator; JavaScript syntax, not SQL | Yes |
| sql-where-parser 2.2.1 | MIT | JS (metadata only, S) | parses SQL-like WHERE to a tree | not read |
| cql2-filters-parser 0.9.14 | none stated on npm (S) | TypeScript | "browser-oriented CQL2" | not read; no licence = not reusable |

Reuse-first verdict: none fits the delivery contract as is. cql2-wasm is a 3.8 MB WASM build, not
ES5; jsep parses JavaScript, not SQL quoting or LIKE; pygeofilter is Python and uses eval;
MapLibre's evaluator is large and typed. The grammar is small enough that a narrow ES5 parser of
our own, checked against the CQL2 BNF and cql2-rs's behaviour, is the smaller risk.

### 3.6 The app's own data (P)

`bimGeoCleanProps` (src/js/engine/properties/map-address-site-data.js) keeps at most 40 properties
per feature, keys cut to 60 characters, values only null, number, boolean or string (500 chars);
objects become JSON text. So the filter sees only scalar types and keys may contain spaces or any
character. It assigns `o[key]` on a plain object: a key `__proto__` with a null value would set the
object's prototype instead of a property (an edge to fix when the filter reads `props`; read with
`Object.prototype.hasOwnProperty.call`, or build `o` with `Object.create(null)`). No `eval` or
`new Function` exists anywhere in `src/js` today.

## 4. Labels

### 4.1 ArcGIS (P)

- A label class has a label expression; the default field is the first string field whose name
  contains "Name", else the first string, integer, then any field.
- Simple expressions are one field, several fields, or fields with custom text (units). Advanced
  ones use Arcade, Python, VBScript or JScript. Field values are cast to text; NULL stays NULL.
  Arcade field syntax `$feature.NAME`, or `$feature['33field']` when the name has special
  characters or starts with a digit; Python/VB/JS use `[FIELD]`.
- Maplex options remove extra spaces and line breaks.

### 4.2 QGIS polygon placement (P)

Modes: Offset from centroid (visible or whole polygon, optionally forced inside), Around centroid
(prefers directly over it), Horizontal and Free (best position inside, furthest from edges),
Using perimeter, Outside polygons. Overlap: "Never overlap" (drop labels), "Allow overlaps if
required", "Allow overlaps without penalty"; priority ranks which label wins; layers can be
obstacles. Callout anchors include "pole of inaccessibility", point on surface and centroid.

### 4.3 polylabel (P, high confidence)

`mapbox/polylabel` 2.1.0, ISC licence (Mapbox), one dependency (tinyqueue, a priority queue).
Algorithm as read in polylabel.js:

1. Bounding box of the outer ring; cell size = min(width, height) (at least the precision).
2. Cover the box with square cells; each cell's value d = signed distance from its centre to the
   polygon outline (positive inside, ray-cast parity for inside), and potential max = d + h*sqrt(2)
   (h = half cell size): no point in the cell can be further from the edge than that.
3. First guesses: the area centroid (if inside), then the box centre; keep the best.
4. Priority queue by max; pop the most promising cell; stop when max - best <= precision;
   otherwise split into four and queue the children worth it.
5. Version 2 speed-ups: flattened coordinates, a bounding box per 32 edges to skip blocks, early
   exit once a cell cannot beat the best, children seeded with the parent's nearest segment.

Result: the interior point furthest from any edge (holes included) within `precision`; good for
L-shaped and U-shaped parcels where the centroid falls outside. In ES5 the core (without the
version 2 block skipping) is about 80 lines; a sorted array or a small binary heap replaces
tinyqueue. The licence allows reuse with the notice kept.

### 4.4 Collision (P for QGIS behaviour; algorithm S)

QGIS's "Never overlap" drops labels that would collide, ordered by priority. A simple greedy
version: sort candidates by priority (then by area or by label length), measure each label's
screen box, keep it if its box does not intersect any kept box (a grid of buckets makes the test
near constant time), otherwise drop it. The full engines (QGIS PAL, Maplex) search several
candidate positions per feature and optimise; that is beyond V173 and not read as code (gap).

## 5. Semantics edges, decided for the experiment

| Edge | CQL2 | ArcGIS | MapLibre | Sketch choice |
|---|---|---|---|---|
| `'O''Brien'` | `''` or `\'` | `''` | JSON string | both accepted; printer writes `''` |
| Field with spaces | not in BNF | not stated | any key | `"Land use"`, `""` inside (as cql2-rs) |
| Keyword as field | double quotes | n/a | n/a | double quotes |
| Missing / null field | NULL, excluded | NULL excluded | `get` gives null, `==` false | NULL, excluded |
| `x <> 1` with x null | NULL | excluded | true | NULL, excluded |
| `NOT IN ('a', NULL)` | NULL | excluded | n/a | NULL: everything excluded (the SQL trap, warn in UI) |
| `'10'` vs `9` | server's choice | depends on field type | unequal / error | numeric when the string is a whole number text |
| `'10' > '9'` | text order | text order | text order | false (text order), as written |
| LIKE case | sensitive; CASEI | sensitive (except SQL Server) | none | sensitive; CASEI both sides |
| LIKE escape | `\` | `ESCAPE 'c'` | none | `\%`, `\_` |
| `!=` | not allowed | not allowed | `!=` | read as `<>`, printed as `<>` |
| Precedence | NOT > AND > OR | AND > OR | nesting | NOT > AND > OR |

A finding from the experiment: CQL2 gives `\` two jobs, string escape (Req 21) and LIKE escape
(Req 5K). If the string reader consumes `\_` to `_`, the LIKE escape is lost and `'A\_1'` matches
`AX1` (the first run failed exactly so). The sketch keeps `\%` and `\_` whole for LIKE. The
standard does not say which reading wins (open; cql2-rs's `like` crate was not read).

## 6. Security

- A filter or label expression is stored in the project file; a file shared by someone else, or a
  data layer's settings, carry text the user never typed. `eval` or `new Function` on that text
  runs arbitrary script in the app's origin: it can read IndexedDB projects, call `fetch`, or
  rewrite the page. An expression language must be data, read by a parser that only builds a tree
  of known node types (P: pygeofilter's own docstring says its native filter is "parsed using
  eval", the pattern to avoid).
- A RegExp built from user LIKE text is a denial-of-service door even with escaping (section 7).
- Property lookup must use own-property checks: `constructor`, `toString`, `__proto__` are not
  fields (tested).
- Limits: length (4000 characters), nesting depth (64), so a crafted file cannot overflow the
  stack (`NOT` repeated 5000 times gives a clean error, tested).
- Labels write field text into the page: draw with canvas `fillText` or set `textContent`, never
  `innerHTML`.

## 7. Experiment

Files: `docs/research/experiments/v173-filter/cql2-subset.js` (the sketch: tokenizer, recursive
descent parser, three-valued evaluator, LIKE matcher without RegExp, printer),
`run.js` (cases), `results.txt` (output). Node v22, 2026-11-08. Research only, not the app's code.

Grammar of the sketch: `or := and {OR and}`, `and := not {AND not}`, `not := NOT not | primary`,
`primary := ( or ) | TRUE | FALSE | predicate`, `predicate := operand (cmp operand | IS [NOT] NULL
| [NOT] LIKE operand | [NOT] BETWEEN operand AND operand | [NOT] IN ( operand {, operand} ))`,
`operand := name | "quoted name" | 'string' | number | TRUE | FALSE | NULL | CASEI(operand)`.

Results: 73 of 73 cases pass after one fix (the LIKE escape above). Covered: both quote escapes,
unclosed strings, spaced and keyword field names, missing and null fields in every operator, the
AND/OR/NOT truth table, the NOT IN null trap, precedence and grouping, IN, BETWEEN (inclusive, and
followed by AND), LIKE `%`, `_`, case, CASEI, escaped `%` and `_`, numeric strings (`'1500'`,
`'1e3'`, `' 12 '`, `''`), booleans, case-insensitive keywords, prototype names, JavaScript text,
200 nested parentheses, 5000 NOTs, trailing text, `!=`, and 11 round trips text to tree to text.

Measured:

- Sketch size: 13.7 KB, 276 lines unminified ES5 (H2 holds; a production file of under 400 lines).
- 10,000 features with `ZONE IN (...) AND POP BETWEEN ... AND NAME LIKE 'n1%'`: 16 to 18 ms.
- LIKE matcher (iterative, O(n*m) worst): pattern `%a%a%a%a%a%a%a%b` on 20,000 characters, 3 ms.
- The same pattern as RegExp `^.*a.*a.*a.*a.*a.*a.*a.*b$`: 20 characters 3 ms, 40 chars 260 ms,
  60 chars 6.9 s, 80 chars 75 s: polynomial blow-up from one short pattern on an 80-character
  value. H3 falsified: never build a RegExp from LIKE text.

## 8. Alternatives

| Criterion | CQL2 Text subset | SQL WHERE subset (ArcGIS-like) | MapLibre JSON | Clause builder (structured) |
|---|---|---|---|---|
| Safe without eval | yes, small parser | yes, small parser | yes, no parser | yes, no parser |
| User-typable | yes | yes | no | no (menus) |
| Standard | OGC 21-065r2 1.0.0 | ANSI SQL, dialect per source | MapLibre spec, de facto | none (stores CQL2 JSON if wanted) |
| ArcGIS-like | nearly (same core) | yes | no | yes (designer mode) |
| Size in ES5 | about 14 KB | about the same; more if functions | about 4 KB evaluator | about 3 KB evaluator plus UI |
| Round trip to text | yes (tested) | yes | via a printer | yes, if each clause prints as CQL2 |
| Phone use | typing is awkward | same | no | best |

## 9. Recommendation (for the owner to decide)

Store one canonical form and offer two editors, as ArcGIS does:

1. The stored filter is the CQL2 Text subset (Basic + Advanced Comparison + CASEI), plain
   text in the project file, with the parsed tree rebuilt on load. It reads as ArcGIS SQL for every
   common query (`=`, `<>`, `<`, `>`, AND, OR, NOT, IN, BETWEEN, LIKE, IS NULL, `''`), and it is a
   named, versioned standard. Accept `!=` and the ArcGIS `UPPER`/`LOWER` spelling as aliases if the
   owner wants; print canonical CQL2.
2. A clause builder (field, operator by field type, value picked from the layer's distinct values,
   All/Any) for phone and tablet, writing CQL2 text through the printer; a text box for desktop
   users, with errors that name the character position.
3. Three-valued logic; missing equals NULL; only TRUE keeps a feature. Numeric strings compare as
   numbers against number literals (ArcGIS-served GeoJSON often has them). Warn when `NOT IN` has a
   NULL item.
4. LIKE by an iterative matcher, never RegExp. Limits on length and depth. Own-property reads.
5. Labels: one field, or fields joined with text (a template such as `{NAME} ({AREA} m2)`), not an
   expression language. Points: beside the point. Polygons: polylabel's pole of inaccessibility
   (ISC, ported to ES5 with credit), falling back to the centroid. Lines: the midpoint along the
   length. Collision: greedy screen boxes by priority, drop on overlap ("Never overlap").

Owner's decisions needed: (a) CQL2 text as the stored form, or structured clauses only; (b) the
numeric-string coercion rule; (c) aliases (`!=`, UPPER/LOWER, ILIKE) or strict CQL2; (d) port
polylabel (ISC) or write a simpler grid search; (e) whether labels may use a template or one field.

## 10. Risks and open questions

- CQL2's double use of `\` (string and LIKE escape) is not resolved in the text; check cql2-rs's
  `like` crate and the OGC test suite before the code.
- CASEI requires full Unicode case folding; `toLowerCase` differs for a few characters (German
  sharp s, Turkish dotted i). Say so or add the short CaseFolding exceptions.
- Dates (`DATE('...')`, `TIMESTAMP('...')`) not in the sketch; data-layer dates are mostly text.
- ArcGIS clause operator names in Pro designer mode are only in screenshots (not verified as text).
- Collision for many labels on phones: measure with real layers when built.

## 11. Confidence

| Finding | Level | Confidence |
|---|---|---|
| CQL2 edition, classes, BNF, null table, LIKE, escapes | P | high |
| ArcGIS operators, quoting, null exclusion, precedence | P | high |
| QGIS quoting, LIKE/ILIKE, NULL, placement and overlap modes | P | high |
| MapLibre strict typing, two-valued, no LIKE | P | high |
| polylabel algorithm and licence | P | high |
| pygeofilter native backend uses eval | P | high |
| cql2-wasm size, sql-where-parser behaviour | S (npm metadata) | medium |
| RegExp blow-up and sketch timings | measured here | high for this machine |
| Greedy collision approach | S | medium |

A second reader should re-check the CQL2 rules in 3.1 and the edges table before code uses them.

## 12. References

- OGC 21-065r2, Common Query Language (CQL2) 1.0.0, 2024-07-26, https://docs.ogc.org/is/21-065r2/21-065r2.html (P, read 2026-11-07).
- Esri, ArcGIS Pro (latest): "SQL reference for query expressions used in ArcGIS"; "Filter features with definition queries"; "Introduction to query expressions"; "Construct and modify queries"; "Control the order of operations in a SQL query"; "Specify text for labels", pro.arcgis.com (P, 2026-11-07).
- Esri, ArcGIS Online: "Apply filters (Map Viewer)", doc.arcgis.com (P, 2026-11-07).
- QGIS 3.40 User Guide: Vector Properties (Query Builder), Expressions, List of functions (Operators), Label settings, docs.qgis.org (P, 2026-11-07).
- MapLibre style-spec 26.5.1, src/reference/v8.json and src/feature_filter/index.ts, BSD-3 (P).
- mapbox/polylabel 2.1.0, polylabel.js, ISC (P).
- geopython/pygeofilter main, cql2_text/grammar.lark and backends/native/evaluate.py, MIT (P).
- developmentseed/cql2-rs main (0.6.1), src/cql2.pest and src/expr.rs, MIT (P).
- EricSmekens/jsep master (npm 1.6.0), src/jsep.js, MIT (P).
- npm registry metadata: sql-where-parser 2.2.1, cql2-wasm 0.5.6, cql2-filters-parser 0.9.14 (S).
