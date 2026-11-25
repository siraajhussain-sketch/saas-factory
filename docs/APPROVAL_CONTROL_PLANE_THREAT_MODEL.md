# Approval Control Plane — Threat Model and Security Review

**Status:** Design review artifact. No production service or execution capability exists.

## 1. Scope

This threat model covers the proposed owner-approval boundary: request construction, human identity, approval issuance, signing, validation, ledger state, revocation, audit and a possible future executor claim. It does not assess any product's application security. Each product requires its own threat model.

## 2. Security objectives

1. Only an authenticated, authorized human can approve a request.
2. Approval is bound to one immutable product, repository, architecture decision, phase plan and exact operation scope.
3. An approval cannot be replayed or concurrently claimed more than once.
4. Revocation and expiry are enforced before a claim.
5. Missing or unavailable trust dependencies stop the operation.
6. No approval silently grants spend, credential, production-data, deployment or destructive-operation permission.
7. Audit evidence is useful without exposing secrets or unnecessary personal data.

## 3. Assets

Owner identity and authentication session; signing private key and public-key metadata; canonical approval payload and scope digests; approval ID and nonce; ledger records, revocation state and claim state; immutable ADR and phase-plan revisions; product repository identity and permitted path set; provider, spend and environment constraints; audit trail; and any future executor credentials and idempotency records.

## 4. Trust boundaries

| Boundary | Untrusted input crossing it | Required control |
|---|---|---|
| Product request → approval interface | Product brief, issue text, agent-generated plan | Treat as data; schema validation and owner-visible review |
| Interface → issuer | User session and approval confirmation | Strong authentication, session protection, explicit confirmation and server-side authorization |
| Issuer → signer | Canonical payload | Strict schema, canonicalization, policy check, key isolation |
| Validator → ledger | Approval ID, nonce and requested scope | Authenticated access, transactional state checks, least privilege |
| Workflow → future executor | Event payload, branch, paths and artifacts | Never treat workflow input as authority; independently validate signed scope |
| Executor → product/provider | Repository write or external side effect | Narrow credentials, exact path checks, idempotency and separate approval class |

## 5. Threats and mitigations

| Threat | Example | Required mitigation |
|---|---|---|
| Spoofed approver | Agent claims the owner said yes | Authenticated identity and explicit owner confirmation; reject model text as evidence |
| Confused deputy | Trusted workflow is tricked into acting on another product | Bind exact repository owner/name, product ID and immutable plan digest |
| Scope expansion | Paths or spend are changed after approval | Sign every authorization field; compare exact canonical digest |
| ADR substitution | Architecture file changes after approval | Bind immutable commit/blob and SHA-256; mismatch blocks |
| Replay | Same signed approval is submitted again | Unique ID and nonce plus transactional one-time claim |
| Race condition | Two workers claim simultaneously | Atomic conditional transition and database uniqueness constraints |
| Revocation race | Worker starts while owner revokes | Serialize claim/revocation transaction; in-progress actions cannot be undone |
| Key theft | Workflow logs or untrusted job expose signing key | Isolated asymmetric signer; no key in repository or untrusted workflow |
| Workflow compromise | Attacker changes workflow to misuse secrets | Do not use workflow-accessible secrets as the sole signer boundary |
| Path traversal | Relative path or symlink escapes approved directory | Canonical normalization, root confinement, symlink policy and adversarial tests |
| Provider escalation | Agent turns on a paid API or cloud resource | Empty provider allowlist and zero spend by default; separate approval class |
| Environment escalation | Test approval is used against production | Signed environment defaults to none; executor verifies exact environment |
| Ledger outage | Revocation state cannot be checked | Fail closed; no permissive offline fallback |
| Partial side effect | Remote action succeeds but worker crashes before recording success | Stable idempotency key, durable operation record and reconciliation |
| Audit leakage | Tokens or personal data appear in logs | Structured allowlisted fields, redaction, access controls and retention limits |
| Insider misuse | Collaborator broadens a request | Explicit approver policy, least privilege, independent review for high-risk classes and immutable audit |

## 6. Abuse cases that must be blocked

- A product agent approves its own generated plan.
- A label, comment, issue closure, PR review or “continue” message is interpreted as signed authorization.
- An approval for one product or repository is reused against another.
- An approval for one phase is reused for a later phase.
- A changed ADR, phase plan, branch or path list is accepted under an old signature.
- A zero-spend approval invokes a paid model or provisions billable infrastructure.
- A staging approval is used with production credentials or data.
- Two concurrent workers both execute the same approval.
- A revoked, expired, malformed or unknown-key approval is accepted.
- A ledger or identity outage causes a permissive fallback.
- A retry repeats an external action whose first outcome is uncertain.
- A workflow modified by an untrusted actor gains access to signing capability.

## 7. Minimum release criteria for a future approval service

All criteria are blocking:
- documented owner identity and recovery model;
- verified repository permission checks;
- canonical payload schema and independent test vectors;
- protected signing boundary with rotation and compromise response;
- durable transactional ledger with unique ID/nonce constraints;
- atomic claim and revocation semantics;
- adversarial tests for scope tampering, concurrency, replay, expiry and outage;
- audit and privacy controls;
- independently reviewed threat model;
- verified operational cost and recovery plan;
- explicit owner approval of the chosen infrastructure and implementation scope.

Passing these criteria would authorize consideration of a separate executor design, not execution itself.

## 8. Current residual risks and status

| Area | Current status |
|---|---|
| Local signature verification | Prototype only; shared HMAC key model |
| Authenticated owner issuer | Not implemented |
| Protected signing key | Not implemented |
| Durable replay/revocation ledger | Not implemented |
| Atomic one-time claim | Not implemented |
| Execution worker | Not implemented |
| Product repository writer | Not implemented |
| Paid providers, credentials, billing and deployment | Not configured or authorized |

The present validator is safe to describe as a read-only, plan-only prototype. It must not be used to authorize side effects.

## 9. Review decision

**Decision: remain design-only.** The highest-risk gaps are owner identity, signing-key isolation, durable atomic replay/revocation state, and recovery from uncertain external side effects. Do not build an executor or connect product repositories until these gaps have a reviewed, affordable design and the owner explicitly approves the next bounded phase.
