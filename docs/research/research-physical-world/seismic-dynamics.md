# Earthquake loads and structural dynamics: ASCE/SEI 7-22 ELF, the USGS service, modes, spectra, time history

One of four parallel research notes for the physical-world phases (2026-11-21). Method:
`docs/research/research-protocol.md`. Script: `docs/research/experiments/physical-world/seismic.py`
(numpy only). Saved service answers: `docs/research/experiments/physical-world/usgs-asce7-22-*.json`.
Downloads were kept under `/tmp/claude-0/dl-seis/`, read as text, never run. No repo file other
than this note, the script and the three JSON samples was touched.

## 1. Abstract

**Question.** What does the app need, fact by fact, to add (1) ASCE/SEI 7-22 seismic loads by
the equivalent lateral force (ELF) procedure, fed by the USGS seismic design service, and (2)
structural dynamics on its existing 6-dof frame solver: modes, modal response spectrum analysis
(MRSA) and linear response history by Newmark's method?

**Answer.** ASCE 7-22 keeps the familiar two-period ELF formulas as "Method 2", but redefines
SDS and SD1 (90% of the multi-period spectrum's peak, section 21.4) and adds "Method 1"
(Cs = Sa(T)/(R/Ie) from the multi-period spectrum); equation numbers shift by one from 7-16.
The USGS service answers keylessly in about 1.2 to 2 s with SDS, SD1, TL, the SDC and both
spectra, and allows browsers (`Access-Control-Allow-Origin: *`) except when CloudFront serves a
copy cached from a request without an Origin header: the app must make every URL unique (the
free `title` parameter does this). Modes: a lumped or consistent mass matrix in tonnes
(kN s2/m), a generalized Jacobi solver for small models and Bathe's subspace iteration (with
Jacobi on the projected problem and a Sturm check) for larger ones, as Frame3DD does.
MRSA: participation factors, SRSS/CQC (Der Kiureghian), scaling to 100% of the ELF base shear.
Time history: Newmark average acceleration with Rayleigh damping (Chopra Table 5.4.2 form),
reproduced here to 1e-13 against modal superposition. No keyless, clearly redistributable
digital copy of the 1940 El Centro record was found; shipping one is an owner's decision.

**Recommendation.** Build ELF Method 2 first (it needs only SDS, SD1, S1, TL from the service,
or typed values for sites outside the US), then modes (Jacobi, then subspace), then MRSA with
CQC and the 100% scaling, then Newmark. Keep the code-dependent numbers (Ct, x, Cu, R, Cd,
Omega0, Ie, drift limits, combination factors) in the V167 registry with the edition. Several
Table 12.2-1 cells and one load-combination factor are still U (section 10) and must be read in
the owner's copy of ASCE 7-22 before code relies on them.

## 2. The question and the hypotheses

| # | Hypothesis (falsifiable) | Outcome | Evidence |
|---|---|---|---|
| H1 | The USGS ASCE 7-22 service can be called from the app's https page with no proxy. | **Partly held.** CORS `*` is sent when the request carries an Origin, but a CloudFront copy cached from an Origin-less request has no CORS header and is served to browsers for up to 900 s. OPTIONS answers 405 (so only simple GETs work). The legacy `/ws/designmaps/asce7-22.json` answers 301 to an `http://` URL (mixed content). | Experiment E1, section 6 |
| H2 | ASCE 7-22's ELF uses the 7-16 two-period formulas unchanged. | **Partly falsified.** The formulas survive as Method 2, but SDS and SD1 are redefined from the multi-period spectrum (21.4), Method 1 is new, equation numbers moved (Cs Method 1 is 12.8-2; Ta 12.8-8; Fx 12.8-12; Cvx 12.8-13), and ASCE's errata touch 12.8. | NEHRP 2020 Part 1; Ghosh (ICC 2025); Rudra and Ghosh; ICC course; FEMA P-2192 |
| H3 | MRSA in 7-22 is scaled to 100% of the ELF base shear, not 85%. | **Held (S).** 100% since 7-16; the 2020 NEHRP commentary explains it; 7-22's own 12.9.1.4.1 text not read. Drift scaling only where Cs came from the 0.5S1 bound. | NEHRP 2020 C12.9.1.4.1 and Part 1 12.9.1.4.2 |
| H4 | A plain generalized Jacobi solver (ES5-portable loops) matches a library eigensolver to better than 1e-9 on a small frame. | **Held.** 10-dof: 1.7e-12 relative, M-orthonormal to 6e-16, 7 sweeps. | Experiment E3 |
| H5 | Newmark average acceleration reproduces Chopra's worked SDOF table and does not dissipate energy. | **Held.** Computed values equal the table values recalled for Chopra's Example 5.3 to 4 decimals; amplitude kept over 20 periods; period elongation 0.82% at dt = T/20, as theory. The book itself was not read (U). | Experiment E4 |
| H6 | A public-domain 1940 El Centro record can be downloaded keylessly and shipped. | **Falsified as tested.** CESMD datasets need a registered e-mail; PEER needs an institutional login and limits downloads citing copyright; vibrationdata.com refuses scripts (406). The original record is a U.S. Coast and Geodetic Survey instrument's (S), so the record is probably a US government work, but the digitized copies' provenance is not settled. | Experiment E5, section 4.8 |

## 3. Method

### 3.1 Search log

