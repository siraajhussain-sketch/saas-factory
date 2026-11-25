# Approval Service Design

**Status:** Design proposal only. No issuer, signer, ledger, approval UI, execution worker, or external service is implemented.

## 1. Objective and non-goals

The approval boundary must prove that an authenticated owner approved one exact, bounded action for one product. Approval must be bound to immutable evidence and must not be reusable, silently widened, or interpreted as permission for unrelated work.

This design does not authorize product code changes, paid AI/API calls, cloud resources, billing, production credentials, customer data, deployment, DNS, public launch, or destructive operations. Those require separate decisions. The current validator remains read-only and plan-only.

## 2. Trust boundaries and roles

| Component | Responsibility | Must not be trusted to |
|---|---|---|
| Owner / approver | Review and explicitly approve a displayed scope | Approve through ambiguous text such as “continue” |
| Approval interface | Authenticate the owner and display the canonical request | Change scope after confirmation |
| Issuer / signer | Validate identity and policy, create and sign the payload | Accept agent-generated approval |
| Approval ledger | Persist status, revocation and one-time claims transactionally | Treat Git history, labels or comments as authoritative |
| Validator | Verify signature, scope, time and ledger state | Grant execution by itself |
| Future executor | Claim a valid approval and perform only the approved operation | Expand scope or infer permission |

Product agents, issue text, pull-request text, model output, repository files and workflow inputs are untrusted data. No component may approve its own request.

## 3. Owner identity and authorization

A future issuer must authenticate a real human owner through a separately controlled identity boundary.

Minimum requirements:
- Use a stable provider subject/user ID, not a display name or email string alone.
- Require strong authentication, preferably phishing-resistant MFA where supported.
- Verify the owner is authorized for the exact target product and repository at issuance time.
- Keep an explicit approver allowlist and documented recovery process.
- Do not treat an issue comment, label, PR review, commit author, workflow dispatch event, or workflow actor alone as proof that the owner approved the exact payload.
- Do not allow an agent, bot, or workflow to self-approve.

A GitHub App or identity provider may be evaluated later. GitHub OIDC can attest workflow identity; it does not, by itself, prove a human approved a particular immutable scope.

## 4. Canonical approval payload

The issuer must construct a versioned canonical payload. Unknown fields and ambiguous encodings must be rejected. The signature covers every authorization-relevant field.

Required fields:
- schema version, unique approval ID, cryptographically random nonce;
- product ID and exact repository owner/name;
- immutable ADR commit/blob identity and SHA-256 digest;
- exact phase ID and digest of the complete phase plan and acceptance criteria;
- exact target branch and normalized, explicit permitted path set;
- operation class and allowed action set;
- environment, defaulting to none;
- provider allowlist, defaulting to empty;
- maximum spend and currency, defaulting to zero;
- approver stable identity and authentication evidence reference;
- issued-at, not-before if used, expiry, and signing key ID.

Canonicalization must be deterministic and versioned (for example, a rigorously implemented canonical JSON profile). Path normalization must reject traversal, ambiguous separators, case-folding collisions where relevant, symlink escapes, and unexpected path expansion.

Any change to product, repository, ADR digest, phase-plan digest, branch, paths, operation class, provider policy, spend, environment, or validity window invalidates the approval.

## 5. Signing boundary

The current local HMAC verifier is a protocol prototype, not a production trust boundary. A shared HMAC secret gives every holder signing capability as well as verification capability.

Before any future implementation:
- Prefer asymmetric signing where the issuer holds the private key and validators receive only public verification keys.
- Keep private signing keys in a protected key boundary, never in source control, issue text, build artifacts, or ordinary workflow environment variables.
- Require key IDs, rotation, retirement, audit, and a documented compromise procedure.
- Ensure untrusted workflow changes cannot access or exfiltrate signing capability.
- Fail closed if the signer, key service, identity provider, or key metadata cannot be verified.

No signing algorithm or key-management vendor is selected here.

## 6. Issuance flow

1. A trusted interface loads a specific approval request and its immutable evidence.
2. The interface displays product, repository, ADR digest, phase-plan digest, branch, exact paths, operation class, environment, providers, spend ceiling, expiry and expected side effects.
3. The owner authenticates and explicitly approves that exact scope.
4. The issuer independently checks identity, repository authority, policy and request integrity.
5. The issuer creates a unique approval ID and nonce, applies a short expiry (maximum seven days unless a separately reviewed policy says otherwise), signs the canonical payload and records it as ISSUED.
6. The owner receives a human-readable receipt containing the approval ID and scope digest, not a signing secret.
7. The validator checks signature, key status, exact scope, time validity and ledger state. A valid result is still only a validated authorization candidate until a future executor atomically claims it.

