# V277a search log

Every retrieval and search for `research-tensors-rotations.md`, 2026-11-24, in order. Downloads were kept outside
the repository as data and read as text (pdftotext for PDFs); nothing downloaded was run.

## Direct retrieval of known primary sources

| # | Where | What was fetched | Result | Kept / set aside |
|---|---|---|---|---|
| 1 | arxiv.org | Sola, *Quaternion kinematics for the error-state Kalman filter*, arXiv 1711.02508 (PDF) | 200, 4,818 lines of text | Kept: conventions (Table 2), kinematics (eqs. 99, 200, 201), exp map (eqs. 97 to 105) |
| 2 | arxiv.org | Kopp, *Efficient numerical diagonalization of hermitian 3x3 matrices*, arXiv physics/0610206 v3 (PDF) | 200 | Kept: abstract and sections 2 to 4 (Jacobi, QL, Cardano, accuracy) |
| 3 | cs.cmu.edu | Shoemake, *Animating rotation with quaternion curves*, SIGGRAPH 1985 (PDF, course copy) | 200, scanned text with OCR noise | Kept: the Slerp definition and the double cover; formulas checked against the scan, not the OCR |
| 4 | raw.githubusercontent.com | three.js `src/math/Quaternion.js`, `Matrix4.js`, `Euler.js`, `LICENSE` (dev branch) | 200 | Kept: storage order, matrix to quaternion, slerp threshold, Euler order; MIT |
| 5 | raw.githubusercontent.com | gl-matrix `src/quat.js`, `LICENSE.md` | 200 | Kept: fromMat3 (Shoemake 1987), slerp without renormalisation; MIT |
| 6 | gitlab.com | Eigen `Eigen/src/Geometry/Quaternion.h` | 200 | Kept: (w, x, y, z) constructor, [x, y, z, w] storage; MPL-2.0 (Eigen's licence, not used) |
| 7 | raw.githubusercontent.com | Jolt Physics `Jolt/Math/Quat.h`, `Quat.inl`, `LICENSE` | 200 | Kept: [x, y, z, w] storage; MIT |
| 8 | raw.githubusercontent.com | Khronos glTF 2.0 `specification/2.0/Specification.adoc` | 200 | Kept: section 3.4 (axes, units), node rotation in XYZW |
| 9 | standards.buildingsmart.org | IFC 4.3 IfcAxis2Placement3D (HTML) | 403, refused (as recorded in the protocol) | Set aside; replaced by 10 |
| 10 | raw.githubusercontent.com | buildingSMART `IFC4.3.x-development` `docs/schemas/.../IfcAxis2Placement3D.md` | 200 | Kept: the definition and formal propositions |
| 11 | astro.rug.nl | Diebel 2006, *Representing attitude* (a mirror) | No file | Set aside; Sola covers the same ground |
| 12 | fs.usda.gov, fpl.fs.usda.gov | Wood Handbook chapter 5 by two guessed URLs | HTML page, then 502 | Set aside; replaced by 13 |
| 13 | research.fs.usda.gov | Treesearch 62200 (the Handbook's index), then `download/treesearch/62244.pdf` | 200; chapter 5 identified by its first page | Kept: Tables 5-1, 5-2, Eq. 5-1 and the text around them |
| 14 | bipm.org | SI Brochure, 9th edition (2019), English PDF | 200 | Kept: Table 2 (base units), Table 4 (22 derived units with special names) |
| 15 | geometrictools.com | Eberly, *A Robust Eigensolver for 3x3 Symmetric Matrices* (2014, modified 2021) | 200 | Kept: an alternative for part 5; CC BY 4.0 |
| 16 | arxiv.org | Habera and Zilian, arXiv 2111.02117 (abstract page) | 200 | Kept: closed-form invariants lose accuracy in finite precision near repeated eigenvalues |
| 17 | mechkit.readthedocs.io | mechkit notation documentation | 200 | Kept: the Mandel basis is orthonormal and converts stress, strain, stiffness and compliance alike |

## Searches for counter-evidence (the protocol's step 4)

| # | Engine | Query | What came back | Kept / set aside |
|---|---|---|---|---|
| S1 | web | gl-matrix quat slerp not normalized linear interpolation issue | No gl-matrix issue found; an Irrlicht forum report of up to 10 degrees from un-normalised slerp; gl-matrix's own note that fromMat3's result is not normalised | Kept as support for renormalising (e03 measured it); the forum report is U, not used for numbers |
| S2 | web | closed-form eigenvectors symmetric 3x3 repeated eigenvalue failure cross product method | Habera and Zilian (2021, 2025) on instability of the closed form at repeated eigenvalues; NVIDIA Warp's note that eigenvectors are not unique there; O3DE's use of Eberly's robust method | Kept: Habera and Zilian (read, item 16), Eberly (read, item 15). No source contradicted e05 |
| S3 | web | Mandel notation vs Voigt notation rotation orthogonal 6x6 fourth order tensor | Wikipedia (pointer only), mechkit's documentation, two arXiv papers stating Voigt's 6x6 operations need type-dependent factors | Kept: mechkit (item 17); e06 measured the claim directly |
| S4 | web | orthotropic wood elastic constants positive definite compliance reciprocity Poisson ratio violated measured | A Michigan State thesis reporting that measured SLR, SRL and SLT, STL do not follow orthotropic reciprocity; a 2018 study checking positive definiteness of wood compliances; a Korean pine study deriving minor ratios from reciprocity | Kept as support for D7, at level S (summaries read, papers not opened); e07 measured the Handbook's own values |

## What was not searched, and why

Bond (1943) and Helnwein (2001) on rotation matrices for 6x6 notations, and Shepperd (1978), are behind publishers'
paywalls; their results are reproduced and measured here (e02, e06) and stated in the open sources above, so the
note cites them at level S through those sources.