| # | Where | Query or request | Came back | Kept / set aside |
|---|---|---|---|---|
| 1 | earthquake.usgs.gov | `/ws/building-codes/asce7-22/calculate` lat 34 lon -118, all site and risk classes, errors, CORS, OPTIONS, legacy path | JSON, 422 enum errors, 200-with-error for out-of-bounds, CORS behaviour | Kept: E1, samples saved |
| 2 | earthquake.usgs.gov | `/ws/building-codes/asce7-22/swagger` | OpenAPI 3.1 with field definitions | Kept (P for the service) |
| 3 | earthquake.usgs.gov | `/ws/building-codes/` docs page | Angular app shell, `main-*.js` | Set aside (no prose) |
| 4 | www.usgs.gov | seismic design web services page; copyrights page | 403 to curl; WebFetch 404 and a digest | Copyright digest kept (S) |
| 5 | Web search | FEMA P-2082-1 NEHRP 2020 provisions pdf | fema.gov 403; nibs.org/files 404; nibs.org wp-content copy 200 | Kept: P-2082-1 (593 pp.) |
| 6 | nibs.org | FEMA P-2192-V1 design examples (2021) | 457 pp., cites ASCE/SEI 7-22 throughout | Kept |
| 7 | wbdg.org | FEMA P-750 (2009) | text without tables | Set aside |
| 8 | Web search | "ASCE 7-22 Ct Cu Table 12.8-1 ..." | ICC BSJ articles (Ghosh), Rudra and Ghosh paper, ICC course PDF, Tekla page | Kept ICC items; Tekla answered 202 (empty) |
| 9 | iccsafe.org | the three ICC documents | 200 | Kept (S) |
| 10 | Web search | "Table 12.8-1 Coefficient for Upper Limit ..." | IISEE (kenken.go.jp), Bentley RAM docs, kim2kie | Bentley and IISEE kept; kim2kie TLS failure |
| 11 | docs.bentley.com | RAM ASCE 7-16 ELF pages (12 topics) | 200 | Kept (S, practice) |
| 12 | Web search, then nvlpubs.nist.gov | NIST GCR 16-917-41 (steel SMF brief) | 200 | Kept (R = 8) |
| 13 | Web search, shop.iccsafe.org | ICC/SEAOC concrete SMF design example sample | 200 | Kept (R, Omega0, Cd, Ct) |
| 14 | wbdg.org | UFC 3-301-01 | 403 | Refused |
| 15 | idecad.atlassian.net, amplify.asce.org | Table 12.2-1 reproductions | 202 empty; redirect loop | Refused |
| 16 | raw.githubusercontent.com | JWock82/Pynite `FEModel3D.py`, `LICENSE` | 200 | Kept (MIT) |
| 17 | raw.githubusercontent.com | hpgavin/frame3dd `main.c`, `frame3dd.c`, `frame3dd_io.c`, `LICENSE`; `eig.c` from pslack/frame3dd fork | 200; eig.c 404 in hpgavin, 200 in fork | Kept (GPL-3, method only) |
| 18 | api.github.com, codeload.github.com | trees, tarball | 403 (session not bound to those repos) | Refused |
| 19 | raw.githubusercontent.com | OpenSees `COPYRIGHT`, `ResponseSpectrumAnalysis.cpp`, `Newmark.cpp` | 200 | Kept (licence: non-commercial; method only) |
| 20 | readthedocs (OpenSeesPy) | `responseSpectrumAnalysisExample.py` | 200 | Kept (CQC code; a units slip found) |
| 21 | nehrpsearch.nist.gov | Der Kiureghian, UCB/EERC-80/15 (1980) | 200, OCR garbles equations | Kept for context only |
| 22 | nrc.gov | ML060870067 (CQC) | 403 | Refused |
| 23 | edwilson.org | Wilson's book chapters | 404 | Refused |
| 24 | gh search | "modal analysis"/"response spectrum" JS/TS repos | mhaseebmohal/structural-frame-analysis (MIT), lambdaclass/stabileo (AGPL-3) | Kept as prior art |
| 25 | uiowa.edu, utpl.edu.ec | Newmark lecture notes | equations are images | Set aside |
| 26 | Web search | Chopra Example 5.3 numbers | no reproduction found | U; recomputed instead |
| 27 | strongmotioncenter.org | `/wserv/` docs, events, records, data policy, VDC event 88 | metadata 200 with CORS `*`; dataset 400 "registered e-mail" | Kept (E5) |
| 28 | vibrationdata.com | `elcentro_NS.dat`, `elcentro.htm` | 406 Mod_Security | Refused |
| 29 | ngawest2.berkeley.edu | home page | login, institutional e-mail, download caps | Kept (terms) |
| 30 | law.cornell.edu | 17 U.S.C. 105 | 200 | Kept (P for the law text) |
| 31 | Web search | 1940 El Centro instrument | USGS OF 87-672 says a USC&GS accelerograph was installed 1932 | Pointer; S |
| 32 | Web search | "0.15S" seismic combination ASCE 7-22 | no confirming source | U (see 4.1) |
| 33 | csiamerica wiki | scale-factor article | 202 JS challenge; WebFetch empty | Refused |

Refused or unreachable hosts, recorded: www.fema.gov (403), www.usgs.gov (403 to scripts),
wbdg.org UFC (403), idecad.atlassian.net (202 empty), amplify.asce.org (redirect loop),
support.tekla.com (202 empty), kim2kie.com (TLS), www.nrc.gov (403), edwilson.org (404),
vibrationdata.com (406), web.wiki.csiamerica.com (202 JS challenge), api.github.com and
codeload.github.com for repos not bound to this session (403).

### 3.2 Sources by kind

- Standard or its federal basis: FEMA P-2082-1 (2020 NEHRP Provisions, Part 1 and Part 2), the
  stated basis of ASCE 7-22's seismic chapters; ASCE 7-22 itself is sold and was not read.
- Service: USGS ASCE 7-22 web service and its OpenAPI.
- Practitioner documents: FEMA P-2192-V1 (examples to ASCE 7-22), ICC's course and Ghosh's
  articles on 7-22, Bentley RAM's ASCE 7-16 manual, the ICC/SEAOC example, NIST GCR 16-917-41.
- Open implementations read as text: PyNite (MIT), Frame3DD (GPL-3), OpenSees (UC non-commercial
  licence), OpenSeesPy example, structural-frame-analysis (MIT, JS), stabileo (AGPL-3).
- Experiments here: E1 to E5 below, and `seismic.py`.

### 3.3 Independent check

Not yet done: the protocol's second reader must re-read the sources behind every fact in
section 4 marked for code use. Until then the levels below are this agent's own.

## 4. Findings, by topic

Units: the app is kN, m, s, so mass is in tonnes (1 t = 1 kN s2/m). A member's mass per metre is
rho A / 1000 t/m with rho in kg/m3 (the app's `bimStructLoads` uses rho A g / 1000 kN/m for the
weight; `analytical-model.js` line 195, g = 9.80665 at line 160).

### 4.1 ASCE/SEI 7-22: ground motion, ELF, load effects

