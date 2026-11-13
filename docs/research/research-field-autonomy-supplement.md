# Track E supplement: localization and field work instructions

Research date 2026-11-13; baseline main 95b7aee4db8be1fc28c0fbe7befc7407fabd1dda. Builds on the existing merged research note [1], not a replacement for it or an implementation. No field trial, licensed imagery acquisition, camera calibration, pose estimate, user test, drone flight or independent review was performed. Existing owner decisions in [1] remain open unless subsequently recorded.

## Questions and evidence

A photo without GPS may be localized only if the image, sufficient reference information and camera/geometry assumptions support it; it is not automatically possible or accurate. A research paper demonstrates UAV orthophoto matching with visual-inertial odometry, local ground planarity, a 200 m starting-area prior and a 1 m/pixel map. It used simulated inertial pose increments based on ground truth and three acquired datasets; it reported less than approximately 50 m RMS after roughly 2 km travel, with ambiguity and appearance-change limitations [2]. This is neither a single-photo phone method nor evidence for centimeter-level location. Earlier OrthoLoC research concerns drone positioning; do not infer DeepScenario's undisclosed vehicle method. Verify each upstream revision and code, data, weights, runtime and commercial-use licenses separately before use.

Work-instruction software can show planned visual steps but a rendered view is not evidence that a person completed a step correctly, that work is safe, or that a procedure is authorized. This direction remains a proposal: domain and workforce validation are outstanding.

## E1: proposed human-assisted workflow and safeguards

1. Obtain permission and a rights-cleared image plus orthophoto/surface model, with timestamps, extent, resolution, CRS, vertical datum, accuracy and acquisition age. Reject or flag missing coverage, incompatible coordinate systems, stale construction and unknown rights. Never infer absolute height from an orthophoto alone.
2. Capture calibrated lens/intrinsics/distortion and image orientation where known. User suggests search region; show orthophoto and surface at compatible vertical reference. Mark independently identifiable 2D image to 3D reference correspondences with each landmark and evidence shown. A DSM might describe roofs/vegetation instead of ground and can disagree with the photo. Automatic matchers are candidates requiring rights/licensing and measured performance, not trusted labels.
3. Estimate pose with a robust outlier method and explicit coordinate transforms; reject insufficient, clustered, nearly planar/degenerate, contradictory or poorly distributed correspondences as appropriate to the chosen solver. Multiple plausible poses may exist; keep alternatives or abstain. A small reprojection error can coexist with wrong absolute pose because the geometry or reference is wrong. Show residuals, coverage, ambiguity, assumptions and uncertainty, not invented confidence.
4. A separate surveyed holdout compares camera position and orientation against independently obtained reference, with uncertainty and datum recorded. Report acceptance rate, median/95th-percentile and worst-case errors, failures and subgroup performance (oblique/low-light/season/change/repeated features/DSM gaps) with sample sizes. Split by site and time to avoid leakage; do not calculate a percentile from a tiny sample as a robust guarantee. Set use-specific acceptance thresholds with a qualified reviewer before tests. Never use preliminary outputs for survey, navigation, machinery or safety control.

A local guided landmark tool can avoid transmitting photos, but local execution does not remove rights, privacy or device-security obligations. Strip or protect EXIF and faces, control access/retention, handle location as sensitive, and log consent and deletion. Offline use and actual model weights/attribution must be independently checked. Air operations, if any, need the operator's jurisdiction-specific rules and permissions; US 14 CFR 107.31 imposes visual-line-of-sight conditions subject to applicable exceptions or waivers [3]. No flight is authorized by this research.

## E2: instructions as controlled, view-only documents

Store instruction version and approved procedure, model revision, stable object/part IDs, camera and highlights, step sequence, expected prerequisites, warnings with their authoritative source, and author/reviewer. A model revision affecting an identified object should mark steps stale, not silently carry them forward; a missing ID must be visible. A saved view demonstrates intended sequence, not engineering approval. No commands to equipment, safety bypass, invented PPE or automatic completion. Human review and signed release must be outside an unverified display pipeline. Completion records need explicit actor, timestamp, evidence, optional offline sync conflicts, audit trail, access/retention and consent; do not treat clicking next as proof of quality or certification. Standards, xAPI or DSC3D integration and permissions are open decisions, not claims of compliance.

## Proposed evidence matrix

| Test | Fixture / observable result |
|---|---|
| Transform | Known local 3D points, CRS and vertical units, round-trip and north convention; independent check of expected coordinates. |
| Ambiguity | Repeated facades, sparse/occluded points and mirrored hypotheses; reject or expose competing poses. |
| Reference change | Old orthophoto, new construction, DSM roofs and datum mismatch; label stale/unknown and prevent false precision. |
| Camera | Unknown focal length/distortion, downsampled/blurred and oblique phone photos; measure failure, not just solved subset. |
| Holdout | Sites and acquisition dates not used for tuning; independently surveyed ground truth; report all attempts and uncertainty. |
| Instructions | Saved camera and IDs, deleted/renamed/changed object, offline conflict, reopen and permission loss; no silent update or unauthorized action. |
| Privacy | Revocation/deletion, location metadata and access controls across local and sync paths; verify no residual copies according to actual retention policy. |

These are plans, not executed acceptance tests. Licensed standards, actual source assets, provider coverage, user requirements and implementation details need further research. The 40-hour rough estimate is not a validated delivery commitment. Before work orders, owner chooses priority E1/E2, target device and workflow; data owners approve collection and use; qualified independent reviewers select thresholds and verify safety, methodology and rights.

## References

[1] https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/docs/research/research-field-autonomy.md
[2] https://arxiv.org/html/2103.14381v2
[3] https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107/subpart-B/section-107.31
Task: https://app.notion.com/p/3fecbfcc3a3881898c8cee95145f1705
