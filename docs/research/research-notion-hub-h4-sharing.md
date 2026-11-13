# Hub H4: explicit project sharing and sync — research

Research date: 2026-11-13. Status: substantive research, not independently reviewed, not a build authorization. Target: Hub H4, push and pull a project's history to a repository, one file per element; GitHub first; synchronize only on user request. This report was initially staged in Notion; this copy is an unmerged research submission. H1 and H2 are recorded as completed in Notion, but the current history serialization and merge implementation have not been audited in this research. Estimates are not validated.

## 1. Abstract and recommendation

Use GitHub as a versioned transport, not as the semantic BIM merge engine or an authorization system for individual elements. Write one immutable, canonical representation per stable element ID plus project metadata and a versioned manifest; preserve the existing history and its two-parent merges rather than silently replacing them. Prepare a complete project snapshot, validate cross-element references, stage an atomic Git tree and commit, and update a branch with non-forced fast-forward semantics. Pull into a separate staging area, validate before applying to a working copy, and use the existing element/field merge and explicit conflict resolution. The owner chooses the sync action; neither a background poll nor a save may push model data. Avoid force, automatic merging of risky references, implicit loss of unsaved work, and exporting a repository as if it were element-private.

A local Git 2.49.0 experiment gave a critical counterexample: two people edited different files and Git merged them without a conflict, yet the resulting door referenced a deleted wall. A clean Git merge is not a valid BIM merge. The same experiment showed stale push rejected and divergent edits to a single file conflicting. These are local Git fixtures, not tests of GitHub or the application. Independent review, full current-code audit, real GitHub integration, browser/offline checks, realistic datasets, and security review remain outstanding.

## 2. Hypotheses and falsification

| Hypothesis | Result | Evidence and limit |
| --- | --- | --- |
| H1: one element per file prevents conflicting edits | Failed in part | Same-file divergence conflicted; disjoint files merged but broke a host reference in the fixture. |
| H2: an ordinary Git non-fast-forward update protects against stale overwritten history | Held for local git push | Bare local repository rejected second push. GitHub documents force=false as fast-forward only; API was not tested. This is not a documented compare-and-swap on an expected old SHA. |
| H3: text merge can be the final authority for BIM | Rejected | Text has no BIM-specific referential, unit, schema or geometry rules. The synthetic orphan demonstrates the gap, not all possible conflicts. |
| H4: per-file REST writes form an atomic model revision | Not established; avoid | Contents endpoint writes one path and has conflicts on concurrent update/delete; whole project requires one tree/commit/ref publication. |
| H5: GitHub repository visibility provides component-level privacy | Rejected | Repository readers can obtain reachable files/history under their repository access. H5 object-level access is a separate system. |
| H6: H1/H2 histories map losslessly to a Git DAG | Unknown | Their task pages describe element history, field merge and two-parent merge; their serialization, IDs, and exact merge graph need inspection and fixtures. |

## 3. Method and evidence boundaries

Read the current Notion H4 task and H1/H2 tasks; read the repository's existing BIM Hub research and GitHub documentation on Git trees, commits, refs and contents; read Git's merge documentation. Tested a bare local Git repository and two working clones with synthetic wall/door JSON. No production model, account, tokens, remote API, implementation code, actual history importer or browser was tested. Source claims marked documented are from GitHub/Git; local findings are from the attached script and JSON. General design choices below are recommendations, not decisions already made by the owner.

The existing Hub research proposed H3 with web-ifc, but current V196 selected cc-ifc and shipped full-reader code. Do not reintroduce obsolete technology assumptions. Its H2 phase numbering also differs from the current H2 task (V151): treat the task and current pipeline as authoritative for status, then inspect implementation.

## 4. Git object model and upload transaction

A blob holds a file's bytes, a tree names blobs/subtrees, a commit points to one tree and lists parents, and a ref names a commit. GitHub supports creating a tree from a base tree and entries, creating a commit with explicit parents, and updating a ref. A single commit's tree is a coherent snapshot: readers of that commit do not see intermediate element file versions. This does not make remote updates, app storage and network retries a distributed transaction.

