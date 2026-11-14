# Hub H4: share and sync through GitHub (outline)

Notion: Later: Hub H4: share and sync. PIPELINE: later. Research: `docs/research/research-notion-hub-h4-sharing.md`, `docs/research/research-bim-hub.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Spec sprint after the history code is audited against the research's gaps (part 10).

## 1. The owner's decisions, 2026-11-14, as recommended

- GitHub as transport only: one canonical file per element by its stable id, plus the project's metadata and a versioned manifest;
- every push is a non-force update; a rejected push is pulled, compared three ways and shown, never overwritten;
- after any Git merge the app checks the model itself (references, hosts, levels); a clean text merge that breaks a reference is a conflict;
- opt-in per project; the token kept by the browser only, asked for each session.

## 2. What it does for the user

Share a project to a GitHub repository and pull others' changes; conflicts and broken references are shown for the owner to resolve.

## 3. The first slice (pure functions in `src/js/engine/history/hub-files.js`, ES5, no other file's names)

- `bimHubCanonical(el)`: an element as canonical JSON: keys sorted, numbers to 9 significant digits, no undefined.
- `bimHubPath(el)`: its file path from its kind and id.
- `bimHubManifest(els, meta)`: the manifest: schema version, element ids and their hashes.
- `bimHubRefs(els)`: every reference an element holds (host wall, level, source) and the ids it points to.
- `bimHubOrphans(els)`: references to ids that are not in the model, after a merge.

Tests: The research's experiment as a fixture: a door whose wall was deleted in the other branch is an orphan.

## 4. Not in this phase

Per-element permissions (h5); other hosts than github; binary assets beyond a size limit.