| Fact | Value | Source, section | Level | Conf. |
|---|---|---|---|---|
| Site classes | A, B, BC, C, CD, D, DE, E, F (BC, CD, DE new in 7-22) | P-2082-1 Part 1, 11.4.2; P-2192 1.4.1 | P (NEHRP) / S (7-22) | high |
| Default site class | most critical of C, CD, D (7-16: D) | P-2082-1 11.4.2.1; P-2192 1.4.1 | P / S | high |
| SS, S1, SMS, SM1 | from the USGS Seismic Design Geodatabase (doi 10.5066/F7NK3C76) via the USGS web service | P-2082-1 11.4.3 | P / S | high |
| SDS, SD1 | 2/3 SMS, 2/3 SM1 (Eqs. 11.4-1, 11.4-2) | P-2082-1 11.4.4 | P / S | high |
| SMS, SM1 from the multi-period spectrum | SDS = 0.9 x max Sa over 0.2 to 5 s; SD1 = 0.9 x max T Sa over 1 to 2 s (vs30 > 442 m/s) or 1 to 5 s (vs30 <= 442 m/s), not less than Sa(1 s); SMS, SM1 = 1.5 x | P-2082-1 21.4; Ghosh BSJ 2025; P-2192 1.4.1 (P-2192 omits the 90% in one bullet: a slip) | P / S | high; reproduced by E2 to 0.002 g |
| Design spectrum required | multi-period (11.4.5.1) unless site-specific or not available, then two-period (11.4.5.2) | P-2082-1 11.4.5 | P / S | high |
| Multi-period spectrum | 2/3 of the MCER spectrum at 22 periods 0 to 10 s; linear between; beyond 10 s, Sa(10) x 10/T up to TL, Sa(10) x 10 TL/T2 beyond | P-2082-1 11.4.5.1 | P / S | high |
| Two-period spectrum | T < T0: SDS (0.4 + 0.6 T/T0); T0 to TS: SDS; TS to TL: SD1/T; > TL: SD1 TL/T2; T0 = 0.2 SD1/SDS; TS = SD1/SDS | P-2082-1 11.4.5.2; USGS answer (Sa(0) = 0.58 = 0.4 x 1.46) | P / S | high |
| MCER spectrum | 1.5 x design spectrum | P-2082-1 11.4.6 | P / S | high |
| ELF in 7-22 | Method 1 or Method 2 where the multi-period spectrum is available; Method 2 only where it is not (11.4.5 Exception 2); lower bounds apply to both | ICC course (quotes 12.8.1.1); Ghosh BSJ; Rudra and Ghosh | S | high |
| Method 1 | Cs = Sa(T)/(R/Ie), Sa from 11.4.5.1 at the period of 12.8.2; for T below the period of peak Sa, use the peak Sa (Eq. 12.8-2) | ICC course; Rudra and Ghosh | S | high |
| Method 2 | Cs = SDS/(R/Ie) (12.8-3), need not exceed SD1/(T R/Ie) for T <= TL, SD1 TL/(T2 R/Ie) for T > TL | ICC course; Rudra and Ghosh; P-2192 examples; Bentley (7-16 form) | S | high |
| Lower bounds | Cs >= 0.044 SDS Ie >= 0.01; where S1 >= 0.6, Cs >= 0.5 S1/(R/Ie); S1 is the mapped value (USGS `s1`, Site Class BC) | Rudra and Ghosh; Bentley; P-2082-1 21.4 (mapped S1); USGS OpenAPI (s1 is Site Class BC) | S | high. P-2192 ch. 4 writes "S1 > 0.6"; the others ">= 0.6" |
| Max SDS cap (12.8.1.3) | still in 7-22 (Cs and Ev may use SDS = 1.0 but >= 70% of SDS under six conditions) | ICC course slide title; Bentley (7-16 text) | S | medium; conditions not read |
| Ta | Ct hn^x (7-22 Eq. 12.8-8); hn in ft in the US table | P-2192 ch. 6, 8; ICC/SEAOC sample; Bentley | S | high |
| Ct, x (Table 12.8-2, ft) | steel MRF 0.028, 0.8; concrete MRF 0.016, 0.9; steel EBF and BRBF 0.030, 0.75; all other 0.020, 0.75 | Bentley (7-16); P-2192 (0.028/0.8, 0.02/0.75, 0.03/0.75 citing 7-22); ICC/SEAOC (0.016/0.9) | S | high |
| Ct in SI (m) | 0.0724, 0.0466, 0.0731, 0.0488: exactly Ct_ft x 3.28084^x | E2 arithmetic; agrees with structural-frame-analysis's table | S | high. IISEE's metric column (0.068, 0.044, 0.070, 0.055) disagrees; it is an older edition or a slip: do not use |
| Cu (Table 12.8-1) | SD1 >= 0.4: 1.4; 0.3: 1.4; 0.2: 1.5; 0.15: 1.6; <= 0.1: 1.7 | Bentley (7-16); IISEE (adds a 0.05 row, 1.7); P-2192 uses 1.4 at SD1 = 0.65 citing 7-22 | S | high for values; whether to interpolate between rows is U |
| T used | T <= Cu Ta; T = Ta permitted without analysis | Bentley; P-2192 ch. 4, 5; commentary C12.8.2 | S | high |
| k | 1 for T <= 0.5 s; 2 for T >= 2.5 s; linear between | Bentley; ICC example (T 0.77, k 1.14) | S | high |
| Fx, Cvx | Fx = Cvx V; Cvx = wx hx^k / sum wi hi^k (7-22 Eqs. 12.8-12, 12.8-13) | Bentley (7-16 numbers 12.8-11, -12); ICC course (7-22 numbers) | S | high |
| SDC A | ELF not required: Fx = 0.01 Wx (Eq. 1.4-1) | Bentley (7-16) | S | medium (7-22 text not read) |
| SDC | from SDS and SD1 (Tables 11.6-1, 11.6-2) and S1 >= 0.75 (E for RC I-III, F for IV); USGS returns `sdc` | Bentley tables; USGS answers (E/F at S1 1.15; D at a rounded 0.75) | S | high; use USGS's `sdc` |
| Ie (Table 1.5-2) | RC I, II: 1.0; III: 1.25; IV: 1.5 | P-2192 (1.0, 1.25, 1.5 cited to 7-22 Table 1.5-2); ICC/SEAOC (1.0, RC II) | S | high |
| Analysis procedure selection | Table 12.6-1 deleted in 7-22: ELF, MRSA or LRHA permitted for any building | P-2082-1 Part 1, 12.6; P-2192 1.4.5 | P / S | high |
| E | E = Eh + Ev (additive) or Eh - Ev; Eh = rho QE; Ev = 0.2 SDS D (7-22 Eq. 12.4-4a) | P-2192 (several examples citing 7-22) | S | high |
| Strength combinations (2.3.6) | 1.2D + Ev + Eh + L + c S; 0.9D - Ev + Eh | P-2192 shows c = 0.2 citing 7-22; ICC's 2024 course shows 0.2 struck through and **0.15** as the 7-22 code change | S, **conflict** | low: U until 2.3.6 of 7-22 (with errata) is read |

**7-22 changes from 7-16 that matter here.** Intermediate site classes and the multi-period
spectrum (site coefficients Fa and Fv are gone); SDS and SD1 defined by 21.4 from the spectrum,
not at 0.2 s and 1 s; ELF Method 1 added; Table 12.6-1 removed; the mass irregularity removed;
equation numbers shifted in 12.8; deformation compatibility uses drifts amplified by R; design
earthquake displacement includes diaphragm deformation (12.8.6.3, Eq. 12.8-15:
delta_DE = Cd delta_e / Ie + delta_di); the extreme torsional irregularity no longer prohibited
in SDC E and F; probably 0.15S in the seismic combinations (U). Sources: P-2192 1.4; P-2082-1
Part 1 12.8.6, 12.12; ICC course.

**Counter-evidence searched.** Ghosh (BSJ, December 2025) records "significant confusion" about
whether the two-period spectrum may still be used; his reading is that it may for ELF only.
Rudra and Ghosh find neither method uniformly larger: Method 1 larger at very short periods
(peaks below 0.2 s), Method 2 often larger at intermediate periods; a 2027 IBC proposal would
make them equal up to the peak. In the example below Method 1 gives V 11% lower than Method 2.
ASCE's errata for 12.8 exist and were not read (U).

### 4.2 Response modification factors (Table 12.2-1)

| System | R | Omega0 | Cd | Source | Level |
|---|---|---|---|---|---|
| Steel special moment frame | 8 | 3 | 5.5 | R: NIST GCR 16-917-41, P-2192; Omega0: P-2192 (cites 7-22); Cd: none read | R, Omega0 S; **Cd U** |
| Steel ordinary moment frame | 3.5 | 3 | 3 | a search digest of idecad's table only | **U** |
| Concrete special moment frame | 8 | 3 | 5.5 | ICC/SEAOC example (2024 IBC, ASCE 7) | S |
| Concrete ordinary moment frame | 3 | 3 | 2.5 | search digest only (Cd truncated) | **U** |
| Special RC shear wall, bearing wall | 5 | 2.5 | 5 | R, Omega0: P-2192 (cites 7-22); Cd none read | R, Omega0 S; Cd U |
| Special RC shear wall, building frame | 6 | 2.5 | 5 | R: ICC course example (B4); others none read | R S; others U |
| New in 7-22 (for the record) | RC ductile coupled walls 8 / 2.5 / 8; steel-concrete coupled composite plate shear walls 8 / 2.5 / 5.5; CLT shear walls 3 / 3 / 3 and 4 / 3 / 4 | P-2082-1 Part 1 Table 12.2-1; P-2192 | P / S |

The table is sold; the exit rule needs the owner's copy for every U cell.

### 4.3 Storey drift