Recommended push state machine:
1. User requests push; present account, repository, branch, project, pending revision count, and destination visibility before first binding and before changing target. No upload on normal Save.
2. Freeze an immutable local snapshot, including all relevant H1 history and H2 graph information. Retain a recoverable local checkpoint. Define exactly what project assets and histories are included before declaring support.
3. Fetch remote ref and commit/tree. Verify expected project identity, schema version and format; reject unrelated or newer incompatible project. Fetch tree subtrees if recursive response is truncated: GitHub documents a 100,000-entry/7 MB recursive response limit. Treat filenames, file mode, executable content and unexpected paths as untrusted.
4. If the remote changed since the recorded base, stage a three-way semantic merge and explicitly resolve conflicts. Validate the result; do not silently choose a winner. Include relationship-level conflicts even when different files changed. Reject duplicate IDs and dangling references unless explicitly allowed by the supported data contract.
5. Create blobs/tree/commit referencing the current remote parent(s), then update the branch ref with force=false. GitHub documentation promises fast-forward behavior, not an expected-old-SHA parameter for this endpoint. An ordinary divergent remote advance should fail; refetch, re-merge and retry, bounded. It is not equivalent to strict compare-and-swap in every history shape: formally define whether a descendant update that incorporates an intervening commit is acceptable; otherwise use a supported stronger server-side mechanism or protected pull-request flow.
6. After a timeout, do not assume failure and blindly repeat. Re-read the ref and verify whether the intended commit became reachable. Show success only after confirmation. If publication failed, keep local snapshot and semantic merge inputs intact; unreferenced server objects may remain but are not a published revision.
7. Branch protection, permission denial, expiry, rate limiting, repository creation rules and empty-repository bootstrapping may prevent a direct update. Surface the actual reason; do not force or weaken protection. Branch/PR policy is an owner decision. Treat server responses, not stale local UI, as authoritative.

## 5. Pull, migration and reconciliation

Fetch a fixed commit SHA, not a branch repeatedly during one import. Confirm manifest format, project ID, hash/path consistency and schema version, decode into a new staging model, and enforce explicit size, recursion and decompression limits. Do not execute repository content. Validate all IDs and references, level/layer membership, units, ordered arrays, project-wide shared registries, topology and parent-child history before mutating the working project. Reject invalid, incomplete or unknown-required data with a recoverable error; missing referenced assets must not be replaced with silent defaults. Preserve raw source and provenance for user-directed recovery where feasible.

If the local project is dirty or has local commits since the shared base, pull must not replace it. Save a local checkpoint, offer compare and staged semantic merge, and publish only on explicit apply. Distinguish fast-forward, unrelated history, diverged history, delete/modify, delete/delete, divergent edits, identical edits, new ID collision, reorder versus modification and concurrent renames. H2 already advertises field-level merge and Keep/Take: reuse it only after verifying its behavior with these cases. If no valid common ancestor exists, block automatic three-way merge and present recovery options rather than fabricate an ancestor.

Project metadata, shared layer tables, materials, georeferencing, external asset references, history metadata and unit settings can conflict even if each element file is independent. A transform or unit change can invalidate many unchanged elements; validation must consider cross-file invariants. Arrays representing coordinate sequences or ordered topology require domain-specific rules, not alphabetical sorting. Never normalize geometry by rounding without a separate precision study.

## 6. Proposed file contract, not an approved schema

A namespaced root such as `bim-project/`, a versioned manifest, project settings, element files keyed by encoded stable IDs, and a content-addressed asset directory can be considered. Manifest should identify format/version, project ID, app schema version, coordinate/unit convention, serialization convention, inventory, required asset references and history mapping. Security metadata must not be presented as enforcing authorization. Stable application ID is distinct from IFC GlobalId and from Git blob SHA; define import/reimport identity and duplicate IFC IDs explicitly. Restrict filenames to a canonical encoding (prevent slash, `..`, normalization collision and reserved-name collisions), reject duplicate IDs and avoid user-provided path concatenation.

Canonical JSON should recursively order object keys, define UTF-8/newlines and numeric representation, preserve meaningful array order and distinguish absent from null. Explicitly define NaN/infinities, negative zero, precision, timestamps, binary assets and circular references. A deterministic serialization test must compare two independent serializations byte-for-byte. A file per element aids diffs but increases tree entries, API work and repository size; project-level indexes and large imported meshes may dominate. Benchmark on realistic sizes before committing to a scale target. Git history can retain deleted data indefinitely; deleting a file or making a repo private later is not reliable secret removal.

Alternatives: (A) one project JSON is simple but causes large coarse conflicts; (B) individual element files plus metadata allow localized diffs but still need semantic merge and large-tree controls, recommended for further specification; (C) Git LFS or object storage for large blobs adds infrastructure, pointers, access controls and lifecycle issues—assess only from measured assets. Contents API is convenient for one file but is not a multi-file transaction; tree/commit/ref supports snapshot publication, subject to branch and API behavior.

## 7. Local falsification experiment

