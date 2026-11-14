# Walkthrough W2 to W5: drive, fly, swim, record (outline)

Notion: Later: Walkthrough W2-W5. PIPELINE: later (after V202 W1). Research: `docs/research/research-scenario-3d-skills.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

After V202 W1 (PR #104, open) merges: these build on its controller and collision.

## 1. The owner's decisions, 2026-11-14, as recommended

- W2 drive on V166's streets at their speed, W3 fly and drone (free camera with collision), W4 swim under V143's water, W5 record a path and play it back as a video;
- the same controls on phone, tablet and desktop as W1.

## 2. What it does for the user

Drive, fly, swim through the model, and record a walk as a path to replay.

## 3. The first slice (pure functions in `src/js/engine/render/walk-path.js`, ES5, no other file's names)

- `bimWkPathAdd(path, pose, t)`: a recorded pose added when it moved far enough.
- `bimWkPathAt(path, t)`: the pose at time t, interpolated (positions linearly, headings the short way).
- `bimWkPathLength(path)`: its length and duration.

Tests: Recorded poses with headings across 0/360 degrees.

## 4. Not in this phase

Vehicles' physics; multiplayer.
