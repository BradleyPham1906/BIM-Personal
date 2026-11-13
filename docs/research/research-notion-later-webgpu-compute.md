# Later: WebGPU compute for simulations — research draft

**Status:** research in progress, not implementation approval. Independent source review, real GPU runs, and domain-expert review have not been performed. This note updates rather than replaces the earlier `research-bim-hub.md`; the task is uncommitted and its rough 24-hour allocation is not a validated estimate.

## Abstract
The question is how to introduce simulation compute without confusing it with the WebGPU renderer already present. Recommend a small opt-in, non-authoritative proof of concept with a CPU reference, explicit device capability checks, revision-aware cancellation, and end-to-end correctness and performance comparisons before selecting any production solver. No evidence establishes that GPU will be faster for the app's workloads or sufficiently accurate for engineering decisions. A simple CPU stencil experiment below illustrates a reference comparison, not a GPU implementation or physical flood model.

## Questions and falsifiable hypotheses
- H1: A renderer already exists, so no new rendering-backend replacement is required. **Supported by selected source inspection** at pinned main commit below; the inspected files are not a full application audit.
- H2: Every WebGPU-capable browser/device can run the same unbounded kernel. **Rejected:** limits, optional capabilities, device loss and asynchronous failures matter [1].
- H3: WebGPU compute makes this app's simulation faster. **Unresolved:** no application-kernel benchmark was run; upload, compilation and readback can dominate. Figma reports device-dependent outcomes for rendering, not a benchmark of our compute [3].
- H4: A CPU single-precision stencil agrees with a double-precision reference for the tested fixture. **Supported only for this one artificial fixture**; WGSL does not promise identical CPU rounding [2].

## Method and search log
Read the W3C WebGPU and WGSL specification excerpts; Figma's engineering account; the project's `webgpu.js`, `gpu-batches.js`, and relevant selected portions of `traffic-sim.js` at commit `95b7aee4db8be1fc28c0fbe7befc7407fabd1dda`; and the older BIM Hub note. Web searches included `WebGPU compute device lost workgroup limits`, `WGSL floating point accuracy workgroup synchronization`, `Figma WebGPU renderer fallback performance`, and counterexamples on WebGPU transfer overhead. W3C standards and product source are primary; Figma's own account is primary for its product only. A local NumPy CPU fixture was run once; see experiment source and raw JSON under `docs/research/experiments/`. No app was launched and no upstream code executed. No independent reader has checked this note; source extracts, not every section of the standards, were reviewed. Browser/network constraints prevent representative cross-device measurements here.

## Findings and evidence
1. **Existing renderer (P, high for inspected code):** `src/js/engine/render/webgpu.js` contains `bimGpuStart`, WebGPU render pipelines and `dev.lost` handling; `bimRender3D` falls back to WebGL. `bimGpuNeedsGl` returns an empty string with a comment that map and terrain are drawn with WebGPU. An older top-of-file comment claiming map/terrain fall back is stale; don't mistake it for current code behavior [4]. `gpu-batches.js` maintains shared scene data and separate GPU/GL copies [5]. This is rendering evidence, not proof of a reusable simulation service.
2. **Compute lifetime (P, high):** `requestAdapter()` may return null, requested device limits govern validation, and a lost device invalidates use of its objects [1]. Reject unavailable or inadequate adapters; allocate within actual device limits; isolate failure and recover to CPU. Readback needs an asynchronous map and proper copy/usage flags; do not treat it as instantaneous.
3. **Ordering (P, high):** WGSL barriers have workgroup execution scope, not a global inter-workgroup barrier, and require uniform control flow [2]. A stencil reading neighbouring outputs must not update the same storage in place across workgroups: use separate input/output buffers and ordered dispatches. Round up the dispatch count and guard out-of-range invocations; barriers must remain uniform.
4. **Numerics (P, high for specification, low for a solver):** WGSL f32 is not bit-for-bit CPU f32: rounding modes and accuracy differ and some non-finite runtime results can be indeterminate [2]. Establish domain-specific absolute and relative tolerances, conservation, stability, and independent reference fixtures before trusting outputs; do not apply generic graphics tolerances to FEA or flood assessments.
5. **Existing candidate, not selected (P, medium):** `traffic-sim.js` comments describe fixed-step runs with fixed typed-array pools, and the code uses `Float32Array` fields and a `bimTrStep` function [6]. Traffic routing, signal dependencies and deterministic behaviour make this a substantial port; inspect the entire state machine before treating it as embarrassingly parallel. Do not use the render benchmark as compute evidence.
6. **Performance counterexample (P, medium):** Figma reports WebGPU wins on some devices and neutral results on others, describes allocation/upload hazards and implements dynamic fallback [3]. Its rendering results cannot be generalized to our kernels.

## Alternatives compared
Criteria: correctness and continuity first, availability, integration complexity, then measured end-to-end latency. No production workload measurements exist.

