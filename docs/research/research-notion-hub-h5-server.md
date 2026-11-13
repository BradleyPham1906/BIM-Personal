# Hub H5 — accounts, element permissions, private checks, and paid access

Research date: 2026-11-13. Phase: Later: Hub H5, not an assigned V number. State: substantive source research and one illustrative experiment; not independently checked, not implementation-ready, no backend, security audit, or approved security guarantee. User's request is research toward specs and work orders, not authority to expose private models or purchase a service.

## 1. Abstract

A multi-tenant server can enforce per-model, element, property and derived-result permissions only if every operation passes through server-side authorization at the relevant object and action. If it computes on ordinary unencrypted model geometry, the operator and its processing environment must be trusted with that data; returning only clash results does not make computation zero knowledge. Even yes/no outputs can leak geometry through repeated, adversarial probes. Recommend a staged, explicit trust model: first establish identity, tenancy, authorization, data lifecycle and a minimal restricted check service; treat privacy-preserving computation and paid subscriptions as separate capabilities whose exact guarantees are justified and tested. The security controls, leakage budget, analysis purpose and integration boundaries require owner and independent reviewer decisions. This is beyond the static app; the 64-hour task estimate is not validated.

## 2. Questions and falsifiable hypotheses

| # | Hypothesis | Finding | Evidence and qualification |
| --- | --- | --- | --- |
| H1 | Hidden or unguessable element IDs provide authorization | False | OWASP API1 requires verifying the subject's action on the specific object; UUIDs alone are not access control. P, high confidence. |
| H2 | A user with access to an object can safely receive all fields | False | OWASP API3 describes unauthorized property exposure and mass assignment. P, high confidence. |
| H3 | A server returning only pass/fail never leaks private geometry | False under a capable adaptive-query attacker | Our synthetic 1-D oracle locates one boundary within about 0.0000954 units in 20 yes/no queries. Applicability depends on granted probes and mitigations; not a deployed-system test. P for our fixture only. |
| H4 | A backend-for-frontend prevents all XSS abuse | False | RFC 10017 says BFF protects against extraction of backend-held OAuth tokens but malicious same-origin code can proxy requests. P, high confidence as source interpretation. |
| H5 | GitHub private repositories enforce H5's element-by-element permissions | Unproven and unsuitable as a guarantee | H4 repository sharing grants repository access; object-specific rights need an independently enforced backend and policy model. U for any particular enterprise configuration. |
| H6 | Existing app already has server authorization | Not established | Original Hub research identifies the static-app/backend gap; no current full code or deployment audit. U, verification required. |
| H7 | Confidential computing or encryption at rest alone is equivalent to zero knowledge | False as a general claim | These mechanisms protect against particular threats under particular assumptions; the complete computation, operator, key ownership and leakage model still require proof and independent review. |

## 3. Method and source log

Reviewed the Notion H5 task and original Hub plan; OWASP API Security Top 10 2023 API1 and API3, OWASP Authorization Cheat Sheet, RFC 9700 OAuth security best practices, RFC 10017 browser-app OAuth, and WCAG 2.2. Searches on 2026-11-13: “OWASP object authorization API security”; “OAuth browser based apps BCP PKCE”; “private analytics query output information disclosure.” The last query did not yield a reviewed privacy proof; an original toy attack demonstrates a limited leakage mode instead. Tested only a local Python fixture on synthetic one-dimensional geometry. No security assessment, real dataset, library licensing review, backend implementation, exploit against anyone, cost estimate, privacy legal opinion, independent second reader, or public third-party service test was performed. P = primary source or our direct measured fixture; U = proposal or unverified app behavior. Confidence is about a claim, not the readiness of the implementation.

## 4. Assets, actors, boundaries and threat model

Assets include source model bytes, private geometry, properties, element IDs, history and branch metadata, signed URLs, search indexes and tile derivatives, result geometry and identifiers, billing metadata, audit events and encryption keys. Roles to distinguish: data owner, tenant administrator, invited viewer, editor, checker, billing administrator, service operator, support, identity provider, payment processor, infrastructure provider, attacker and external plugin. A legitimate user may be authorized to check a model but not read or export it. A compromised browser, stolen session, malicious plugin or worker, confused tenant, overprivileged support, and an operator with broad infrastructure access have different powers.

Trust boundaries: (1) browser and local disk; (2) identity provider and OAuth redirect; (3) backend entry point; (4) authorization/policy and tenant database; (5) object storage, caches, queues, analytics workers, logs and backups; (6) third-party billing/telemetry; and (7) GitHub H4, which is a separate sharing surface. TLS protects traffic in transit, not an endpoint or an authorized user's browser; storage encryption protects data according to key access, not from a service authorized to decrypt. A signed object URL can remain usable until it expires or is invalidated even after a UI revocation—test the selected storage and CDN behavior rather than promise instant revocation.

