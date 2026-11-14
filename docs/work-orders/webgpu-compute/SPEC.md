# Rendering on WebGPU: compute for the simulations (outline)

Notion: Later: Rendering on WebGPU. PIPELINE: later. Research: `docs/research/research-notion-later-webgpu-compute.md`. Written by Claude, 2026-11-14, as an outline: **blocked**, no work orders for Cline.

## 0. Status

Blocked: needs GPU hardware tests and a CPU reference the GPU must match; the renderer already uses WebGPU with a WebGL fallback. Unblocked when a simulation is measured too slow on the CPU.

## 1. The owner's decisions, 2026-11-14, as recommended

- a CPU reference for each kernel first; a GPU kernel ships only when it matches it within a stated tolerance on the owner's devices;
- WebGL stays the fallback.

## 2. What it does for the user

(When unblocked) the simulations' heavy steps on the GPU.

## 3. Not in this phase

Everything until the gate clears.
