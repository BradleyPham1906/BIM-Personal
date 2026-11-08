# V173 research: classification, raster stretch and colour ramps (the algorithms side)

Date: 2026-11-07 to 2026-11-08. Scope: the algorithms behind graduated colours (classification methods),
categories, raster stretch and colour ramps, read in their primary sources and open implementations,
with experiments run here. It follows `docs/research/research-protocol.md`. Levels: **P** primary (the
paper, the spec, the code read as text, or measured here); **S** secondary, with the gap said; **U** a
search summary only, never used by code until confirmed.

Experiments: `docs/research/experiments/v173-classify/` (`classify.js` our own ES5 implementations,
`run.js` the runner, `calemp.json` the 58-value test data from mapclassify, BSD-3). Downloaded upstream
files were kept outside the repository in the session scratchpad and read as text only; none was run.

## 1. Question and hypotheses

Question: which algorithm should the app use for each classification method, and with what limits, so
that an ES5 browser build gives the same breaks as QGIS, ArcGIS and PySAL do?

- H1: the Fisher-Jenks optimum can be computed exactly in the browser for every layer the app will hold
  (up to about 1e5 values) without sampling. Falsified for the plain O(k n^2) programme (57 s at 1e5);
  supported for the divide-and-conquer form (0.11 s at 1e5). See section 6.
- H2: the open implementations agree on Fisher-Jenks breaks. Partly falsified: the exact ones agree;
  geostats' `getClassJenks` and QGIS's sampling on large layers do not (section 5).
- H3: quantile, equal interval and standard deviation have one definition each. Falsified: quantile has
  at least two break rules in use, standard deviation at least three (section 4).
- H4: the app's YlOrRd 6-class ramp is ColorBrewer's exactly. Confirmed (section 8).

## 2. Search log

| # | Where | Query or path | Kept |
|---|---|---|---|
| 1 | raw.githubusercontent.com | simple-statistics `src/ckmeans.js`, `jenks*.js`, tests, LICENSE | read |
| 2 | raw.githubusercontent.com | simogeo/geostats `lib/geostats.js`, package.json | read |
| 3 | raw.githubusercontent.com | QGIS `src/core/classification/*.cpp`, `qgssymbollayerutils.cpp` prettyBreaks, raster min/max and contrast files | read |
| 4 | raw.githubusercontent.com | pysal/mapclassify `classifiers.py`, `tests/test_mapclassify.py`, `datasets/calemp` | read |
| 5 | raw.githubusercontent.com | wch/r-source `src/appl/pretty.c`, `base/R/pretty.R`, `stats/man/quantile.Rd` | read |
| 6 | raw.githubusercontent.com | axismaps/colorbrewer `colorbrewer_schemes.js`; d3/d3-scale-chromatic `YlOrRd.js`, LICENSE | read |
| 7 | journal.r-project.org | Wang & Song 2011, RJ-2011-015 (PDF) | read |
| 8 | cran/Ckmeans.1d.dp DESCRIPTION | version, references | read |
| 9 | doc.esri.com | data-classification-methods; stretch-function; histogram-stretching; arcpy Stretch | read |
| 10 | web search | ArcGIS Jenks sample size | nothing primary found |
| 11 | web search | Jenks 1977 / Fisher 1958 citations | bibliographic only (papers not open) |
| 12 | web search | simple-statistics, geostats, QGIS Jenks issues | QGIS #6625, #28299; geostats #3, #49 |

## 3. Findings (level, confidence)

1. **The Fisher-Jenks problem is exact 1-D k-means.** Minimise the within-class sum of squared
   deviations (SDCM) over contiguous classes of the sorted values. Recurrence (Wang & Song 2011):
   D[i,m] = min over m <= j <= i of D[j-1,m-1] + d(x_j..x_i), with d computed in constant time from
   running sums, giving O(k n^2) time and O(k n) memory. P (paper read), high.