| Alternative | Strength | Limitation | Decision |
| --- | --- | --- | --- |
| CPU JavaScript reference | Available without WebGPU; straightforward oracle | Can block UI for heavy work | Required correctness baseline; use worker if responsiveness requires |
| CPU WebAssembly/worker | Potential isolation and speed | Build, messaging and accuracy need measurement | Benchmark when real workload selected; no assumed gain |
| WebGPU compute | Parallel, can keep intermediate buffers resident | Async lifetime, transfer and device variance, f32 limitations | Opt-in experiment only; deploy only after correctness and speed gates |

## Reproducible experiment
`experiments/webgpu-stencil-cpu.py` uses Python 3.13.15 and NumPy 2.5.4: a 16×16 interior with zero boundary, unit center impulse, 100 five-point explicit diffusion updates, alpha 0.24. CPU f64 vs CPU f32: max absolute difference **6.114579714951163e-10**, RMS **1.6262180131533655e-10** across the whole 18×18 grid including zero boundary; sums **0.30728186670470226** and **0.30728190113586606**. One run, not a timing benchmark. Boundary absorption explains why the sum need not remain 1. This synthetic comparison is not WebGPU, not traffic, not flooding or structural validation; cross-device WGSL arithmetic may differ. Raw JSON is committed next to the script.

## Proposed integration and gates
- Select one small kernel only after defining user-visible quantity, units, acceptable errors and CPU oracle. Start with data-parallel, non-authoritative output; do not change any engineering calculation by inference from the demonstration.
- Snapshot model revision and input arrays; return `{revision, backend, units, assumptions, diagnostics, result}`. Publish only when revision still matches; cancel logically on edits and release resources when safe. Keep this a proposed interface, not an existing API.
- Reuse lifecycle ideas from the renderer only after checking device ownership and teardown: if the shared device is lost, reject/ignore old jobs, release job buffers, retain CPU inputs and run CPU or report failure; never silently accept partial/stale data. A separate device has isolation benefits but needs memory/ownership measurement.
- Test zero/nonmultiple workgroup sizes, adapter null, low limits, loss during dispatch/map, allocation and validation failure, cancellation, revision changes, repeated jobs and memory cleanup; compare CPU/GPU numeric error and invariants over synthetic and real anonymized fixtures.
- Benchmark cold pipeline/device creation and warm cases across small/medium/large representative inputs, including packing/upload, all dispatches, synchronization, copy/map and presentation. Record browser/version, OS, hardware, device limits, repeated runs, median and tail; compare equivalent CPU results. Establish thresholds with the owner, not retroactively.
- Engineering outputs stay labelled experimental until the named domain specialist checks reference cases and signs off. Research is not done until remaining unverified facts and independent checks meet `research-protocol.md`.

## Edges, risks and open questions
Precision near ill-conditioned cases, no adapter, device limits, large buffers, background tabs, browser/device differences, timeout, thermal throttling, resource exhaustion, workgroup edges, stale revisions and cancellation are open. A huge model must be chunked or rejected within device limits; tile-boundary halos and ordering must be tested. No CORS/data service is needed for this local synthetic fixture. Actual numerical algorithms, units, tolerances, CPU worker architecture and break-even sizes are **U** until selected and tested. No independent review, other-browser, mobile or hardware GPU run is represented. This draft has not checked all prior V152–V156 tests or all simulation code.

## Owner decisions
1. Which simulation should be first, and is its result visualization-only or engineering decision support?
2. Who approves domain-specific numeric tolerance and independent benchmark fixtures?
3. What browsers, devices, memory budget, performance thresholds and fallback UX define release?
4. Should compute share the renderer device or own a device after lifecycle tradeoffs are tested? Does the 24-hour rough allocation need revision?

## References
1. [W3C WebGPU](https://www.w3.org/TR/webgpu/), initialization, limits, device loss, buffers and compute dispatch; primary, excerpts read 2026-11-13.
2. [W3C WGSL](https://www.w3.org/TR/WGSL/), execution, barriers and floating point evaluation; primary, excerpts read 2026-11-13.
3. [Figma engineering: rendering powered by WebGPU](https://www.figma.com/blog/figma-rendering-powered-by-webgpu/), 2025-09-18, renderer integration and fallback; primary practitioner account, read 2026-11-13.
4. [`webgpu.js` at audited commit](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/render/webgpu.js), selected renderer functions; primary.
5. [`gpu-batches.js` at audited commit](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/render/gpu-batches.js), shared scene and dirty data; primary.
6. [`traffic-sim.js` at audited commit](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/simulation/traffic-sim.js), selected initialization and step declarations; primary.
7. [`research-bim-hub.md`](https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/docs/research/research-bim-hub.md), earlier brief; superseded where it treats renderer as future work.