| Fact | Value | Source | Level | Conf. |
|---|---|---|---|---|
| Design storey drift | difference of delta_DE at the centres of mass top and bottom; delta_DE = Cd delta_e / Ie (+ diaphragm term) | P-2082-1 Part 1 12.8.6.3-12.8.6.4 | P / S | high |
| Forces for drift | the ELF forces, strength combinations; period may be the computed T without the Cu Ta cap (12.8.6.2) | P-2082-1 12.8.6.1-2; Bentley | P / S | high |
| Allowable drift, Table 12.12-1 | 4 storeys or less with partitions designed for the drift (not masonry): 0.025 / 0.020 / 0.015 hsx (RC I-II / III / IV); masonry cantilever shear walls 0.010 all; other masonry shear walls 0.007 all; all other structures 0.020 / 0.015 / 0.010 | P-2082-1 Part 1 Table 12.12-1 | P / S | high |
| Moment frames in SDC D-F | Delta <= Delta_a / rho (12.12.1.1) | NIST GCR 16-917-41; Table 12.12-1 note b | S | high |
| MRSA drifts | multiplied by Cs W / Vt only where Cs came from the 0.5 S1 bound (Eq. 12.8-6 in 7-16 numbering) | P-2082-1 Part 1 12.9.1.4.2; C12.9.1.4.2 | P / S | high |

### 4.4 The USGS seismic design service (tested here, P)

- Endpoint: `https://earthquake.usgs.gov/ws/building-codes/asce7-22/calculate?latitude=&longitude=&riskCategory=&siteClass=&title=`.
  OpenAPI 3.1 at `.../asce7-22/swagger` ("ASCE7-22 Web Services", version 0.1.0). Backend
  `erp-design-ws` 1.2.4 and `nshmp-utils-py` 1.3.0 (code.usgs.gov), named in every answer.
- Fields (`response.data`): `pgam, sms, sm1, sds, sd1, sdc, ss, s1, tl, ts, t0, cv`, and
  `multiPeriodDesignSpectrum`, `multiPeriodMCErSpectrum` (22 periods, 0 to 10 s),
  `twoPeriodDesignSpectrum`, `twoPeriodMCErSpectrum` (184 points to 9 s),
  `verticalDesignSpectrum`, `verticalMCErSpectrum` (empty with `cv: null` at both test sites),
  `underlyingData` (`pgauh, pga84th, riskTargetedSpectrum, eightyFourthSpectrum`). Values to
  2 decimals (ts, t0 to 3-4). The OpenAPI says `ss` and `s1` are for Site Class BC; `sds`,
  `sd1` are those of the two-period spectrum for the chosen class.
- Site classes accepted: A, B, BC, C, CD, D, DE, E, DEFAULT (any case). `D-default` and
  `B-estimated` pass the validator and then fail ("not supported for ASCE7-22"); F and others:
  HTTP 422 with a FastAPI `detail` array.
- Risk categories: I, II, III, IV, and an undocumented `N` (returns `sdc: "N"`). RC changes
  only the SDC, not the accelerations.
- Out of range (Pacific at 30 N 140 W; London; latitude 95): **HTTP 200** with
  `request.status: "error"` and `response: "Location [lon, lat] out of bounds"`. Alaska,
  Hawaii, Puerto Rico and Guam answer. Missing parameters: `status: "usage"` and a long listing.
- Timing: 1.2 to 2.0 s uncached (14 requests); 0.15 to 0.2 s for errors and cache hits.
  Answer size about 16 to 19 kB. `cache-control: max-age=900`, CloudFront, API Gateway.
- CORS: a GET with an Origin gets `Access-Control-Allow-Origin: *` on a cache miss. A cache entry
  created by a request without Origin carries no CORS header, and later browser requests for the
  same URL get that copy (shown twice: E1 steps 1-2). `Vary` lists only Accept-Encoding.
  `Origin: null` (a `file://` page) gets no header. OPTIONS: 405. Mitigation: never add custom
  headers (stay a simple request), and add a unique `title` value per request; extra parameters
  are ignored.
- Legacy `https://earthquake.usgs.gov/ws/designmaps/asce7-22.json?...` answers 301 to
  `http://earthquake.usgs.gov/ws/building-codes/...` which then upgrades; a browser on https
  would refuse the http hop as mixed content (the hop measured here; browser refusal not tested).