2. **Fisher (1958) and Jenks (1977) are not open.** Fisher, "On grouping for maximum homogeneity",
   JASA 53:789-798; Jenks, "Optimal data classification for choropleth maps", Occasional Paper 2, Dept.
   of Geography, Univ. of Kansas. Their content is known here only through Wang & Song, the code
   comments that cite the 2006 r-sig-geo Fortran/Java port, and the QGIS/mapclassify code. S, medium:
   the recurrence is the same in every reading, but the original texts were not read.
3. **The optimum's argmin is monotone, so divide and conquer gives the same answer in O(k n log n).**
   simple-statistics' `ckmeans` says it follows Ckmeans.1d.dp 3.4.6 ("improved runtime from O(kn^2) to
   O(kn log(n))"); Ckmeans.1d.dp 4.3.6 cites Song & Zhong 2020 for a further linear-time version (SMAWK,
   not read). Measured here: identical SDCM and breaks to the plain programme at every size tested up
   to 1e5 (section 6). P (code read, measured), high.
4. **The classic "Jenks" code is the same exact programme.** simple-statistics `jenksMatrices`, geostats
   `getClassJenks/Jenks2`, QGIS `QgsClassificationJenks`, mapclassify `_fisher_jenks_means` are all the
   LC/OP matrix form of the O(k n^2) programme; they compute the exact optimum on what they are given.
   P, high.
5. **mapclassify `NaturalBreaks` is not Jenks.** It runs scikit-learn k-means (k-means++, 10 random
   starts); only `FisherJenks` is exact. Its docstring happens to give the same calemp breaks. P, high.
6. **geostats `getClassJenks` (v2.1.0, MIT) starts its backtrack at row n-1, not n.** Read as text it
   returns the optimum of the first n-1 sorted values with the maximum appended. Reproduced here as our
   own arithmetic: on calemp k=5 that gives breaks [29.82,110.74,264.93,370.5,4111.45], GVF 0.662,
   against the exact 0.998; on [1,2,4,5,7,9,10,20] k=3, GVF 0.601 against 0.943. geostats issue #3
   reported odd ranges; the maintainer did not confirm a bug. P (code read; effect measured on our
   transcription of the rule), high that the rule is as read; medium that every geostats call is
   affected (not run).
