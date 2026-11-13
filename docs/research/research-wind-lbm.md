# Wind around buildings: WebGPU lattice Boltzmann research draft

Research date 2026-11-13. Scope: the remaining wind part of the Structural and Wind Analysis task; its notes say V125 already built the frame solver. Existing app source inspected at main 95b7aee4db8be1fc28c0fbe7befc7407fabd1dda. This is a research draft, not an implementation, validated solver, design calculation or independent review. No application, GPU solver, hardware, dataset or wind tunnel run has been tested.

## Questions and findings

1. Is a 3-D lattice Boltzmann approach plausible? Yes as a research direction, not as proof of our implementation: ABLE-LBM uses D3Q19, MRT and LES for a building array, compares to matched-Reynolds-number water-channel MR velocimetry, and describes boundaries and conditions [1]. Those results do not transfer automatically to our code, buildings, atmospheric conditions or WebGPU.
2. Can existing WebGPU render support be treated as an existing CFD solver? No such solver was established in the pinned renderer inspection [2]; rendering initialization and fallback are not validation of numerical compute.
3. Can a single illustrative wind simulation establish design wind, safety, compliance, or comfort? No. Inputs, conditions, model uncertainty, statistics and intended use all matter. The AIJ benchmark catalog has many geometries and measurements, and reports uncertainty details for only selected cases; study each dataset's original protocol and license [3]. A wind rose alone is not a complete inlet velocity/turbulence profile.
4. Does a supported adapter guarantee an allocation? No. Check the requested device limits, actual resources and errors. WebGPU specifies default 128 MiB maximum storage-binding size and 256 MiB maximum buffer size, while higher supported limits can be requested [4]. Those limits are not a promise of successful allocation or performance.

## Intended use and essential inputs

Owner and qualified wind engineer must choose purpose and acceptable uncertainty. Research-only exploratory visualization should be explicitly watermarked as unvalidated; no structural design loads, safety decisions, pedestrian compliance, pollutant dispersion or autonomous navigation from an unvalidated result. Never present an instantaneous flow image as a climate statistic or regulatory determination.

Freeze a run manifest: project/model and geometry revisions, hash, CRS/vertical datum, units, north and wind-from versus flow-to convention, site/context/terrain geometry and omissions; domain and grid spacing/timestep; measured or assumed inlet profile, reference height/speed, turbulence, roughness, atmosphere and averaging period; outlet/top/side/ground/building wall conditions; collision/turbulence model and parameterization, lattice-to-physical scaling and stability checks; spin-up and sampling; solver/shader/device versions, actual enabled limits, failures and uncertainty. A change in geometry or inputs makes the result stale, not silently updated. Missing met data, invalid geometry, nonfinite values or unverified conditions must produce an explicit unavailable/failed state rather than a fake zero.

## Candidate architecture and resources

Prefer a separately versioned compute module coupled to existing model geometry and renderer, with explicit immutable geometry snapshot, units, result schema and cancellation; don't invent a second project model. Determine closed solid / terrain voxelization, porous or thin elements, faces, context extents and boundary behavior through tests. A structured 3-D grid may not resolve building edges or nearby pedestrians at useful resolution. Collision scheme (MRT versus alternatives), LES/subgrid assumptions, valid lattice Mach/Re mapping and data layout remain design questions for specialist review, not approved specifications.

For a naive two-buffer, 19 populations per cell, 32-bit layout, distribution storage is Nx×Ny×Nz×19×4×2 bytes, excluding all geometry, masks, output, staging and overhead. Local arithmetic fixture [5] reports: 64³ = 38 MiB total; 128³ = 304 MiB total (152 MiB per buffer); 256³ = 2432 MiB total. A 152 MiB single storage binding exceeds the WebGPU default binding limit even though each buffer is below the default maximum buffer size. Partitioned bindings, alternative layouts, supported higher requested limits or a smaller domain may help, but change memory, dispatch, synchronization and halo behavior; none has been implemented or benchmarked. GPU availability, device loss, adapter-specific limits, allocation failure and cancellation must be visible. Workgroup barriers are not global synchronization; use separate dispatch boundaries or another verified correct design. f32 arithmetic is not necessarily bitwise CPU-identical [6].

## Verification and validation plan, not results

- Code verification: compare an independently derived analytic laminar channel solution and conservation/steady-state cases; exercise corners, no-slip wall, inlet/outlet, clipping, geometry holes, NaN and zero velocity. Test units and wind direction explicitly; choose and justify numeric tolerances before execution.
- Numerical verification: vary grid spacing, domain extents, sampling time and inlet; document convergence, discretization and temporal uncertainty. A three-grid study can inform a grid-convergence estimate when assumptions hold; do not claim an error bound from arbitrary differences or a non-asymptotic solution [7]. Check cross-device GPU-versus-reference differences.
- Physical validation: select a suitable published wind-tunnel case with usable geometry, inflow, measurement units and licensing; reproduce conditions and compare measurement points, velocities and uncertainty. AIJ Case A and the building-array study are candidates, not passed tests. Compare multiple directions and geometry classes only after adequate independent evidence; record disagreement, not just visually appealing streamlines. Field data need authorized measured ground truth and specialist review.
- App tests: existing project save/reopen, geometry revisions, layer visibility assumptions, device loss, resource limits, cancellation, browser targets, backend differences and memory behavior; report exact commands/environment. No tests above were performed here.

## Alternatives, risks and decision gates

External validated CFD service may reduce development but introduces data ownership, service terms, cost, vendor verification and connectivity; browser LBM favors local integration but requires significant numerical validation and GPU resources. A simple directional airflow graphic is not CFD and must not be labeled as predictive. Specify target use, supported devices, minimum geometry resolution, benchmark, owner risk tolerance and expert reviewer before implementation. The task's 64-hour figure is a rough backlog estimate, not evidence of solver delivery cost. The repository requires independent review; it remains open. Upstream code/data/weights are not approved or executed, and per-source reuse licenses must be checked before use.

## References

[1] https://link.springer.com/article/10.1007/s10652-020-09770-6
[2] https://github.com/BradleyPham1906/BIM-Personal/blob/95b7aee4db8be1fc28c0fbe7befc7407fabd1dda/src/js/engine/render/webgpu.js and prior WebGPU research in this PR.
[3] https://onlinelibrary.wiley.com/doi/full/10.1002/2475-8876.70083
[4] https://www.w3.org/TR/webgpu/
[5] fixtures/wind-memory-fixture.py (self-authored arithmetic only).
[6] https://www.w3.org/TR/WGSL/
[7] https://nvlpubs.nist.gov/nistpubs/ir/2020/NIST.IR.8298.pdf
Task: https://app.notion.com/p/3fecbfcc3a388188b060ced595518127