- Terms: USGS states its data are U.S. public domain and asks for credit (usgs.gov copyrights
  page, read through WebFetch's digest because the site refuses scripts: S). No key, no stated
  rate limit seen.
- Checks: SDS and SD1 recomputed from the multi-period spectrum by 21.4 match USGS (1.458 vs
  1.46; 0.700 vs 0.70), TS = SD1/SDS, T0 = 0.2 TS, Sa(0) of the two-period spectrum = 0.4 SDS.

| Site (Site Class C, RC II) | SS | S1 | SDS | SD1 | TL | SDC |
|---|---|---|---|---|---|---|
| 34, -118 (LA) | 2.15 | 0.75 | 1.46 | 0.70 | 8 | D |
| 34.3, -117.5 | 2.79 | 1.15 | 1.94 | 1.09 | 8 | E (F for RC IV) |
| 61.2, -149.9 (Anchorage) | 1.50 | 0.65 | 1.03 | 0.59 | 16 | D |
| 21.3, -157.8 (Honolulu) | 0.54 | 0.15 | 0.39 | 0.15 | 4 | C |
| 40.7, -74.0 (NYC) | 0.27 | 0.05 | 0.18 | 0.043 | 6 | B |

LA by site class (SDS / SD1): A 0.88/0.31, B 1.02/0.36, BC 1.29/0.50, C 1.46/0.70,
CD 1.51/0.95, D 1.45/1.13, DE 1.29/1.43, E 1.21/1.72, Default 1.51/1.13 (= the worst of C, CD, D
per parameter: SDS from CD, SD1 from D).

### 4.5 Modal analysis

| Fact | Value | Source | Level | Conf. |
|---|---|---|---|---|
| Problem | K phi = w2 M phi on the free dofs; T = 2 pi / w | PyNite `analyze_modal` (cites Hart and Wong 4.96); Frame3DD | P (code) | high |
| Lumped mass (Frame3DD `lumped_M`) | each end gets (rho A L + extra)/2 in each translation; rotations get rho L J/2 (torsion) and rho Iy L/2, rho Iz L/2 transformed to global | Frame3DD `frame3dd.c` lines 751-781 | P (GPL-3: method only) | high |
| Consistent mass | PyNite uses it for member self-weight; nodal masses translational only; Frame3DD offers both (`lump` flag) | PyNite `FEModel3D.M`; Frame3DD | P | high |
| Massless dofs | PyNite adds eps = 1e-6 x smallest positive diagonal mass to zero diagonals; Frame3DD's lumped rotary inertia makes M positive definite; structural-frame-analysis adds 1e-10 relative | PyNite lines 2106-2128; JS repo `modes.js` 181 | P | high |
| Supports | PyNite partitions them out; Frame3DD keeps them with K_ii = 1e4 trace(K), M_ii = trace(M), off-diagonals zeroed | as above | P | high |
| Solver: PyNite | SciPy `eigsh` shift-invert (sigma 0), ARPACK Lanczos | PyNite line 2536 | P | high |
| Solver: Frame3DD | Bathe's subspace iteration with generalized Jacobi on the projected matrices and a Sturm sequence check (or Stodola with shifting); q = min(p + 8, 2p) trial vectors; shift for rigid-body modes | Frame3DD `eig.c`, `main.c` 643-681 | P | high |
| Solver: OpenSees | ARPACK (`-genBandArpack`) | OpenSeesPy example | P | high |
| Solver: structural-frame-analysis (JS, MIT) | Bathe subspace iteration, Cholesky reduction + Jacobi on the projected problem | `modes.js` header and functions | P | high |
| Participation | Gamma_n = phi_n' M iota / phi_n' M phi_n; effective mass M*_n = (phi_n' M iota)2 / phi_n' M phi_n; sum over all modes = total mass in that direction | Frame3DD `write_modal_results` (mpf = sum V ms with mass-normalised V); E3 | P / measured | high |
| Number of modes (12.9.1.1) | enough for 100% of the mass, with modes of T <= 0.05 s allowed as one residual rigid mode at 0.05 s, or (exception) at least 90% in each direction | P-2082-1 commentary C12.9.1.1 (7-16 based) | S for 7-22 | medium-high |
| Residual-mode Sa | Sa(0.05) = SDS (0.4 + 0.15/TS) for the two-period spectrum | C12.9.1.1 | S | medium |
| Practice | Bentley RAM: engineer must confirm 90%; Ritz vectors include missing mass; subspace does not | Bentley RAM RSA page | S | high |

**Licences.** PyNite MIT (code reusable with notice). Frame3DD GPL-3 (method only: it cannot be
joined into the app under the owner's rule). OpenSees: UC Regents, non-commercial and internal use
only (method only). structural-frame-analysis MIT (2026, small, young: read, not trusted).
stabileo AGPL-3 (method only).

### 4.6 Response spectrum analysis

| Fact | Value | Source | Level | Conf. |
|---|---|---|---|---|
| Modal peak | per mode, Sa(Tn) Ie/R (in g) times Gamma_n phi_n; base shear V_n = Sa_n g M*_n Ie/R | C12.9.1.2 (division by R, multiplication by Ie); standard modal analysis | S | high |
| Spectrum in 7-22 | the multi-period spectrum (two-period only for ELF or where multi-period unavailable) | Ghosh quoting Soules and Guglielmo 2025; 11.4.5 | S | high |
| SRSS / CQC | either; CQC with the spectrum's damping, 5% | C12.9.1.3 | S | high |
| CQC coefficient (Der Kiureghian 1981) | rho_ij = 8 sqrt(zi zj)(zi + r zj) r^1.5 / [(1 - r2)2 + 4 zi zj r (1 + r2) + 4 (zi2 + zj2) r2], r = wj/wi; equal damping: 8 z2 (1 + r) r^1.5 / [(1 - r2)2 + 4 z2 r (1 + r)2] | OpenSeesPy example (general form); structural-frame-analysis (equal form); E3 shows they agree and are symmetric | S | high (paper's equations unreadable in the OCR) |
| Counter-evidence | the OpenSeesPy example passes eigenvalues (w2) where the formula wants w: for r = 0.382 it gives rho 0.0013 instead of 0.0089 | E3 | P | high |
| Orthogonal directions | 100% + 30%, or SRSS of the two directional results | C12.9.1.3 | S | medium |
| Scaling forces | where Vt < V (ELF), multiply forces by V/Vt (100%; 7-10 used 85%) | C12.9.1.4.1 | S | high |
| Practice | CSI's old article (ASCE 7-05): scale factor I g / R and 85%: an outdated edition, as a forum digest reports | search digest only | U | - |

### 4.7 Linear response history

| Fact | Value | Source | Level | Conf. |
|---|---|---|---|---|
| Newmark, incremental (linear) | k^ = k + gamma/(beta dt) c + m/(beta dt2); a = m/(beta dt) + gamma/beta c; b = m/(2 beta) + dt (gamma/(2 beta) - 1) c; du = (dp + a v + b a_acc)/k^; dv = gamma/(beta dt) du - gamma/beta v + dt (1 - gamma/(2 beta)) a_acc; da = du/(beta dt2) - v/(beta dt) - a_acc/(2 beta) | Chopra, Dynamics of Structures, Table 5.4.2 (from memory, U); OpenSees `Newmark.cpp` coefficients c2 = gamma/(beta dt), c3 = 1/(beta dt2), a1 = 1 - gamma/beta, a2 = dt (1 - gamma/(2 beta)), a3 = -1/(beta dt), a4 = 1 - 1/(2 beta); reproduced to 1e-13 in E4 | P (code) + measured | high |
| Average acceleration | gamma 1/2, beta 1/4: unconditionally stable, no amplitude decay, period elongation about (w dt)2/12 | uiowa lecture 16 (stability statement); E4 measured 0.817% at dt = T/20 | S + measured | high |
| Rayleigh damping | C = a0 M + a1 K; with zeta at wi and wj: a0 = zeta 2 wi wj / (wi + wj), a1 = zeta 2 / (wi + wj) | E3 (checked both target modes); textbook form | S (Chopra not read) + measured | high |
| MDOF | the same recurrences with matrices (Chopra Table 16.3.3 form); p = -M iota ag | E4: equals modal superposition to 3e-13 | measured | high |
| ASCE 7-22 LRHA (12.9.2) | not read: ground-motion selection, scaling and the number of records | - | U | - |

### 4.8 Ground-motion records

| Source | Keyless? | CORS | Terms read | Verdict |
|---|---|---|---|---|
| CESMD web services (strongmotioncenter.org/wserv) | metadata yes; datasets need a registered e-mail (400 "E-mail parameter not supplied") | `*` | Data attribution and use policy (2015): serves only data the owners deem public; asks for citation (doi 10.5066/P13HTZQS) and attribution; no warranty; no licence stated | metadata usable; the record needs the owner to register |
| CESMD VDC (event 88, El Centro 1940) | download bin needs login | - | as above | 180 component PGA 341.69 cm/s2, 270 component 210.14 cm/s2; CESMD records metadata gives 0.359 and 0.349 g (processing versions differ) |
| PEER NGA-West2 | login, institutional e-mail, yearly membership from 2026-07-02, caps "due to copyright issues" | not tested | home page | not keyless, not redistributable as far as stated |
| vibrationdata.com | refuses scripts (406) | - | not read | refused |
| GitHub copies | many repositories carry PEER-processed El Centro files (e.g. RSN6 ELC180) | - | their provenance is PEER's | do not ship from these |

The 1940 record: USGS OF report (search pointer) says a U.S. Coast and Geodetic Survey standard
accelerograph was installed at 302 Commercial Ave., El Centro, in 1932; CESMD lists the station
as USGS 0117. 17 U.S.C. 105(a) (read, P): copyright is not available for works of the US
Government; USGS calls its data public domain (S). So the analog record is very probably public
domain (S); the widely used digitized and corrected series (Caltech EERL 1975, PEER) were made
by others, and their status is not settled (U). The script `seismic.py` uses a synthetic
half-sine ground pulse instead.

## 5. The alternatives compared

Criteria, fixed before the comparison: plain ES5 without a library; accuracy for frames of up to
a few thousand dofs; memory in a browser; how much new code; fit with the app's banded storage.

| Eigensolver | ES5, no library | Accuracy | Scale | New code | Fits banded K | Verdict |
|---|---|---|---|---|---|---|
| Generalized Jacobi on full K, M (Bathe 11.3.3) | yes | all modes, machine precision (E3) | O(n3) per sweep: fine to about 200 dofs | small (about 60 lines) | no (dense) | first step and test oracle |
| Subspace iteration (Bathe) with Jacobi on the projected q x q problem, Sturm check | yes | the lowest p modes to tolerance; Sturm check proves none missed | uses the existing banded Cholesky of K; O(n b q) per iteration | medium | yes | **recommended** for real models (Frame3DD, the MIT JS repo) |
| Inverse iteration with shifting and Gram-Schmidt deflation | yes | good for a few modes; deflation drifts for many | banded | small | yes | fallback for "first 3 modes" |
| Lanczos (ARPACK style, shift-invert) | yes, but reorthogonalisation is delicate | best for many modes | banded | large | yes | not now (PyNite and OpenSees use it through libraries) |
| A WASM library (e.g. a LAPACK build) | no (needs a vetted library per the 2026-11-13 rule) | best | best | adapter only | - | only if the owner approves a library |

| Ground-motion data | Keyless | Redistributable | Effort | Verdict |
|---|---|---|---|---|
| Ship one 1940 El Centro record (owner downloads from CESMD with a registered e-mail, we commit it with credit) | no (one-time) | probably (US Gov work, S) | small | owner decides |
| Ask the user to load their own record (CSV, PEER AT2) | yes | n/a | small | **recommended** in any case |
| Synthetic pulses and harmonic ground motion only | yes | yes | smallest | for tests and teaching |

| ELF method | Inputs | Edges | Verdict |
|---|---|---|---|
| Method 2 (two-period) | SDS, SD1, S1, TL (service or typed) | works outside the US with typed values | **build first** |
| Method 1 (multi-period) | 22-point spectrum (service) | US only; peak-Sa rule below the peak period | second; show both when the spectrum is available |

## 6. The experiments

**E1, the USGS service (2026-11-21, curl 8 on Linux through the session proxy).** 30+ requests.
Raw: three answers saved (`usgs-asce7-22-la-siteC-rcII.json`, `usgs-asce7-22-nyc-siteD-rcII.json`,
`usgs-asce7-22-ocean-error.json`). The CORS sequence, with a fresh `title` each time:
(1) no Origin: miss, no ACAO; (2) same URL with Origin: hit, **no ACAO**; (3) new URL with
Origin: miss, ACAO `*`; (4) other Origin: hit, ACAO `*`; (5) no Origin: hit, ACAO `*`; (6)
OPTIONS: 405. Not tested: a real browser (fetch from an https page), a phone.

**E2, ELF (seismic.py part a).** 4 storeys of 3.5 m, 2000 kN each, steel SMF (R 8, Cd 5.5,
Omega0 3, Ie 1.0), lat 34, lon -118, Site Class C, RC II: SDS 1.46, SD1 0.70, S1 0.75, TL 8.
hn = 14 m = 45.932 ft; Ta = 0.028 x 45.932^0.8 = 0.5982 s; Cu = 1.4; Cu Ta = 0.8375 s; T = Ta.
Method 2: SDS/(R/Ie) = 0.1825; SD1/(T R/Ie) = 0.1463 (governs); 0.044 SDS Ie = 0.0642;
0.5 S1/(R/Ie) = 0.0469. Cs = 0.1463, W = 8000 kN, **V = 1170.2 kN**. Method 1: Sa(0.598) by
linear interpolation = 1.0439 g, Cs = 0.1305, V = 1043.9 kN. k = 1 + (0.5982 - 0.5)/2 = 1.0491.

| Level | hx (m) | wx hx^k | Cvx | Fx (kN) | Storey shear (kN) |
|---|---|---|---|---|---|
| 4 | 14.0 | 31873.9 | 0.4071 | 476.4 | 476.4 |
| 3 | 10.5 | 23570.1 | 0.3011 | 352.3 | 828.7 |
| 2 | 7.0 | 15403.6 | 0.1967 | 230.2 | 1058.9 |
| 1 | 3.5 | 7444.1 | 0.0951 | 111.3 | 1170.2 |

Drift, with an **assumed** storey stiffness of 200 000 kN/m (shear building, m = 203.94 t per
level, computed T1 = 0.578 s): delta_xe 5.851, 5.295, 4.143, 2.382 mm; Delta = Cd delta_xe/Ie =
32.2, 29.1, 22.8, 13.1 mm; limit 0.020 hsx = 70 mm, or 53.8 mm with rho = 1.3 (12.12.1.1).

**E3, eigenproblems (part b).** 2-dof, m1 = m2 = 100 t, k1 = k2 = 40 000 kN/m: w2 = (3 -/+ sqrt5)/2
k/m = 152.7864 and 1047.2136; T = 0.50832 and 0.19416 s; phi1 = [1, 1.61803], phi2 = [1, -0.61803];
Gamma 0.72361 and 0.27639; M* = 189.443 t (94.721% = 1/2 + 1/sqrt5) and 10.557 t (5.279%).
Jacobi: exact in 2 sweeps. 10-dof (masses 120 to 80 t): Jacobi 7 sweeps, 1.7e-12. CQC (5%):
rho(1) = 1, rho(0.9) = 0.4730, rho(0.5) = 0.01849, rho(0.382) = 0.00886. Rayleigh 5% at
w1 = 12.3607, w2 = 32.3607 rad/s: a0 = 0.89443 1/s, a1 = 0.002236 s.

**E4, Newmark (part c).** Chopra's Example 5.3 data: m = 0.2533 kip s2/in, k = 10 kip/in,
zeta 5% (Tn = 1.0 s), p = 10 sin(pi t/0.6) kips for t <= 0.6 s, dt = 0.1 s.

| t (s) | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| Newmark u (in) | 0.0437 | 0.2326 | 0.6121 | 1.0825 | 1.4310 | 1.4231 | 0.9622 | 0.1908 | -0.6044 | -1.1442 |
| Exact u (in) | 0.0328 | 0.2332 | 0.6487 | 1.1605 | 1.5242 | 1.4814 | 0.9245 | 0.0593 | -0.7752 | -1.2718 |

These equal, to the last digit (1.4310 vs 1.4309), the values recalled for the book's table; the
book was not read here, so the book's numbers stay U, and the test data comes from this script.
Undamped free vibration: amplitude kept over 20 periods; period 1.00817 s at dt = T/20 and
1.03206 s at T/10, exactly 2 pi dt / (2 atan(w dt/2)). MDOF 2-dof with Rayleigh 5% under a
0.3 g half-sine ground pulse of 0.5 s (dt 0.005 s): peak roof displacement 36.133 mm; matrix
Newmark equals modal superposition to 3.2e-13.

**E5, ground-motion hosts.** As in section 4.8 (CESMD metadata query for event CI3365279:
1 station, code 117, epicentral distance 16.9 km).

## 7. Edges

- **T and the spectrum.** T < T0 in the two-period spectrum: the rising branch is not used by
  ELF Method 2 (Cs = SDS/(R/Ie) for all T <= TS) but is used by MRSA. Method 1: for T below the
  period of peak Sa use the peak. T > 10 s in the multi-period spectrum: 10/T then 10 TL/T2.
- **TL boundary.** Cs switches from SD1/T to SD1 TL/T2 at T = TL (continuous). TL = 4 to 16 s
  in the answers seen; only tall or flexible structures reach it.
- **S1 >= 0.6.** The 0.5 S1/(R/Ie) floor; S1 is the Site Class BC mapped value (`s1`), not
  SD1. At LA (S1 0.75) it gives 0.0469, below Method 2's 0.1463; it governs only for long T.
  "S1 > 0.6" in one P-2192 example: a slip against the other sources.
- **SDC thresholds.** S1 >= 0.75 makes RC I-III SDC E and RC IV SDC F. USGS rounds to 2
  decimals: at LA `s1: 0.75` came with `sdc: "D"`, so the true value is just below 0.75. Use the
  service's `sdc`, never recompute it from rounded values.
- **k interpolation.** Linear between 0.5 and 2.5 s; T for k is the same T as for Cs (with the
  Cu Ta cap), not the drift period.
- **Cu between rows.** Interpolation between Table 12.8-1 rows: practice differs (the MIT JS
  repo steps; the script interpolates). U until the table's note is read.
- **Computed T below Ta.** Allowed either way (T = Ta is permitted); in E2 the assumed-stiffness
  model's T1 0.578 s is below Ta 0.598 s.
- **SDC A.** No ELF: Fx = 0.01 Wx (1.4). Risk Category `N` in the service: `sdc: "N"`.
- **Outside the US.** Service answers "out of bounds" with HTTP 200; the app must read
  `request.status`. Method 2 with typed SDS, SD1, S1, TL; no multi-period spectrum, so Method 1
  and 7-22 MRSA (multi-period only) are not available: an owner decision whether to allow the
  two-period spectrum for MRSA as a labelled departure.
- **Massless dofs.** Rotations of a lumped-mass model: give rotary inertia as Frame3DD does, or
  a tiny diagonal (PyNite 1e-6 of the smallest mass), or condense them statically. A model with
  no mass at all: refuse with a message (PyNite raises).
- **Supports and releases.** Remove restrained dofs (the app already numbers only free dofs);
  released member ends: the condensation in `bimFrameCondense` handles K; the mass of a released
  rotation needs the same care.
- **Rigid-body modes.** An unstable frame already fails the static Cholesky; for modes use a
  shift (Frame3DD) only if mechanisms are allowed, otherwise reuse the static stability message.
- **Closely spaced modes.** SRSS under-predicts where periods are within about 10%; CQC needed
  (rho 0.47 at r = 0.9).
- **Newmark dt.** Unconditionally stable, but period error (w dt)2/12: keep dt <= T/20 of the
  highest mode that matters (0.8%), and no larger than the record's step.
- **Rayleigh damping.** Over-damps modes above the second anchor and under-damps between; the
  anchors are a user choice (modes 1 and the mode reaching 90% mass is common practice, U).

## 8. What the app already has

- `src/js/engine/structure/frame-solve.js` (287 lines): 6 dofs per node (u, v, w, rx, ry, rz),
  local stiffness `bimFrameKLocal` (lines 5-17), end releases condensed (`bimFrameCondense`,
  62-83), Reverse Cuthill-McKee ordering (85-103), equation numbering skipping fixed or pinned
  dofs (111-115), banded storage with half-bandwidth `hb`, banded Cholesky (150-165) with an
  instability message naming the node and dof. Only `bimFrameSolve` is exported. A modal solver
  can reuse the numbering, the banded K and its Cholesky factor (subspace iteration needs K^-1 x).
- `src/js/engine/structure/analytical-model.js` (226 lines): members carry `rho` (kg/m3), `sec.A`,
  E, G; g = 9.80665 (line 160); self-weight as rho A g /1000 kN/m (line 195); nodal loads only
  forces [fx, fy, fz]; a "lateral" load at a column top along X or Z; load cases D and L only
  (`bimLoadProblem`, line 173). Seismic adds case E (and Ev), storey masses and a mass source.
- `src/js/engine/standards/registry.js`: `asce7.combos` (edition ASCE/SEI 7-22, 2021-12, line
  209-210) and `asce7` (line 510): the place for Ct/x, Cu, R/Cd/Omega0, Ie, drift limits and the
  seismic combinations with their editions.
- `docs/research/experiments/physical-world/e01_eigen_speed.mjs` belongs to another agent's
  work and was not read.

## 9. Risks and threats to validity

- ASCE 7-22 itself was not read; its seismic chapters are taken from the 2020 NEHRP Provisions
  (its stated basis) and practitioners' readings of 7-22. 7-22 departs from NEHRP 2020 in places
  (P-2192 1.4.7: the height-limit exception was not adopted). Supplements and errata not read.
- Equation numbers in 7-22 are inferred from three practitioner documents that disagree in
  places (P-2192 numbers Cs 12.8-2 in one chapter and 12.8-3 in another).
- R, Cd, Omega0: several cells U (4.2).
- CORS behaviour depends on CloudFront configuration, which USGS can change at any time.
- The CQC formula's primary paper was not readable; two independent codes agree with each other.
- Chopra's book was not read; Newmark's recurrences are confirmed by OpenSees code and by exact
  reproduction, Rayleigh by algebra.
- One agent; the second reader has not checked yet.

## 10. What is still open (U)

1. The 0.15S vs 0.2S snow factor in 7-22's seismic combinations (2.3.6), and ASCE's errata.
2. Table 12.2-1 cells: Cd of steel SMF; steel OMF (3.5 / 3 / 3); concrete OMF (3 / 3 / 2.5);
   special RC shear walls (Cd 5; building frame Omega0 2.5): the owner's copy of 7-22 is needed.
3. Whether Cu is interpolated between rows of Table 12.8-1.
4. 7-22's own text of 12.9.1.1 (100% mass or residual mode, 90% exception), 12.9.1.4.1 (100%),
   12.8.1.3 conditions, and 12.9.2 (LRHA records and scaling).
5. Whether 7-22 permits the two-period spectrum for MRSA outside the US (11.4.5 Exception 2
   suggests yes where the multi-period spectrum is unavailable; Soules and Guglielmo, quoted by
   Ghosh, say MRSA uses only the multi-period spectrum).
6. Chopra's Table 5.4.2 and Example 5.3 read at the source (the numbers are reproduced here).
7. The provenance and licence of a digitized 1940 El Centro record; CESMD dataset terms after
   registration.
8. Browser CORS from a real https page and from `file://` (Origin null gets no header).
9. CSI, SkyCiv and RISA documents for how they present modes, spectra and drift (CSI refused).

## 11. The owner's decisions

1. **ELF method.** Method 2 only, or both methods side by side where the multi-period spectrum
   is available (Rudra and Ghosh: neither is always larger; E2: Method 1 11% lower)?
2. **The USGS service.** Call it from the browser with a unique `title` per request (keyless, no
   proxy, credit "U.S. Geological Survey"), and cache the answer in the project file so the app
   still works offline? Outside the US, typed SDS, SD1, S1, TL?
3. **Mass.** Lumped (Frame3DD style, with rotary inertia) or consistent; mass source: self-weight
   plus D plus a share of L (12.7.2 effective seismic weight, not researched here)?
4. **Eigensolver.** Generalized Jacobi first (small models, tests), then subspace iteration on
   the banded K, all in our own ES5 code; or approve a library?
5. **Ground motion.** Ship one 1940 El Centro component (owner registers at CESMD, the record is
   committed with CESMD's citation and USC&GS credit), or only user-loaded records and synthetic
   pulses?
6. **Code values.** Who reads the sold ASCE 7-22 tables (12.2-1, 12.8-1 note, 2.3.6) for the U
   cells before the registry carries them?

## 12. References

All read 2026-11-21.

| # | Source | URL | What was read | Level |
|---|---|---|---|---|
| R1 | USGS ASCE 7-22 web service | https://earthquake.usgs.gov/ws/building-codes/asce7-22/calculate | answers (E1); saved samples | P |
| R2 | Its OpenAPI 3.1 | https://earthquake.usgs.gov/ws/building-codes/asce7-22/swagger | endpoint description, field definitions, enums | P |
| R3 | Legacy redirect | https://earthquake.usgs.gov/ws/designmaps/asce7-22.json | 301 Location header | P |
| R4 | USGS copyrights and credits | https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits | WebFetch digest (curl 403) | S |
| R5 | FEMA P-2082-1, 2020 NEHRP Recommended Seismic Provisions, Vol. I (BSSC, Sept. 2020) | https://nibs.org/wp-content/uploads/2025/04/fema_2020-nehrp-provisions_part-1-and-part-2.pdf | Part 1: 11.4.2-11.4.7, 12.6, 12.8.6, 12.9.1.4.2, 12.12, Table 12.2-1 additions, 21.4, 21.5; Part 2: C12.8.2, C12.8.3, C12.9.1.1-C12.9.1.4.2, C21.4 | P (NEHRP) / S (for 7-22) |
| R6 | FEMA P-2192-V1, 2020 NEHRP Provisions Design Examples (Dec. 2021) | https://nibs.org/wp-content/uploads/2025/04/fema_nehrp_design-examples-and-training-materials_volume01.pdf | 1.4 key updates; ELF examples ch. 4, 5, 6, 8; load combinations | S |
| R7 | S. K. Ghosh, "Is continued use of the two-period design spectrum in the ELF procedure permitted by ASCE 7-22?", ICC Building Safety Journal, 2025-12-09 | https://www.iccsafe.org/building-safety-journal/bsj-technical/is-continued-use-of-the-two-period-design-spectrum-in-the-equivalent-lateral-force-procedure-of-seismic-design-permitted-by-asce-7-22/ | whole article | S |
| R8 | B. Rudra and S. K. Ghosh, "Evaluation of ASCE 7-22 ELF procedures: Method 2 versus Method 1" | https://www.iccsafe.org/wp-content/uploads/bsj/Method-1-vs-Method-2-as-Submitted.pdf | abstract, sections 1-3 | S |
| R9 | ICC, Demystifying Loads for Building Officials (2024 IBC and ASCE 7-22), Part 2 | https://www.iccsafe.org/wp-content/uploads/DemystifyingLoads_24IBC_ASCE7-22_EC-85122-Part2.pdf | 2.3.6 slide, 11.4 slides, 12.8.1.1 quoted text, ELF example, drift | S |
| R10 | Bentley RAM Structural System help, ASCE 7-16 ELF topics | https://docs.bentley.com/LiveContent/web/RAM%20Structural%20System%20Help%20Complete-v5/en/GUID-C794ADD4-E7FF-4632-81C6-7CFB0183F67B.html (and its 12 child topics) | Cs, Ta table, Cu table, k, SDC tables, 12.8.1.3, SDC A | S |
| R11 | IISEE, ASCE 7 tables 3-5 | https://iisee.kenken.go.jp/net/seismic_design_code/usa/table4_usa.html (and 3, 5) | Cu, Ct (and its conflicting SI column), I | S |
| R12 | NIST GCR 16-917-41, Seismic design of steel special moment frames, 2nd ed. | https://nvlpubs.nist.gov/nistpubs/gcr/2016/NIST.GCR.16-917-41.pdf | R = 8, drift Delta_a/rho | S |
| R13 | ICC/SEAOC design example 3, RC special moment frame (sample) | https://shop.iccsafe.org/media/wysiwyg/material/9011S243-Sample.pdf | R, Omega0, Cd, Ct, Ie | S |
| R14 | PyNite (MIT), `FEModel3D.py` | https://raw.githubusercontent.com/JWock82/Pynite/main/Pynite/FEModel3D.py | `M()` 2007-2135, `analyze_modal` 2472-2560 | P |
| R15 | Frame3DD (GPL-3), H. P. Gavin | https://raw.githubusercontent.com/hpgavin/frame3dd/master/src/main.c, .../frame3dd.c, .../frame3dd_io.c; eig.c via https://raw.githubusercontent.com/pslack/frame3dd/master/src/eig.c | modal set-up, lumped_M, subspace/jacobi/sturm, participation | P |
| R16 | OpenSees (UC Regents licence) | https://raw.githubusercontent.com/OpenSees/OpenSees/master/COPYRIGHT; .../SRC/analysis/integrator/Newmark.cpp; .../SRC/analysis/analysis/ResponseSpectrumAnalysis.cpp | licence; Newmark coefficients; RSA leaves combination to the user | P |
| R17 | OpenSeesPy response spectrum example (M. Petracca) | https://jjaramillod93-openseespydoc.readthedocs.io/en/latest/_downloads/70b0bf3c3f461ea4b447a406d2884112/responseSpectrumAnalysisExample.py | CQC function and its call | P |
| R18 | structural-frame-analysis (MIT, JS) | https://raw.githubusercontent.com/mhaseebmohal/structural-frame-analysis/main/js/analysis/spectrum.js, .../modes.js, README | CQC, Ct SI table, Cu, ELF, solver choice | P |
| R19 | stabileo (AGPL-3) | https://raw.githubusercontent.com/lambdaclass/stabileo/main/README.md | features, licence | P |
| R20 | A. Der Kiureghian, A response spectrum method for random vibrations, UCB/EERC-80/15 (1980) | https://nehrpsearch.nist.gov/static/files/NSF/PB81122301.pdf | text around Eqs. 21-31 (equations garbled) | S (context) |
| R21 | CESMD web services, documentation, data policy, VDC event 88 | https://www.strongmotioncenter.org/wserv/ ; https://www.strongmotioncenter.org/NCESMD/reports/CESMD_DataPolicy.htm ; https://strongmotioncenter.org/vdc/scripts/event.plx?evt=88 | parameters, queries, policy, record PGAs | P |
| R22 | PEER ground motion database | https://ngawest2.berkeley.edu/ | home page terms | P |
| R23 | 17 U.S.C. 105 | https://www.law.cornell.edu/uscode/text/17/105 | (a) | P |
| R24 | Univ. of Iowa 58:153 lecture 16 | https://user.engineering.uiowa.edu/~sxiao/class/058-153/lecture-16.pdf | stability statements (equations are images) | S |
| R25 | A. K. Chopra, Dynamics of Structures (Table 5.4.2, Example 5.3, Table 16.3.3) | not available here | from memory, checked by computation | U |
| R26 | USGS Open-File Report 87-672 (El Centro accelerograph, 1932) | https://pubs.usgs.gov/of/1987/0672/report.pdf | search pointer only | U |

## After the independent check (2026-11-21)

`independent-check.md` re-read S1 to S10. Changes to this note:

- **Steel SMF Cd 5.5 moves from U to S:** an ATC 154 design report by AISC, designed to ASCE 7-22,
  gives R 8, Omega0 3, Cd 5.5 (femap2343.atcouncil.org).
- **Equation numbers are not settled:** FEMA P-2192 cites Ta as 7-22 Eq. 12.8-7 and Cvx as 12.8-12, this
  note 12.8-8 and 12.8-13. They stay out of the app's labels and the registry until the text is read.
- S2 (methods 1 and 2), S10 (the USGS service, re-tested: keyless, HTTP 200 errors, OPTIONS 405, the
  cached copy without CORS) confirmed as written.
