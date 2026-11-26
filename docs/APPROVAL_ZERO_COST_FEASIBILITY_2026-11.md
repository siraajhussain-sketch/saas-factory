# Approval Infrastructure — Current Zero-Cost Feasibility Decision

**Assessment date:** 2026-11-26  
**Status:** Design-only; no account inspection, infrastructure setup, setting changes, credentials, or deployment performed.

## 1. Executive decision

**Do not build an approval service or executor yet. Keep the factory non-executable.**

The existing Phase 1 validator is a local, read-only plan validator. There is no current product-writing or deployment capability that requires a remote approval backend. Adding identity, signing, storage, monitoring, backups and recovery now would create a new security-critical system before there is a demonstrated need.

A genuinely useful zero-cost arrangement exists for human review, but no verified free-tier combination should currently be treated as a production-grade trust service with durable authorization, replay protection, recovery and operational guarantees.

## 2. Current official plan facts

The following facts were checked against official vendor documentation on the assessment date. They describe published plan capabilities, not the user's account state or a promise that a free tier will remain unchanged.

### GitHub

- GitHub Free currently lists unlimited public and private repositories and 2,000 Actions minutes per month for private repositories; Actions are free for public repositories.
- GitHub deployment environments, environment secrets and deployment protection rules are available in public repositories on current plans.
- On GitHub Free, private-repository environments are not available; private-repository environment features require GitHub Pro, Team or Enterprise. Required reviewers and other deployment protection rules on Free are available for public repositories.

**Implication:** Because this factory repository is public, GitHub environment reviewers are a plausible no-additional-infrastructure human gate for a future bounded workflow. They are not a complete approval service. A reviewer gate does not, by itself, provide the canonical signed payload, independent issuer, protected signing boundary, durable replay/revocation ledger, atomic one-time claim or uncertain-side-effect recovery.

Sources:
- https://github.com/pricing
- https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments

### Cloudflare Workers and D1

Published Workers Free limits include 100,000 requests per day and 10 ms CPU time per invocation. D1 Free currently lists 10 databases, 500 MB per database, 5 GB total account storage, 5 million rows read per day, 100,000 rows written per day and seven days of Time Travel recovery.

D1 batch operations execute statements sequentially as a SQL transaction and roll the batch back if a statement fails. This is a useful primitive for a conditional one-time claim, but a correct implementation would still need concurrency tests, unique constraints, authorization checks, backups/recovery procedures, monitoring and operational ownership.

Cloudflare states that Free-tier D1 operations fail after daily row-read or row-write limits are exceeded until the daily reset. That is fail-closed behavior for availability, not a service-level guarantee.

**Implication:** Workers + D1 could be evaluated for a low-volume technical prototype if a future approved phase genuinely needs it. It is not selected as a production approval ledger. Seven-day recovery, quota exhaustion, account-level operational risk and the absence of a reviewed identity/signing boundary remain material limitations. Do not create an account resource or deploy anything as part of this assessment.

Sources:
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/d1/platform/limits/
- https://developers.cloudflare.com/d1/worker-api/d1-database/
- https://developers.cloudflare.com/changelog/post/2026-09-01-d1-free-tier-limit-enforcement/

### Supabase

Supabase Free currently lists a 500 MB database and up to 50,000 monthly active users for Auth, but free projects can pause after one week of inactivity and automatic backups are not included in the Free plan.

**Implication:** It is convenient for experiments, but those pause and recovery characteristics make it a poor default for a security-critical approval ledger that should be available when an operation is about to be claimed.

Sources:
- https://supabase.com/pricing

## 3. Option comparison

| Option | Can be zero additional spend? | Useful security property | Important missing property | Decision |
|---|---|---|---|---|
| Manual owner review in issues/PRs | Yes, within existing GitHub usage | Human-visible review trail | Comments and labels are not machine authorization | Use for discussion only |
| GitHub environment required reviewer on this public repo | Yes, subject to current plan and feature availability | A named reviewer must approve a gated job | Not a complete signed scope, issuer, replay ledger or recovery system | Candidate human gate only; not configured |
| Cloudflare Worker + D1 Free | Published Free tier | Separate service boundary, secrets support, transactional D1 batch | Quotas, seven-day recovery, operational ownership, and no identity model by default | Prototype candidate only; not provisioned |
| Supabase Free | Published Free tier | Integrated Auth and database | Inactivity pause and no automatic backups on Free | Not recommended for this ledger |
| Self-hosted service | Potentially no new hosting bill only if suitable infrastructure already exists | Full design control | Patching, uptime, key custody, backups, monitoring and incident response become owner's responsibility | Not recommended |

## 4. Recommended architecture decision

### Now

1. Keep the existing local validator read-only and plan-only.
2. Continue to use GitHub issues and pull requests for discussion and human review.
3. Never interpret conversational “OK”, “continue”, labels, issue comments or workflow dispatch alone as machine authorization for writes, spending, credentials, production data or deployment.
4. Do not add a backend, database, GitHub App, OAuth configuration, signing key, secret, Cloudflare resource or Supabase project.
5. Do not add an executor or connect product repositories.

### If a future bounded workflow needs a human gate

First evaluate GitHub environment required reviewers on this public repository, with a workflow that displays the immutable request digest and exact proposed scope before the gate. This would remain a human workflow gate, not a replacement for an authenticated issuer and replay-protected ledger. Any configuration change requires a separate approval.

### Only if a real execution use case emerges

Run a separate architecture decision for:
- authenticated owner identity and repository authority;
- isolated asymmetric signer with key IDs and rotation;
- canonical versioned payload bound to an immutable repository revision and phase-plan digest;
- durable ledger with unique approval ID and nonce;
- atomic claim/revocation semantics and concurrency tests;
- audit, backup, restore, outage and incident response;
- a verified operating-cost ceiling and named operational owner.

The executor remains a separate later decision, with its own scope, credentials, idempotency and recovery design.

## 5. Explicit non-authorization

This assessment authorizes no GitHub setting change, environment creation, reviewer assignment, app installation, OAuth/OIDC setup, Cloudflare or Supabase account/resource creation, database, secret, key generation, billing change, paid provider, product repository write, execution worker, deployment or public launch.

## 6. Decision status

**Selected now:** manual owner review; no remote approval infrastructure; no executor.

**Potential later candidate:** GitHub environment required reviewers as an additional human gate for a public-repository workflow, subject to a separate configuration review.

**Not selected:** Cloudflare D1, Supabase, self-hosted signer/ledger, or any production approval service.
