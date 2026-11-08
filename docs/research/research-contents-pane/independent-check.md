# V173 research: independent second reading

Date: 2026-11-08. Reader: an independent agent that did not write `practice.md`, `classification.md` or
`filter-and-labels.md`. This is step 9 of `docs/research/research-protocol.md`: every fact the code will use, or
that a default depends on, is re-read in its source, and recorded as confirmed or not. A fact that fails goes
back to U.

## Method

- The three notes were read in full. Every fact that code or a default will rest on was listed. Facts that only
  describe practice and that no code uses (the Contents pane tabs, kepler.gl, Felt and similar) were not
  re-checked.
- Each source was fetched again on 2026-11-08 with curl through the session proxy. No quotation in the notes was
  trusted. The files were saved in the session scratchpad, outside the repository, and read as text only.
  - raw.githubusercontent.com: pysal/mapclassify `main` (`mapclassify/tests/test_mapclassify.py`,
    `mapclassify/classifiers.py`, `mapclassify/datasets/calemp/calempdensity.csv` and `data.py`);
    scipy/scipy `main` `scipy/stats/_stats_py.py`; wch/r-source `trunk` (`src/appl/pretty.c`,
    `src/library/base/R/pretty.R`, `src/library/stats/man/quantile.Rd`); qgis/QGIS `master`
    (`src/core/raster/qgsrasterminmaxorigin.h`, `src/ui/qgsgraduatedsymbolrendererwidget.ui`,
    `src/gui/symbology/qgsgraduatedsymbolrendererwidget.cpp`,
    `src/core/classification/qgsclassification{jenks,quantile,custom,methodregistry}.cpp`, `qgsclassificationjenks.h`,
    `src/core/symbology/qgsgraduatedsymbolrenderer.cpp`); axismaps/colorbrewer `master`
    (`colorbrewer_schemes.js`, `LICENCE.txt`); d3/d3-scale-chromatic `main` (`src/sequential-multi/YlOrRd.js`);
    mapbox/polylabel `master` (`polylabel.js`, `LICENSE`, `package.json`); simple-statistics `main`
    (`src/ckmeans.js`, `LICENSE`).
  - https://docs.ogc.org/is/21-065r2/21-065r2.html (the whole standard; HTML turned into text, then searched).
  - https://journal.r-project.org/articles/RJ-2011-015/RJ-2011-015.pdf (Wang and Song 2011, text extracted).
  - pro.arcgis.com: Pro SDK topic11645 (3.6); Pro 3.5 definition-query.htm, graduated-colors.htm,
    data-classification-methods.htm.
  - The Colby tutorial and the Meisterlin page cited for the raster stretch defaults; PSU GEOG 160 node 1975.
- The calemp worked examples were not taken from the notes' own runner (`docs/research/experiments/v173-classify/`).
  They were recomputed from mapclassify's CSV with a separate plain-Python script written for this check (an O(k n^2)
  Fisher-Jenks programme, type-7 quantiles, equal interval, the sample standard deviation), and compared with
  mapclassify's test file.
- R's `pretty()` cases were checked by tracing `pretty.c` by hand. R itself is not installed here.
- Verdicts: CONFIRMED (the source says it, or the recomputation gives it); NOT CONFIRMED (the source says
  something else, or does not say it); COULD NOT CHECK (the source did not load).

## Table

Abbreviations: C = classification.md, F = filter-and-labels.md, Pr = practice.md.

