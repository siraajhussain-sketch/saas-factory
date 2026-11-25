# Cost and Provider Policy

## Default: zero spend

The factory must assume that no budget is available unless the owner explicitly approves a defined spend.

The following activities must not trigger paid provider usage:
- Repository inspection.
- Documentation review.
- Product intake.
- Architecture drafting and review.
- Deterministic validation.
- Dry runs and policy checks.
- Test execution that does not require a paid external service.

## Provider controls

Before enabling an external AI or service provider, record:
- Provider and exact model/service.
- Why a deterministic or free alternative is insufficient.
- Data that will be sent and how it is minimized.
- Environment and credential scope.
- Maximum spend per run and total budget.
- Rate limits, timeout, retry, and failure behavior.
- Approval owner and expiry.

Provider integrations must be disabled by default and must fail closed when configuration or approval is missing.

## Credentials

- Never commit credentials or place them in issues, pull requests, prompts, logs, or test output.
- Use scoped secrets and rotate them according to a documented process.
- Do not request or store production credentials during design or dry-run phases.
- Never test a dummy key against a live provider endpoint.

## Cost reporting

Every approved provider-backed run should report:
- Provider and model/service.
- Purpose and product.
- Execution identifier and time window.
- Estimated or reported usage and cost.
- Configured cap and whether it was reached.
- Errors, retries, and any unexpected charges.

## Prohibited assumptions

A free tier is not a guarantee of permanent availability, sufficient quota, or zero future cost. Any pricing or free-tier claim must be verified against the provider's current terms before use.