For each security claim document the protected asset, attacker, permitted disclosure, trust in operator, check type, output precision, retention, authentication, allowed query volume and model ownership. Distinguish policy assurance (who may use what) from cryptographic assurance (who can learn what). Avoid promising perfect deletion from backups, fully immutable logs, or zero leakage without independently tested mechanisms.

## 5. Authorization and lifecycle design

Recommend deny-by-default policy evaluated on every relevant server request; use tenant identity from authenticated server context, not a client-supplied tenant ID alone. Model policy records should bind subject or group, tenant, resource, action, conditions, policy version and grant/revocation evidence. Object permission and property permission are separate. Typical actions: list existence, read metadata, read geometry, edit, publish, download, run a named check, view result, export result, grant, revoke, manage billing and administer tenant. Whether discovering an element's existence is itself protected must be decided.

Check all resource IDs in a request, not only the first: source model, target model, elements, revisions, result, attachments, job and output. Authorize both source and derived output independently. Do not use a partial response assembled by serializing all fields and hiding them in UI. Return allowlisted, role-appropriate fields; reject unauthorized patch properties; validate response schemas. Relationships and parent-to-child inheritance require an explicit rule for overlapping grants and denies. Never infer that paying for a plan grants access to a particular model: entitlement is a separate necessary predicate, not a replacement for membership or consent.

Re-evaluate authorization when a queued job starts and before results are delivered. Define what happens if permission is revoked mid-run, if membership changes during a model export, and how ACL revisions invalidate materialized views, search indexes and caches. Include tenant ID and policy revision in cache keys only after validating both; ensure cross-tenant isolation also in storage paths, background jobs and monitoring. An ACL change should trigger a bounded, measured revocation procedure with no unsupported instant-revocation promise. Signed URLs, offline copies, already downloaded geometry, analytics outputs and external repositories cannot generally be recalled by merely changing an ACL.

Invite acceptance, identity recovery, account deletion, role delegation, project transfer and tenant offboarding need explicit flows. Rate-limit and log authorization denials without logging sensitive geometry, bearer tokens, unredacted URLs or model contents. Logging access may itself expose existence and relationships. Audit log integrity and retention require a separate implementation and threat model; hash chains alone do not prove an operator cannot rewrite all history.

## 6. Authentication and client architecture

Separate authentication from authorization. For browser clients, RFC 9700 requires PKCE for public clients, discourages unsafe redirect patterns and prohibits passing access tokens as URI query parameters in its specified form. RFC 10017 describes authorization-code + PKCE and compares three browser architectures. A backend-for-frontend keeps OAuth tokens server-side; cookies should be Secure and HttpOnly, with suitable SameSite/host restrictions and CSRF protection. It reduces token exfiltration but does not stop an XSS script making requests through the legitimate browser. Apply contextual output encoding, dependency controls, CSP and integrity checks where supported; validate issuer, audience, expiry and required claims, and use tested identity-provider libraries rather than writing authentication primitives.

Direct browser OAuth may fit the static deployment but exposes a different token/storage threat profile and cannot by itself satisfy H5's backend enforcement requirement. A token-mediating backend is an intermediate architecture; it can expose access tokens to the browser depending on design. An application BFF centralizes sessions but introduces operations, state, CSRF and scaling responsibilities. Choose based on the deployment and service trust boundary, not on a claim that one pattern eliminates XSS. Define logout, session expiry, renewal and incident response. CORS is a browser origin control, not authorization against arbitrary HTTP clients.

## 7. Private checks and output leakage

Three alternatives: A, local check by a party entitled to read geometry, simple and offline but that party receives the model; B, trusted server computes on plaintext and returns a deliberately minimized result, feasible in principle but requires operator trust and leakage controls; C, privacy-preserving computation or trusted execution, potentially narrower exposure but dependent on exact cryptographic/attestation model, performance, side channels, key custody and independent validation. No benchmark or proof here supports choosing C.

Define operations as approved, versioned check recipes—not arbitrary attacker-controlled geometry predicates by default. Bind each job to a model version, authorized purpose, checker identity and approved result schema. Consider owner approval, least-precision results, quotas, query auditing, anomaly alerts, bounded access duration and controlled export, but do not imply these defenses mathematically prevent inference. A clash result listing exact contact point, two IDs and severity discloses much more than a project-level status; even a binary answer may be sensitive. Thresholds, suppression and differential privacy only provide guarantees under their exact algorithms and composition assumptions; do not label a simple rate limit or rounding as differential privacy. Decide whether the user may see their own geometry plus a redacted warning or a generic aggregate, and document utility loss.