| # | Fact | Note | Level claimed | Source re-read | Verdict | Remark |
|---|---|---|---|---|---|---|
| 1 | Fisher-Jenks is exact 1-D k-means: contiguous classes of the sorted values minimising the within-class sum of squares, by dynamic programming in O(k n^2) time and O(k n) memory | C 3.1 | P | Wang and Song 2011 PDF | CONFIRMED | The paper gives "an exact dynamic programming solution with a runtime of O(n2 k)" and an (n+1) x (k+1) matrix. The paper does not name Fisher or Jenks. The equivalence rests on mapclassify's `_fisher_jenks_means` docstring and on the recomputation in rows 3 to 5. |
| 2 | Divide and conquer gives O(k n log n) (Ckmeans 3.4.6) | C 3.3 | P | simple-statistics `src/ckmeans.js` lines 207-208; LICENSE (ISC, 2014 Tom MacWright) | CONFIRMED | Only the comment was re-read. The note's measurement that the result is identical was not re-run. |
| 3 | calemp, k=5, Fisher-Jenks: breaks [75.29, 192.05, 370.5, 722.85, 4111.45], counts [49,3,4,1,1], ADCM 799.24 | C 6a | P | `test_mapclassify.py` TestFisherJenks; recomputed here | CONFIRMED | The test asserts the same bins, counts and `adcm == 799.24`. The recomputation gives the same bins, the same counts and ADCM 799.24. calemp is 58 values, the `emp/sq km` column (`data.py`). |
| 4 | calemp, k=9, Fisher-Jenks breaks [16.7, 40.48, 75.29, 110.74, 192.05, 264.93, 370.5, 722.85, 4111.45]; find_bin results for k=5 and k=9 | C 6a | P | TestFindBin; recomputed here | CONFIRMED | The recomputed k=9 breaks are identical. The test's two `known` arrays are the same as in the note. |
| 5 | GVF of calemp k=5 Fisher-Jenks is 0.998435 | C 6a | P (measured) | recomputed here | CONFIRMED | 0.998435091. |
| 6 | calemp, quantile k=5, type 7: [1.464, 5.798, 13.278, 54.616, 4111.45], counts [12,11,12,11,12] | C 3.9, 6a | P | TestQuantiles; recomputed here | CONFIRMED | |
| 7 | calemp, equal interval k=5: [822.394, 1644.658, 2466.922, 3289.186, 4111.45], counts [57,0,0,0,1] | C 6a | P | TestEqualInterval; recomputed here | CONFIRMED | |
| 8 | calemp StdMean: bins [-967.36235382, -420.71712519, 672.57333208, 1219.21856072, 4111.45], counts [0,0,56,1,1], sample s (ddof=1), mean 125.928103, s 546.645229 | C 3.11, 6a | P | TestStdMean; `classifiers.py` line 1851 `y.std(ddof=1)`; recomputed here | CONFIRMED | |
| 9 | mapclassify's quantile uses scipy `scoreatpercentile` (linear interpolation at (n-1)p, that is type 7) and collapses repeated breaks with `np.unique` | C 3.9, 3.10 | P | `classifiers.py` lines 255-256; scipy `_stats_py.py` lines 1961-2062 (default `interpolation_method='fraction'`, `idx = per/100 * (n-1)`) | CONFIRMED | The `np.unique` collapse is confirmed in `quantile()`. The warning it gives was not re-read. |
| 10 | Type 7 is R's default quantile | C 3.9 | P | `quantile.Rd`: `type = 7` in the usage; "The default method is type 7" | CONFIRMED | |
| 11 | QGIS quantile is type 7: the comment says q(n+1), the code uses q(n-1) with linear interpolation | C 3.9 | P | `qgsclassificationquantile.cpp` | CONFIRMED | The comment gives `NI1 = (int)(q*(n+1))`; the code has `a = q*(n-1)`, `Xq = (1-r)*v[aa] + r*v[aa+1]`. |
| 12 | mapclassify `NaturalBreaks` is k-means (k-means++, 10 starts), not exact | C 3.5 | P | `classifiers.py` lines 513-531 | CONFIRMED | `KMeans(n_clusters=k, init="k-means++", n_init=n_init)`, `n_init` default 10. |
| 13 | R `pretty()`: unit from {1,2,5,10} x 10^p; high.u.bias h=1.5; u5.bias h5=0.5+1.5h; min.n = n %/% 3; default n=5 | C 3.12 | P | `pretty.R` `.pretty` defaults; `pretty.c` lines 159-168 | CONFIRMED | |
| 14 | `pretty(c(-3.2,7.9))` = -4 to 8 by 2; calemp gives 0 to 5000 by 1000 | C 6a | P (measured) | `pretty.c` traced by hand | CONFIRMED | (-3.2, 7.9): cell 2.22, unit 2, ns -2, nu 4. calemp: cell 822.3, unit 1000, ns 0, nu 5. R was not run. |
| 15 | QGIS Jenks samples above 3000 values; the sample is sized max(3000, n/10) but a stride fills only about 3000 slots, so the rest stay zero | C 3.7 | P | `qgsclassificationjenks.h` (`mMaximumSize = 3000`); `qgsclassificationjenks.cpp` lines 84-118 | CONFIRMED as read | The `resize`, the stride test `i*(mMaximumSize-2)/(size-2) > j` and the slot writes are as the note says. The zero padding follows from the code. It was not run in QGIS, and the overflow figure near 7e5 was not recomputed. |
| 16 | QGIS graduated class count starts at 5 (range 1 to 999) | Pr 2.4 | P | `qgsgraduatedsymbolrendererwidget.ui` (`spinGraduatedClasses`: minimum 1, maximum 999, value 5) | CONFIRMED | |
| 17 | QGIS's default graduated mode is Equal Count (Quantile), the first entry in a list sorted by name | Pr 2.4 | P source, medium inference | widget .cpp lines 518-522 and 750-754; `qgsgraduatedsymbolrenderer.cpp` line 71; `qgsclassificationmethodregistry.cpp` lines 32-38; `qgsclassificationcustom.cpp` | CONFIRMED by tracing the code (not run) | Traced further than the note. A new renderer's method is `QgsClassificationCustom` (named "Custom"). The registry does not register it, so `findData` fails and the combo box stays on index 0. A QMap sorts by name, so index 0 is "Equal Count (Quantile)". |
| 18 | QGIS asks for confirmation before running Jenks on more than 50,000 features ("O(n2) complexity") | Pr 2.4 | P | widget .cpp lines 1117-1125 | CONFIRMED | |
| 19 | QGIS cumulative count cut is 2 % to 98 %; the std-dev factor is 2.0 | C 3.15, Pr 2.4 | P | `qgsrasterminmaxorigin.h` lines 40-46 | CONFIRMED | `CUMULATIVE_CUT_LOWER = 0.02`, `CUMULATIVE_CUT_UPPER = 0.98`, `DEFAULT_STDDEV_FACTOR = 2.0`. The histogram-bin behaviour of `cumulativeCut` was not re-read. |
| 20 | ArcGIS Pro graduated colours default to Natural Breaks with 5 classes (SDK) | Pr 2.2 | P (SDK), S (GUI) | Pro SDK topic11645 (3.6) | CONFIRMED for the SDK | The page reads "(default value = NaturalaBreaks)" and "breakCount (Optional) Number of breaks. (default value = 5)". The SDK says "breaks", where the note says "classes". The GUI default is still not stated in any Esri text. |
| 21 | Pro's default classification sample size is 10,000 records | Pr 2.2 | P | Pro 3.5 graduated-colors.htm | CONFIRMED | "The default sample size is 10,000 records." |
| 22 | About seven colours is the upper limit that can be told apart | Pr 2.2 | P | Pro 3.5 graduated-colors.htm | CONFIRMED | |
| 23 | Std-dev intervals of 1, 1/2, 1/3 and 1/4 | Pr 2.2, C 4 | P | Pro 3.5 data-classification-methods.htm | CONFIRMED | "intervals of one, one-half, one-third, or one-fourth". arcpy was not re-read. |
| 24 | A defined interval must give at least three classes | Pr 2.2, C 4 | P | the same page | CONFIRMED | "the minimum number of classes allowed, which is three". |
| 25 | Natural breaks are data-specific and not for comparing maps | Pr 2.2, C 7 | P | the same page | CONFIRMED | |
| 26 | Pro's default raster stretch is Percent Clip | Pr 2.2 | S | Colby tutorial (M. Gimond) | CONFIRMED as S | "The default is Percent Clip." The Bard tutorial was not re-read. It stays S: no Esri page says this. |
| 27 | Pro's percent clip default is 0.5 % at each end | Pr 2.2 | S | Meisterlin page | CONFIRMED as S | "the default setting is 0.5% from the minimum and the maximum." This is one teaching site (Pro 2.9.1). It stays S. |
| 28 | A layer can have several definition queries, at most one active, and all can be off | Pr 2.3, F 3.2 | P | Pro 3.5 definition-query.htm | CONFIRMED | "no more than one definition query can be active at a time ... they can all be turned off". |
| 29 | A definition query limits drawing, the attribute table, selection, labels, identify and geoprocessing; a display filter limits drawing only | Pr 2.3, F 3.2 | P | the same page | CONFIRMED | "affects not only drawing, but also which features appear in the layer's attribute table and can be selected, labeled, identified, and processed by geoprocessing tools". |
| 30 | ColorBrewer YlOrRd 6 = ['#ffffb2','#fed976','#feb24c','#fd8d3c','#f03b20','#bd0026'] | C 8 | P | `colorbrewer_schemes.js`; d3 `YlOrRd.js` | CONFIRMED | rgb(255,255,178), (254,217,118), (254,178,76), (253,141,60), (240,59,32), (189,0,38); d3 gives `ffffb2fed976feb24cfd8d3cf03b20bd0026`. The app's `BIM_LENS_RAMP` (`src/js/engine/map/colour-lens.js` line 19) is identical. |
| 31 | YlOrRd 5 has `#fecc5c` second (`BIM_LAND_SLOPE_D`); YlOrRd is marked `blind:[1]` | C 8 | P | the same files; `src/js/engine/standards/registry.js` line 926 | CONFIRMED | 5-class: rgb(254,204,92) is `#fecc5c`. The app's five colours match YlOrRd 5 exactly. |
| 32 | ColorBrewer's licence is Apache-2.0 style | C 3.16 | P | axismaps/colorbrewer `LICENCE.txt` | CONFIRMED | The file is the Apache License, Version 2.0. |
| 33 | CQL2 is OGC 21-065r2, version 1.0.0: submitted 2024-03-26, approved 2024-05-23, published 2024-07-26; editors Vretanos and Portele | F 3.1 | P | OGC 21-065r2 HTML, header | CONFIRMED | |
| 34 | The requirements classes are named "Basic CQL2", "Advanced Comparison Operators" (LIKE, BETWEEN, IN), "Case-insensitive Comparison" (CASEI) and "Accent-insensitive Comparison" (ACCENTI) | F 3.1 | P | the standard, contents and section 6.1 | CONFIRMED | Basic CQL2 holds and, or, not, the six comparisons and is null. |
| 35 | Precedence NOT > AND > OR, from the BNF | F 3.1 | P | BNF annex: `booleanExpression = booleanTerm {OR booleanTerm}`, `booleanTerm = booleanFactor {AND booleanFactor}`, `booleanFactor = [NOT] booleanPrimary` | CONFIRMED | |
| 36 | Not-equal is `<>` only; there is no `!=` | F 3.1 | P | BNF `comparisonOperator` | CONFIRMED | |
| 37 | Strings use single quotes; an embedded quote is `''` or `\'`; `\` is the escape, with `\a \b \t \n \v \f \r` | F 3.1 | P | Requirement 21, `/req/cql2-text/escaping`; BNF `escapeQuote = "''" \| "\\'"` | CONFIRMED | |
| 38 | Truth table: FALSE AND NULL = FALSE, TRUE OR NULL = TRUE, other mixes with NULL give NULL, NOT NULL = NULL; only an overall TRUE keeps an item | F 3.1 | P | Table 2, Table 3 and the text after Table 2 | CONFIRMED | |
| 39 | A comparison with a NULL operand is NULL (so `x <> 1` with x null is NULL); a missing property reads as NULL | F 3.1, 5 | P | Requirement 3C; Requirement 2B ("or NULL if unset") | CONFIRMED | |
| 40 | LIKE: `%` matches zero or more characters, `_` exactly one, `\` is the escape, and a NULL operand gives NULL | F 3.1 | P | Requirement 5, parts C, E, F, H, I, K | CONFIRMED | |
| 41 | BETWEEN is inclusive and is NULL when any operand is NULL | F 3.1 | P | Requirement 6, parts A and C | CONFIRMED | |
| 42 | An IN list has at least one item | F 3.1 | P | BNF `inList = scalarExpression [{"," scalarExpression}]` | CONFIRMED | |
| 43 | Keywords are case-insensitive; a property named like a keyword goes in double quotes | F 3.1 | P | section 8.2 (ABNF strings are case-insensitive); the sentence on keyword property names | CONFIRMED | |
| 44 | Under the strict BNF, identifiers (quoted or not) cannot hold spaces | F 3.1, 5 | P | BNF `propertyName`, `identifierStart`, `identifierPart` | CONFIRMED | The allowed characters are letters, `:`, `_`, `.`, digits and some Unicode ranges. There is no space. |
| 45 | CASEI must do full Unicode 15.0.0 case folding and should be applied to both sides | F 3.1 | P | Requirement 8E and the implementation note | CONFIRMED | "the function should be applied to both sides of an expression". |
| 46 | LIKE is case-sensitive unless CASEI is used | F 3.1, 5 | P | Requirement 5; the CASEI section | NOT CONFIRMED as a stated rule | The standard never says LIKE is case-sensitive. That follows from the purpose of CASEI, but it is not a requirement. Keep it as the app's own design choice, not as a CQL2 rule. |
| 47 | Basic CQL2 may allow only property-left, literal-right comparisons (Permission 1) | F 3.1 | P | Permission 1 | CONFIRMED | |
| 48 | How incompatible types are cast is not prescribed (`'5' > 4`) | F 3.1 | P | Permission 2 | CONFIRMED | So the rule for numeric strings is the app's choice (owner decision b). |
| 49 | NFD normalisation is recommended for string comparison | F 3.1 | P | Recommendation 1 | CONFIRMED | |
| 50 | The edges table's CQL2 column says `NOT IN ('a', NULL)` evaluates to NULL | F 5 | P (via 3.1) | BNF `inList` and `scalarExpression`; Requirement 7 | NOT CONFIRMED | CQL2 Text has no NULL literal: `scalarExpression` allows character, numeric, boolean and instant literals, property names and functions, so `('a', NULL)` does not parse. Requirement 7A gives IN only TRUE or FALSE. Requirement 7B makes list items the same literal type as the tested value. The standard does not define IN with a NULL item. The note's own SQL-style rule is a fair choice for the app, but it is not what CQL2 says. |
| 51 | polylabel 2.1.0, ISC licence, one dependency (tinyqueue) | F 4.3 | P | `LICENSE`, `package.json` | CONFIRMED | The licence line reads "Copyright (c) 2026 Mapbox". Keep that notice exactly as it is in the port. |
| 52 | polylabel algorithm: cell size min(width, height) but at least the precision; potential max = d + h*sqrt(2); seeds at the centroid cell, then the box centre; a priority queue by max; stop when max - best <= precision; split into four; blocks of 32 edges | F 4.3 | P | `polylabel.js` lines 5, 23-96, 116, 240 | CONFIRMED | The centroid cell is always made and compared by its signed distance, so a centroid outside the polygon loses. The note's "(if inside)" is the effect of that, not a separate test. |
| 53 | McHarg: "darker the tone, the greater the cost ... the least-social-cost areas are revealed by the lightest tone", p. 34, quoted by PSU GEOG 160, which cites McHarg (1971) | Pr 2.5 | S | PSU GEOG 160 node 1975 (now at courses.ems.psu.edu) | CONFIRMED as S | The wording and the page number are as the note gives them. Design with Nature was first published in 1969, which is outside the sources read here. PSU cites a 1971 printing, and the note says so. The book itself was not read, so this stays S. |
| 54 | Corbett (CSISS Classics, 2001): one transparency per factor, "superimposed upon one another over the original map" | Pr 2.5 | S | escholarship.org item 5x78n2gn and its PDF | COULD NOT CHECK | HTTP 403 from the site on both addresses. |
| 55 | Penn Architectural Archives finding aid (2008) calls it the "layer cake method" | Pr 2.5 | S | design.upenn.edu McHarg109.pdf | COULD NOT CHECK | HTTP 403. |

## Summary of verdicts

- CONFIRMED: 51 (rows 1-45, 47-49, 51-53). Of these, rows 26, 27 and 53 are confirmed as S and stay S. Rows 2, 15
  and 17 are confirmed by reading the code, not by running it.
- NOT CONFIRMED: 2 (rows 46 and 50).
- COULD NOT CHECK: 2 (rows 54 and 55).

## Facts that go back to U

1. "LIKE is case-sensitive unless CASEI is used", as a rule of CQL2 (F 3.1, F 5). CQL2 does not state it. If the
   app makes LIKE case-sensitive, the note and the code should say that this is the app's own choice.
2. "`NOT IN ('a', NULL)` gives NULL under CQL2" (the CQL2 column of the edges table in F 5). CQL2 Text cannot
   express a NULL list item, and it does not define IN with one. The app's rule (a NULL item makes the result NULL,
   with a warning) stays an app choice for the owner. Only the claim that CQL2 says so goes back to U.

Unchecked, with their level unchanged (S) but not re-read by this reader: Corbett 2001 (row 54) and the Penn
finding aid (row 55). No code depends on them. They support only the name and history of the "layer cake".

## Not re-read (outside this check's list)

geostats' `getClassJenks` backtrack (C 3.6); QGIS's standard deviation and pretty-breaks ports (C 3.11, 3.12); the
QGIS `cumulativeCut` bin rule (C 3.15); ArcGIS SQL quoting, null exclusion and precedence (F 3.2); MapLibre, cql2-rs,
pygeofilter and jsep (F 3.4, 3.5); the ArcGIS label default field (Pr 2.3, F 4.1); Brewer and Pickle 2002 (Pr 5).
If code is to use any of them, they need a second reading of their own.