7. **QGIS samples above 3000 values, and the sample is padded with zeros.** `mMaximumSize = 3000`;
   above it the sample array is sized max(3000, n/10) but filled by a stride that writes only about
   3000 slots; the rest stay 0.0 (QVector value-initialises). Our model of the arithmetic: n=1e5 leaves
   7000 of 10 000 slots at zero; at n=1e6 the int product `i*(M-2)` passes 2^31 (signed overflow in
   C++), and only about 2150 slots are written in our wrap-around model. Older QGIS (3.12-3.14) sampled
   at random (QGIS #6625: "breaks differ each run"). P (code read, master, 2026-11), medium on the
   exact effect (not run in QGIS). No issue filed against the zero padding was found (search 12).
8. **ArcGIS Pro's Natural Breaks text gives no algorithm detail or sampling limit**; Defined Interval
   mentions "maximum sample size" without the number. The often-repeated 10 000-sample figure was not
   found in a primary source. P for what the page says; the sample size is U.
9. **Quantile break rules differ.** QGIS and mapclassify (scipy `scoreatpercentile`) and
   simple-statistics use Hyndman-Fan type 7 (linear interpolation at (n-1)p; R's default). geostats
   uses a nearest-rank rule, value at index round(i n/k + 0.49). QGIS's comment says q(n+1) but its
   code uses q(n-1). On calemp k=5: type 7 [1.464,5.798,13.278,54.616] counts [12,11,12,11,12]
   (matches mapclassify); nearest rank [1.34,5.9,13.09,57.26] counts [12,12,11,12,11]. P, high.
10. **Duplicate quantile breaks:** mapclassify collapses repeated breaks (`np.unique`) and warns, so k
    falls; type 7 can still leave empty classes, since interpolated breaks need not be data values
    (measured: [0x7,1,2,3] k=4 gives counts [7,0,3]). P, high.
11. **Standard deviation has three conventions.** mapclassify `StdMean`: cuts at mean + s*[-2,-1,1,2],
    sample s (ddof=1), max appended (matches its test exactly). geostats: odd k, a class of width 1 s
    centred on the mean; even k, the mean is a break; population s. QGIS: R classInt style, pretty()
    breaks of the z-scores, population s, so the class count may differ from what was asked. Esri: "a
    proportion of the standard deviation" (1, 1/2, 1/3, 1/4); whether the mean is a break or a class
    centre is not stated on the page. P for the three codes; Esri's centring U.
12. **Pretty breaks: R and mapclassify differ.** R `pretty()` picks a unit from {1,2,5,10} x 10^p using
    biases h=1.5, h5=0.5+1.5h and min.n = n %/% 3; QGIS ports it (`prettyBreaks`, with an `int U`
    truncation where R uses double, harmless at the defaults). mapclassify `_pretty` is a different,
    simpler rule (Heckbert-like). Both give 0..5000 by 1000 on calemp. P, high.
13. **Geometric Interval is Esri's own algorithm.** Esri: breaks "based on class intervals that have a
    geometric series", "minimizing the sum of squares of the number of elements in each class", with
    the coefficient allowed to change once to its inverse. Not enough to reimplement and match. geostats'
    "geometric progression" is equal intervals in log space (positive data only). P for the text; an
    Esri-identical implementation is not possible from it.
14. **GVF = 1 - SDCM/SDAM**, SDAM = squared deviations about the overall mean. mapclassify reports ADCM
    and GADF (absolute deviations about medians) instead; its `get_tss` returns the within-class sum
    despite its name. P (code read; S for Jenks' original GVF wording).
15. **Raster stretch defaults (QGIS):** cumulative count cut 2% to 98% (`CUMULATIVE_CUT_LOWER = 0.02`,
    `UPPER = 0.98`), standard deviation factor 2.0, linear min-max output
    floor((v - min)/(max - min) x 255) clamped to 0..255. Cumulative cut is computed on a histogram and
    returns bin lower edges for both ends (so the upper limit sits up to a bin low). P, high. Esri's
    arcpy `Stretch` documents types and ranges (min_percent 0-99, num_stddev) but the UI defaults were
    not found in a primary page. U for Esri defaults.
16. **ColorBrewer** (Apache-2.0 style licence, 2002 Brewer, Harrower, Penn State; schemes file from
    axismaps/colorbrewer; d3-scale-chromatic ISC carries the same hex): 18 sequential schemes 3-9
    classes, 9 diverging 3-11, 8 qualitative (Set2, Accent, Dark2, Pastel2: 3-8; Set1, Pastel1: 3-9;
    Set3, Paired: 3-12). Each scheme carries `blind`, `print`, `copy`, `screen` arrays indexed by class
    count minus 3 (a single entry applies to all). P for the data; S for the meaning of codes 1/2/0
    (good / possibly / not), read from the site's behaviour, not a specification.

## 4. Method definitions

| Method | Definition used for code | Source | Level |
|---|---|---|---|
| Natural breaks (Fisher-Jenks) | contiguous classes of sorted x minimising sum of squared deviations from class means | Wang & Song 2011; mapclassify FisherJenks | P |
| Quantile | breaks at type-7 quantiles p = i/k, i = 1..k-1, plus max; repeated breaks collapsed | R `quantile` type 7; QGIS; mapclassify | P |
| Equal interval | breaks min + i (max-min)/k, i = 1..k-1, plus max | mapclassify; QGIS; geostats | P |
| Defined interval | fixed width w; classes from the data's range in steps of w (Esri: at least 3 classes) | Esri page | P (text) |
| Standard deviation | breaks every f s from the mean, f in {1, 1/2, 1/3, 1/4}; choose mean-as-break or mean-centred class explicitly; state ddof | mapclassify, geostats, QGIS, Esri | P / U for Esri centring |
| Pretty | R `pretty(range, n)` with R's defaults | R pretty.c; QGIS port | P |
| Geometric interval | no reproducible definition; log-equal intervals as an honest substitute, named as such | Esri text; geostats | P |
| GVF | 1 - SDCM / SDAM | Jenks via mapclassify, S | S |
| Min-max stretch | out = clamp(floor((v-lo)/(hi-lo) x 255)) with lo,hi = min,max | QGIS LinearMinMax | P |
| Std-dev stretch | lo,hi = mean -/+ n s, default n = 2 (QGIS) | QGIS min/max widget | P |
| Percent clip / cumulative cut | lo,hi = values at cumulative fractions p_lo, p_hi (QGIS 0.02, 0.98) | QGIS cumulativeCut | P |
| Histogram equalise | out = round((cdf(v) - cdf_min)/(N - cdf_min) x (L-1)) | textbook form (Gonzalez and Woods), not read here | S |

Assignment rule: class j holds bins[j-1] < v <= bins[j] (upper bounds inclusive; mapclassify). Note
simple-statistics' `jenks` returns lower limits plus the max (`[1,7,20,20]`), so its arrays are not
directly comparable to mapclassify's upper bounds.

## 5. Implementations compared

| Implementation | Licence | Exact? | Time | Limits and edges |
|---|---|---|---|---|
| simple-statistics `ckmeans` | ISC | yes | O(k n log n) | throws if k > n; one cluster if all equal; median shift for stability |
| simple-statistics `jenks` | ISC | yes | O(k n^2) | returns null if k > n; lower-limit output; median shift |
| geostats `getClassJenks` (2.1.0) | MIT | no on full data: backtrack from n-1 | O(k n^2) | errors (alert) if k >= n; `Jenks2` sets first bound to 0 when equal to the second |
| QGIS `QgsClassificationJenks` | GPL-2+ (read only) | exact up to 3000 values; sampled above | O(k s^2) on sample s | zero-padded sample when n/10 > 3000; int overflow near n = 7e5; returns the values when k >= n |
| mapclassify `FisherJenks` | BSD-3 | yes | O(k n^2) (numba) | raises if distinct < k; Welford running variance |
| mapclassify `FisherJenksSampled` | BSD-3 | on sample | O(k s^2) | 10% or 1000 values, random with replacement, min and max forced |
| mapclassify `NaturalBreaks` | BSD-3 | no (k-means) | iterative | k lowered to distinct count |
| Ckmeans.1d.dp 4.3.6 (R/C++) | LGPL (not read) | yes | O(k n) per Song & Zhong 2020 | U for details |
| ArcGIS Pro | proprietary | not stated | not stated | sampling U |

## 6. Experiments (all raw numbers from `node run.js ...`)

Environment: Node v22.23.4, linux x64, 4 vCPU Intel Xeon @ 2.10GHz. Best of 5 runs (1 run for the
slowest). Data for timing: seeded log-normal (mulberry32 seed = n), sigma 1.5.

**(a) Worked examples.**
- calemp k=5 Fisher-Jenks: [75.29, 192.05, 370.5, 722.85, 4111.45], counts [49,3,4,1,1], ADCM 799.24,
  GVF 0.998435. mapclassify test: same bins, counts and ADCM. MATCH (both DP and D&C).
- calemp k=9: [16.7, 40.48, 75.29, 110.74, 192.05, 264.93, 370.5, 722.85, 4111.45]; find_bin of
  [0,1,3,5,50,70,101,202,390,505,800,5000,5001] = [0,0,0,0,2,2,3,5,7,7,8,8,8], matching mapclassify's
  TestFindBin; k=5 gives [0,0,0,0,0,0,1,2,3,3,4,4,4], matching.
- Quantiles k=5 type 7: [1.464, 5.798, 13.278, 54.616, 4111.45], counts [12,11,12,11,12]. MATCH.
- Equal interval k=5: [822.394, 1644.658, 2466.922, 3289.186, 4111.45], counts [57,0,0,0,1]. MATCH.
- StdMean [-2,-1,1,2]: [-967.36235382, -420.71712519, 672.57333208, 1219.21856072, 4111.45], counts
  [0,0,56,1,1], mean 125.928103, s 546.645229. MATCH.
- Pretty: R rule [0,1000,...,5000]; mapclassify rule the same; R pretty(c(-3.2,7.9)) = -4..8 by 2.
- simple-statistics jenks fixtures reproduced as classes ({1..5},{7..10},{20}; {2},{32..34},{100};
  one per value); ckmeans fixtures reproduced, including the 1e-12 floating-point case.
- GVF on calemp k=5: Fisher-Jenks 0.9984, equal interval 0.9489, log-equal 0.6565, quantile 0.1729.
  Fisher-Jenks GVF by k: 2: 0.9489, 3: 0.9872, 4: 0.9967, 5: 0.9984, 6: 0.9993, 7: 0.9995, 9: 0.9998.

**(b) Timing (ms).**

| n | k | plain DP O(k n^2) | divide and conquer | quantile (sort) |
|---|---|---|---|---|
| 1 000 | 5 | 7.3 | 1.2 | 0.3 |
| 1 000 | 9 | 12.9 | 1.6 | 0.3 |
| 3 000 | 5 | 46.7 | 1.8 | 0.7 |
| 3 000 | 9 | 140.6 | 4.0 | 0.9 |
| 10 000 | 5 | 796.5 | 9.3 | 3.9 |
| 10 000 | 9 | 1356.4 | 10.2 | 2.7 |
| 30 000 | 5 | 4531.6 | 20.0 | 14.7 |
| 30 000 | 9 | 11141.9 | 50.6 | 13.2 |
| 100 000 | 5 | 57475 (one run) | 107.5 | 44.8 |
| 100 000 | 9 | not run | 126.6 | 49.6 |
| 300 000 | 5 / 9 | not run | 346.7 / 471.0 | 161.5 / 186.4 |
| 1 000 000 | 5 / 9 | not run | 1326.7 / 1597.0 | 548.6 / 572.8 |

DP and D&C gave identical SDCM and breaks at every n where both ran (1e3 to 1e5). Memory is two k x n
typed arrays (k=9, n=1e6: about 108 MB for Float64 + Int32), the real ceiling in a phone browser.

**(c) Edge cases** (our implementation's behaviour, the proposed rule):
- n < k ([3,1,2], k=5): Fisher-Jenks lowers k to 3 distinct values; type-7 quantile and equal interval
  give 5 breaks with empty classes [1,0,1,0,1].
- All equal ([7,7,7,7]): one class [7] for every method. The current colour lens does not fail here:
  `bimLensPick` (`src/js/engine/map/colour-lens.js` line 95) returns the last bin when hi <= lo, before the
  division on line 96 (corrected by the main session on 2026-11-08; the agent's first draft said NaN). It builds six
  bins of zero width, puts every value in the last, and its legend (which lists only bins with a count) shows one
  row, "7 to 7".
- Duplicates ([1,1,1,1,2,2,9,9,9,30], k=4): Fisher-Jenks and quantile both give one class per distinct
  value [1,2,9,30]; equal interval [8.25,15.5,22.75,30] counts [6,3,0,1].
- NaN, null, undefined, '', booleans, Infinity, 'x' dropped; numeric strings ('4') kept: [1,3,4].
- Negatives ([-50..41], k=3): Fisher-Jenks [-48, 2, 41] counts [3,5,2]; works unchanged; log-equal refuses.
- Two distinct ([0,0,0,5,5], k=5): Fisher-Jenks k=2 [0,5]; quantile collapses to [0,2,5] with an empty
  class; equal interval [1..5] with three empty classes.
- Empty and single value: no bins, or one.
- Equal-cost ties ([0,1,2], k=2; both splits cost 0.5): strict '<' keeps the earliest start of the
  last class, giving {0},{1,2}, upper bounds [0,2]; the rule must be written down so it is reproducible.
- Offset data (1.7e12 + 0..11): exact breaks [3,7,11] after the median shift.

**Sampling.** On 1e5 log-normal values, k=5, exact GVF 0.869447. Stride samples: 1000 values 0.836154,
3000 values 0.866643, 10 000 values 0.868650. Random samples: 1000 0.860215, 3000 0.863178, 10 000
0.834826 (random samples are noisier, and not reproducible). QGIS-style zero-padded sample (3000 real,
7000 zeros): bins [4.775, 21.681, 66.594, 168.956, 657.07], GVF 0.864882.

**Raster stretch** (10 000 log-normal values plus 20 outliers to 1450; mean 5.05, s 46.34):

| Stretch | Range | Output levels used | Share at 0 | Share at 255 |
|---|---|---|---|---|
| min-max | 0.004 to 1450 | 43 | 0.874 | 0.000 |
| std dev n=2 | 0.004 to 97.73 | 149 | 0.267 | 0.003 |
| std dev n=2.5 | 0.004 to 120.90 | 132 | 0.313 | 0.002 |
| percent clip 2/2 | 0.046 to 23.95 | 241 | 0.097 | 0.020 |
| percent clip 0.5/0.5 | 0.022 to 63.23 | 182 | 0.196 | 0.005 |
| histogram equalise | cdf | 256 | 0.002 | 0.002 |

The QGIS-style 256-bin cumulative cut gave 0.004 to 22.66 against the exact quantiles 0.046 to 23.95:
the bin rule moves both ends down by up to one bin width (5.66 here).

## 7. Edges, risks and counter-evidence

- Jenks' breaks are data-specific and should not be used to compare maps of different data (Esri page,
  P). Quantile hides the size of differences and can put very different values together (calemp: GVF
  0.17), and creates empty classes with ties. Equal interval on skewed data puts 57 of 58 values in one
  class. Each method needs its histogram shown with the breaks (practice; S).
- Fisher-Jenks optima can be unstable for near-tied partitions: a tiny edit to the data can move a
  break. Tie rule must be fixed and tested.
- QGIS's large-layer breaks will not match an exact computation; any parity test against QGIS must stay
  under 3000 values.
- geostats' Jenks should not be used as a reference for fixtures.
- Typed arrays (Float64Array, Int32Array) are not ES5 by the letter (ES2015 adopted them) but have been
  in every browser with WebGL since 2011-2013; the app already uses Float32Array for WebGL. If the
  contract forbids them, plain arrays work at about twice the memory.
- ColorBrewer's colourblind flags cover class counts, not ramps interpolated beyond 9 or 12 classes.

## 8. ColorBrewer verification

The app's `BIM_LENS_RAMP` (`src/js/engine/map/colour-lens.js` line 19),
`['#ffffb2','#fed976','#feb24c','#fd8d3c','#f03b20','#bd0026']`, equals ColorBrewer YlOrRd 6:
rgb(255,255,178), (254,217,118), (254,178,76), (253,141,60), (240,59,32), (189,0,38), and d3's
`ffffb2fed976feb24cfd8d3cf03b20bd0026`. `BIM_LAND_SLOPE_D` in `standards/registry.js` line 926 uses
YlOrRd 5 (`#fecc5c` second) exactly. YlOrRd's `blind:[1]` marks it colourblind-safe at every count.
Colourblind-safe by the data: all 18 sequential; diverging RdBu, PiYG, PRGn, RdYlBu, BrBG, PuOr
(Spectral and RdYlGn only possibly at 3-5, not beyond; RdGy possibly); qualitative Set2 and Dark2 at 3
classes only, Paired at 3-4. Brewer's own guidance on class count (5-7) was not read in a primary text
here: S (Brewer's site and papers say most maps work with 3 to 7 classes; to confirm).

## 9. Recommendations for V173

| Method | Algorithm | Limit |
|---|---|---|
| Natural breaks | exact Fisher-Jenks by divide and conquer on the monotone argmin (ckmeans style), median shift, strict-less tie rule, iterative not recursive | exact to 1e5 values (about 0.1 s); above that, a deterministic stride sample of 1e5 with min and max kept, said in the legend; never random |
| Quantile | type 7 (matches QGIS, mapclassify, R), duplicate breaks collapsed, the reduced class count reported | none (sort only) |
| Equal interval | min + i w, last = max; all-equal gives one class | none |
| Defined interval | user width, lattice anchored at 0 (multiples of w), at least 1 class | cap classes (for example 32) |
| Standard deviation | f in {1, 1/2, 1/3, 1/4}; mean-centred class by default with a "mean as break" option; population s stated | needs s > 0 |
| Pretty | R `pretty()` port | k is approximate, say so |
| Geometric | log-equal intervals for positive data, named "log interval", not "Geometric Interval" | refuse with zero or negatives |
| Categories | one class per distinct value, ColorBrewer qualitative up to 12, then "other" | 12 |
| Raster | min-max, std dev (n default 2), percent clip (2/98 default, exact quantiles, not bins), histogram equalise (exact cdf on a sample) | sample large rasters (stride) for statistics |
| Fit | report GVF with each classification | |

Open: Esri's stretch and Jenks sampling defaults (U); Esri's standard-deviation centring (U); Brewer's
class-count guidance in a primary text; Song & Zhong 2020 linear-time method (not read). An independent
second reader should recheck sections 3 and 6 before code.

## 10. References

- Wang, H. and Song, M. (2011). Ckmeans.1d.dp: optimal k-means clustering in one dimension by dynamic
  programming. The R Journal 3(2): 29-33. doi:10.32614/RJ-2011-015. Read 2026-11-07. P.
- Song, M. and Zhong, H. (2020). Bioinformatics, doi:10.1093/bioinformatics/btaa613. Cited by
  Ckmeans.1d.dp 4.3.6 DESCRIPTION; not read. S.
- Fisher, W. D. (1958). On grouping for maximum homogeneity. JASA 53: 789-798. Not read. S.
- Jenks, G. F. (1977). Optimal data classification for choropleth maps. Occasional Paper 2, Dept. of
  Geography, University of Kansas. Not read. S.
- simple-statistics (ISC, Tom MacWright), main branch: src/ckmeans.js, jenks.js, jenks_matrices.js,
  jenks_breaks.js, quantile_sorted.js, tests. Read 2026-11-07. P.
- geostats 2.1.0 (MIT, Simon Georget), lib/geostats.js. Read 2026-11-07. P. Issues #3, #49 via search. U.
- QGIS master (GPL-2+), src/core/classification/qgsclassification{jenks,quantile,standarddeviation,
  prettybreaks}.cpp, qgsclassificationjenks.h, qgssymbollayerutils.cpp, raster/qgsrasterminmaxorigin.h,
  qgslinearminmaxenhancement.cpp, qgsrasterinterface.cpp, gui/raster/qgsrasterminmaxwidget.cpp. Read
  2026-11-07. P. Issues #6625, #28299 via search. U.
- mapclassify main (BSD-3, PySAL), classifiers.py, tests/test_mapclassify.py, datasets/calemp. Read
  2026-11-07. P.
- R source (GPL-2+), src/appl/pretty.c, src/library/base/R/pretty.R, stats/man/quantile.Rd. Read
  2026-11-07. P.
- ColorBrewer (Apache-2.0 style; Brewer, Harrower, Penn State 2002), axismaps/colorbrewer
  colorbrewer_schemes.js; d3-scale-chromatic (ISC) src/sequential-multi/YlOrRd.js. Read 2026-11-07. P.
- Esri, ArcGIS Pro: Data classification methods; Stretch function; Histogram stretching; arcpy
  Spatial Analyst Stretch (doc.esri.com). Read 2026-11-07. P for their text.