Broad conversational consent is never converted into approval for spend, credentials, deployment, public launch or destructive operations.

## 7. Durable ledger, replay and revocation

A future ledger must be durable, access-controlled, backed up, monitored and transaction-capable. Enforce uniqueness for both approval ID and nonce.

Minimum states:
- ISSUED: available for a valid claim.
- REVOKED: revoked before claim; terminal.
- CLAIMED: atomically claimed by one execution attempt; includes a unique operation ID and claim time.
- SUCCEEDED: operation completed and independently recorded.
- FAILED: operation failed; recovery policy determines whether a safe retry is possible.
- EXPIRED: no longer claimable; may be derived or materialized.

The claim operation must be one transaction that checks signature digest, scope digest, expiry, revocation and current state, then conditionally changes ISSUED to CLAIMED. A unique constraint and transaction isolation must ensure concurrent workers cannot both win. A revoked approval must not be claimed. If the ledger is unavailable, no side effect starts.

### Crash and retry semantics

Do not promise exactly-once execution for arbitrary external side effects. A process can crash after a remote service accepted an action but before the ledger recorded success.

A future executor therefore needs:
- a stable operation/idempotency key derived from the approval ID and operation;
- a durable execution record and explicit CLAIMED state;
- provider-specific idempotency where available;
- reconciliation for uncertain outcomes;
- bounded leases and a recovery process that cannot silently issue a second operation;
- manual intervention when the outcome cannot be established safely.

A retry must resume or reconcile the same operation record. It must not mint a new approval or repeat an uncertain non-idempotent action. Revocation prevents a not-yet-claimed approval from starting; it cannot undo an operation already in progress.

## 8. Separate approval classes

Require separate, explicit decisions for architecture acceptance; each bounded implementation phase; paid provider/API use and paid infrastructure (provider, model/service, purpose, maximum spend, currency, duration and environment); secret creation or use, live integrations, billing activation and production data; production deployment, DNS changes and public launch; destructive migrations, deletion, data export, and security/privacy exceptions.

Approval for one class never implies another. Zero-spend approval must be enforced as zero, not as an informal budget expectation. A phase approval does not imply merge, release or deployment permission.

## 9. Audit, privacy and operations

Record only what is needed to prove and investigate the decision:
- approval ID and canonical payload digest;
- stable approver subject and authentication result/reference;
- scope, issue/expiry times and signing key ID;
- ledger state transitions and actor;
- validation and claim result;
- operation/idempotency correlation ID and final outcome.

Never log private keys, access tokens, passwords, raw credentials, or unnecessary personal data. Protect audit access, define retention and deletion rules, and make records tamper-evident. Alert on repeated invalid attempts, unexpected revocation, key rotation anomalies and failed recovery.

## 10. Required security tests before any issuer or executor

- Changing each authorization-relevant field invalidates the signature.
- Unknown fields, malformed canonicalization and duplicate JSON keys are rejected.
- Wrong owner, missing authentication, insufficient repository permission and self-approval are rejected.
- Expired, future-dated, revoked, retired-key and overlong approvals fail.
- Duplicate approval IDs and nonces are rejected.
- Concurrent claims permit exactly one successful transition.
- Revocation racing a claim has a deterministic serialized outcome.
- Ledger, identity or key-service unavailability fails closed.
- Replay after claim is rejected.
- Retries reconcile the same operation and do not duplicate side effects.
- Scope cannot cross products, repositories, ADRs, phases, branches, paths, operation classes, providers, environments or spend limits.
- Path traversal, symlink escape and normalization collisions are rejected.
- Audit output contains no secrets or unnecessary personal data.
- Key rotation, key compromise, backup restoration and incident recovery are tested.

## 11. Decisions deliberately deferred

No database, cloud vendor, key-management service, GitHub App, identity provider, hosting platform, approval UI, budget, or implementation timeline is selected. Availability and cost of any proposed no-cost tier must be verified before use; free tiers are not assumed to be durable, secure, or sufficient.

The next work should be a threat-model review and a no-cost feasibility comparison of identity and ledger options. Only after that review should an owner decide whether to authorize a narrowly scoped implementation proposal. The executor remains out of scope.