## 8. Experiment: adaptive oracle leakage

Attached `experiment.py` models hidden 1-D interval [37.125, 42.875]. An attacker can send adaptive interval probes and receive only an overlap boolean. A binary search over [-100,x] finds the first boundary in [37.12491989135742, 37.12501525878906] using 20 queries, an interval 0.000095367431640625 units wide. Python float, one deterministic run, no server, ACL, noise, quota or spatial geometry. This demonstrates that repeated minimal answers can reveal a hidden boundary under these assumptions; it does not prove that a specific production API or its legitimate users could perform the same attack. Reproduce with `python3 experiment.py`; output saved alongside script.

## 9. Work-order-ready test inventory, not an approved plan

- Authentication: invalid issuer/audience, expired/replayed tokens, PKCE downgrade, redirect mismatch, logout, stolen/revoked session, CSRF and origin handling.
- Tenant isolation: two tenants, reused IDs, manipulated path/header/body, list vs detail, batch operations, search, stream, history and export; prove no cross-tenant reads or writes.
- Property exposure: authorized metadata-only user requests geometry, private prices, ACL or audit fields; overposting protected fields must be rejected.
- Access lifecycle: invite/accept/revoke, shared group change, ownership transfer, worker queue, in-flight job, cached output and expiring download URL; measure revocation and document residual access.
- Private checks: no unauthorized input access; jobs bound to immutable revisions; per-check approved output; result caching isolated by tenant and authorization context; repeated adaptive queries and sensitivity tests.
- Payments: out-of-order, duplicated and replayed webhook events; signature verification; grace periods, cancellation and refunds; no privilege escalation via client-supplied plan. Payment provider is not data authorization.
- Malicious input: oversized files, zip bombs, parser crashes, external URI/SSRF, path traversal, long-running jobs, worker compromise, log injection and resource limits. Isolate workers with minimum privileges and bounded CPU/memory/time; do not execute uploaded scripts.
- Operations: encrypted backups, restore into an isolated environment, key rotation, least-privilege support, retention expiry, incident response, data export and deletion verification with documented backup exceptions.
- Accessibility: keyboard operability, accessible authentication, visible understandable errors and status messages. WCAG conformance requires actual testing, not this checklist.

## 10. Integration, performance and alternatives

H4's GitHub transport is not a substitute for per-element server rights; data committed to an accessible repo is governed by repository access and may persist in history. Do not automatically upload offline projects, tokens or proprietary assets. Resolve stable identity between imported IFC GlobalId, application IDs and version IDs before defining policy targets. The source task says project is static and needs a backend; current app file-level inventory, deployment and storage behavior have not been audited here. Rendering and permission filtering must not expose unauthorized data through tiles, metadata, caches or file downloads.

Track authorization p50/p95 latency, throughput, number of checked resources, job queue latency, egress, storage, deleted-data lag and incident metrics on agreed synthetic fixtures; these are measurement categories, not promised targets. The 64-hour rough estimate is neither sufficient evidence of delivery nor a security budget. Provider, region, tenant isolation model and support operations remain unselected.

## 11. Open decisions and research exit gates

Owner decisions: intended actors and markets; model- and element-level sharing semantics; whether restricted checking is allowed and what it may reveal; trust in host/operator and location; permitted integrations and offline behavior; retention, backups and deletion; billing entitlements; deployment and service ownership; priority relative to H4. No default in this report is an approved decision. Before specification: map app/deployment code; formalize use cases and security properties; validate the backend/policy library and external dependencies; define threat and leakage model; build controlled prototype and adversarial tests; have an independent security review and re-estimate the actual scope. The repository's independent-reader requirement is not satisfied here.

## 12. Sources

- [H5 task](https://app.notion.com/p/3fecbfcc3a3881139bc7ed9832d6b76a); [Hub research](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/research/research-bim-hub.md): project intent; original research may be stale.
- [OWASP API1:2023 BOLA](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/); [API3 property authorization](https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/); [Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).
- [RFC 9700 OAuth security BCP](https://www.rfc-editor.org/rfc/rfc9700.html), January 2025; [RFC 10017 OAuth for Browser-Based Applications](https://www.rfc-editor.org/rfc/rfc10017.html), August 2026.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/), accessible authentication, keyboard and status requirements.
- Attached local experiment and output, author-generated 2026-11-13; not independently verified.


---
Research evidence files: [`experiments/notion-h5-server/`](experiments/notion-h5-server/). Original scripts and results reflect only the experiments described above.