Run `python3 h4-git-experiment.py` on a computer with Git and Python. It creates a disposable bare repository and clones in a temporary folder; no network is used. Initial state: wall and a hosted door. Clone A deletes wall and pushes; clone B modifies door and attempts its stale push. Push rejected; after fetch, B merges successfully because changed paths differ. The door's host points to a nonexistent wall. A second divergent door edit creates a same-file Git conflict. Captured results: git version 2.49.0; stale push rejected=true; disjoint merge exit=0; orphaned host=true; same-file merge rejected=true. This single synthetic case establishes a failure mode, not its frequency or whether H2 already catches it. The script and machine-readable output accompany this record.

## 8. Failure and adversarial test matrix for a future work order

1. Initial push to an empty repository and existing branch; no data disclosure or write on cancel.
2. Disjoint element modifications merge cleanly and preserve both; same field differently edited prompts; same value on both sides resolves only if H2 semantics allow.
3. Deleted host plus edited door: no silent successful publication; explain orphan and allow valid resolution.
4. Concurrent same ID creation with different content, duplicate GUIDs and path-encoding collisions: reject and preserve both working copies.
5. Unit/georeference changes versus object edit: detect project-wide semantic conflict; verify coordinate transforms, not just text.
6. Network failure before ref update, timeout after ref update, retry, token expiry and rate-limit: verify idempotence/recovery, no phantom success, no automatic force.
7. Branch protection, read-only credentials, repository deleted/renamed, revoked account and detached/unrelated branch: preserve local state and give actionable error.
8. Large tree/truncated response, malformed JSON, path traversal, invalid UTF-8, huge or absent asset, newer schema: bounded processing, no code execution and no partial application.
9. Dirty local edits during pull, interrupted merge, app crash and restore: checkpoint remains readable; no overwrite; validate before apply.
10. Two-parent H2 merge round-trip and history graph identity; branch checkout; restore old element; deletion/re-add; two contributors; no invented history mapping.
11. Secret controls: repository privacy warnings, credentials never in project files, history, logs or URLs; tests use ephemeral credentials and isolated test accounts.
12. Baseline and target performance: measure wall time, peak browser memory, network requests, bytes, tree entries and offline behavior on agreed fixture sizes. No performance acceptance limit is inferred from the task's 24-hour estimate.

## 9. Security and privacy

Authenticate using an appropriate scoped, revocable mechanism compatible with a static browser deployment, with explicit account and repo binding; document token lifetime, refresh, storage and XSS exposure. Do not put tokens in Git, model files, query strings, client logs or screenshots. For public repositories, assume everyone can read all published elements and history. For private repositories, collaborators with repo access can inspect data unless a separate, actually enforced encryption or service design exists. Per-element ACLs, payments and protected analyses belong to H5, not Git tree layout. A signed commit or append-only-looking history is not an automatically immutable audit trail: permissions and force-push settings govern rewrite; choose an audit model and verify it separately.

## 10. App-specific gaps, risks and owner decisions

Code audit must map existing H1 IDs, version graph, metadata, H2 merge rules, project save/load, assets and schema migrations to the transport. Verify the current main commit before work starts and inspect related tests. Risks include destructive conflation of app versions with Git commits, orphaned relations, missed assets, history leakage, large trees, stale race and false success after timeout. The H1/H2 task descriptions record completion but are not a current source-level verification.

Decisions not yet approved: repo ownership and branch/PR protection; first-push visibility confirmation; exact inclusion of history and assets; write access model and credential strategy; the semantic-conflict resolution policy; supported size thresholds; and whether any history rewrites are ever allowed. Recommendations above are provisional. None of these items authorizes implementation, estimates, a security guarantee or a new phase number.

## 11. References

- [Original Hub research](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-bim-hub.md), existing project intent; some implementation details now stale.
- [H1 element history](https://app.notion.com/p/3fecbfcc3a3881ba97cff98677d2ccee) and [H2 branches and merge](https://app.notion.com/p/3fecbfcc3a3881758b7aca180b21b86a), task-reported scope, accessed 2026-11-13.
- [GitHub Git trees](https://docs.github.com/en/rest/git/trees), base trees, entry replacement and truncation; [Git commits](https://docs.github.com/en/rest/git/commits), tree and parents; [Git references](https://docs.github.com/en/rest/git/refs), force=false and statuses; [Contents](https://docs.github.com/en/rest/repos/contents), per-file updates and size limits, accessed 2026-11-13.
- [Git merge manual](https://git-scm.com/docs/git-merge), three-way stages and recovery, accessed 2026-11-13.
- Attached `h4-git-experiment.py` and `h4-git-experiment-results.json`: author-run synthetic local test, 2026-11-13; no independent reproduction or real provider test.


---
Research evidence files: [`experiments/notion-h4-sharing/`](experiments/notion-h4-sharing/). Original scripts and results reflect only the experiments described above.
