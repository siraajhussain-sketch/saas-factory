# Approval Infrastructure Options — Zero-Spend Feasibility

**Status:** Read-only design comparison. No app, service, database, key, secret, workflow, permission, billing setting or external account has been created or changed.

## 1. Decision summary

**Current decision: keep approval manual and keep the factory non-executable.**

The repository currently has a read-only validator and documentation. There is no product writer or execution worker to authorize. Adding an approval service now would create operational cost and a new security boundary without enabling a necessary capability.

A no-cost claim must not be confused with a no-risk or production-suitable design. Free tiers can change, have quotas, lack recovery guarantees, or require a paid plan for essential controls.

## 2. Options

| Option | Direct cost assumption | Security value | Missing controls / risks | Current decision |
|---|---|---|---|---|
| Manual owner review; no executor | No new infrastructure | Human remains in control; no automated side effect can follow a comment | Not machine-verifiable; depends on keeping all automation non-executable | **Use now** |
| GitHub issue/PR review and labels | Uses existing GitHub workflow | Useful discussion and visible audit trail | Mutable text and labels are not signed, scoped, one-time credentials; no atomic replay ledger | Use for discussion only |
| GitHub Actions dispatch plus actor checks | May use existing Actions allowance; actual limits and plan must be checked | Can identify the workflow trigger and enforce trusted refs and allowlists | Actor identity does not prove approval of exact ADR/phase/path scope; workflow changes and secrets create risk; no durable replay/revocation ledger by itself | Not sufficient alone |
| GitHub App plus external identity and signer | App setup may have no separate charge; hosting/key services may not | Can separate human identity, repository permissions and signing | More moving parts; protected key boundary and durable ledger still needed; costs and operational ownership unknown | Defer |
| Managed signer/key service plus transactional database | Free-tier availability varies; paid usage may be required | Stronger key isolation, durable state and atomic claims when correctly designed | Vendor lock-in, quotas, backup/recovery, security configuration and possible ongoing charges | Defer |
| Self-hosted signer and ledger | Could run on existing infrastructure only if suitable capacity already exists | Full control over identity, signing and state | Server maintenance, patching, backups, availability, monitoring and secret protection; “free” hosting is not assumed | Not recommended at this stage |

## 3. What GitHub can and cannot provide

GitHub can provide repository identity, workflow event metadata, permissions, review discussion and CI. These are useful inputs to a future approval system.

They do not automatically provide the complete security property required here:
- authenticated confirmation of every field in an immutable approval payload;
- a protected signing key that untrusted workflow changes cannot access;
- a durable transactional record for revocation and one-time claim;
- atomic exclusion of concurrent workers;
- safe recovery from an uncertain external side effect.

A manually dispatched workflow or an approved pull request must not be treated as a substitute for these controls.

Repository plan, environment availability, reviewer protection, Actions quotas, collaborator permissions and workflow restrictions have not been inspected in this phase. Do not infer them from the fact that CI currently runs.

## 4. Minimum questions before selecting any future option

Before proposing implementation, verify:
1. Which GitHub account or organization owns the target repository and which plan applies.
2. Who has admin, maintain, write and Actions permissions.
3. Whether trusted workflow paths and policy files can be protected against unauthorized changes.
4. Whether the selected identity mechanism can prove the human approver and repository authority.
5. Whether the signer can be isolated from product workflows and untrusted code.
6. Whether the ledger supports durable transactions, uniqueness constraints, backups and restoration.
7. What happens when identity, signer, ledger or provider is unavailable.
8. The full cost ceiling, quota limits, retention and operational burden.

Verification must be read-only. Do not upgrade plans, enable billing, install apps, add secrets, create cloud resources or change repository settings as part of feasibility assessment.

## 5. Recommended staged path

### Now — no new infrastructure
- Keep the deterministic validator read-only.
- Use issues and pull requests for human discussion and evidence only.
- Record owner decisions in documentation, but do not let workflows interpret comments or labels as authorization.
- Keep provider access, product-repository writes and deployment disabled.

### Later — only after a separate owner decision
- Compare a GitHub identity interface with a separately isolated signer.
- Select a durable transactional ledger only after verifying cost, retention, recovery and concurrency guarantees.
- Implement issuer and ledger as a bounded, independently tested phase.
- Perform adversarial security review before considering an executor.
- Design any executor separately, with its own repository/path permissions, idempotency, recovery and approval scope.

## 6. Explicit non-authorization

This document does not authorize a GitHub App installation, OAuth/OIDC configuration, plan upgrade, repository setting change, workflow modification, secret creation, signing-key generation, database, hosting, provider/API use, product implementation, billing, production access or deployment.
