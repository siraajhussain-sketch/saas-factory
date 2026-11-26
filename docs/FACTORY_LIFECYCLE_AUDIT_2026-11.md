# Factory Lifecycle Audit — 2026-11-26

**Review type:** Read-only repository and documentation audit  
**Scope:** Public generic factory lifecycle from product intake through discovery, architecture, approval and implementation handoff  
**Decision:** Keep the factory non-executable. Resolve the documented integration and trust gaps before considering an executor.

## 1. Executive assessment

The repository has useful, independently testable foundations:

- Product Brief structural validator.
- Phase 2 discovery/architecture/evidence package validator.
- Strict AI-output structure and exact-source-span provenance validator.
- Deterministic mock adapter and a small synthetic NLP evaluation harness.
- Local plan-only approval validator with strict input and path checks.
- Approval-service design, threat model, approval gates and cost-policy documentation.

However, these are separate components and documents. There is no end-to-end workflow runner, persisted lifecycle state, common artifact manifest, or verified handoff that automatically connects one stage's output to the next. The orchestrator and lifecycle state machine remain proposals, not implemented capabilities.

**Overall classification: GOVERNANCE AND VALIDATION FOUNDATION — NOT AN OPERATIONAL FACTORY.**

No product repository, external provider, credential, cloud resource, billing service, customer data, deployment target or executor was accessed or configured during this review.

## 2. Lifecycle trace

| Lifecycle stage | Existing capability | Audit finding |
|---|---|---|
| Product intake | Product Brief template and issue contract | Human/manual intake; no integrated intake workflow or durable case record |
| Intake validation | `product_brief_validator.py` | Working local structural check; not connected to a lifecycle state store or Phase 2 runner |
| Discovery | Discovery report and evidence templates; written operating contract | Process is documented, but research and report production remain manual |
| Architecture | Architecture package template and ADR guidance | Product-specific design is documented as required; no automatic completeness-to-decision handoff |
| AI-assisted NLP | Output contract, mock adapter, evaluator and synthetic multilingual dataset | Contract and tests exist; no real model, provider or workflow integration |
| Phase 2 validation | `phase2_validator.py` | Working local structural check; does not establish factual accuracy or architecture quality |
| Owner decision | Approval gates and issue contract | Human review is specified; no authenticated approval interface or durable decision ledger |
| Approval validation | Local HMAC plan-only validator | Prototype only; cannot authenticate an owner or prevent durable replay |
| Repository setup | Design and approval requirements | Not implemented; no repository provisioner |
| Implementation | Orchestrator design and roadmap | No generic implementation worker in this repository |
| Validation and human acceptance | CI for factory's own Python tests; documented future product gates | No product-specific build/test worker or acceptance evidence pipeline |
| Release | Separate release gate documented | No release automation, credentials or deployment capability |

## 3. Findings and priorities

### F-01 — No connected lifecycle state or artifact handoff

**Priority: High**

The validators accept file paths and return independent JSON results. There is no common product-case identifier, versioned artifact manifest, lifecycle state store, or workflow that proves the validated Product Brief is the exact brief used to create a particular discovery and architecture package.

**Risk:** A person can accidentally review mismatched versions or skip a stage while the repository still contains individually passing validators.

**Recommendation:** Define a read-only lifecycle manifest and transition contract first. It should record product/case ID, artifact paths and content digests, validator version/results, timestamps, owner decisions and current state. It must not imply authorization. Keep this local and file-based initially; no database or service is required.

### F-02 — Approval is not a trusted authorization service

**Priority: Critical — blocking any executor**

The current HMAC validator is a local plan-only prototype. The approver field is not authenticated identity; any holder of the shared HMAC key can sign; no durable replay/revocation ledger or atomic one-time claim exists.

**Risk:** A passing local signature check cannot prove that the owner approved the exact action, nor prevent reuse.

**Recommendation:** Preserve the existing design-only decision. Do not connect product repositories, create signing keys, add secrets, or build an executor. Any future approval-service implementation needs a separately reviewed identity, signer, ledger, recovery and cost design, followed by explicit owner approval.

### F-03 — Phase 2 structural checks are not evidence or architecture verification

**Priority: High**

The package validator checks headings, obvious placeholders, evidence-table shape and basic evidence-type/source-URL requirements. It does not verify that URLs resolve, sources are authoritative/current, claims are supported, dates/geography are correct, legal conclusions are sound, or architecture/security decisions are correct.

**Risk:** A structurally passing package could still contain weak, irrelevant or misleading evidence.

**Recommendation:** Keep its status as `READY_FOR_HUMAN_REVIEW`. Add a human-review checklist and explicit evidence dispositions (accepted, disputed, stale, rejected, needs follow-up) in a later bounded documentation phase. Do not relabel structural validation as factual verification.

### F-04 — AI output validation proves traceability, not interpretation

**Priority: High before model selection**

The AI output contract checks strict JSON shape and whether an excerpt is an exact substring of a supplied source. It cannot establish that the model's normalized statement accurately represents the excerpt. The mock adapter is fixed fixture data, and the current multilingual dataset is small and synthetic.

**Risk:** A model could cite a genuine excerpt but misinterpret it, omit a critical qualifier or misclassify a statement.

**Recommendation:** Keep AI disabled. Continue with the documented plan to expand the UAE Arabic/English and Pakistan Urdu/mixed-language evaluation set, obtain fluent human review, and define per-language acceptance thresholds before comparing candidate models. No model or API integration is authorized by this audit.

### F-05 — Product Brief validator is intentionally lightweight

**Priority: Medium**

The validator checks required headings, selected template phrases and blank labeled fields. It does not assess completeness of meaning, consistency, evidence, language quality or whether a nonblank answer is useful. Phrase matching may also reject some legitimate text or miss unfamiliar template instructions.

**Risk:** A pass could be mistaken for a high-quality brief.

**Recommendation:** Keep the narrow status `READY_FOR_DISCOVERY_REVIEW`; explain the limitation in the CLI and review checklist. Do not make this validator a mandatory security or approval gate.

### F-06 — Roadmap and lifecycle naming need normalization

**Priority: Medium**

The roadmap currently places Phase 2D (brief validation) before Phase 2 (discovery) and lists optional AI phases separately. This is understandable as a work history but less clear as a product lifecycle sequence.

**Risk:** Future contributors may confuse implementation chronology with operational stage order.

**Recommendation:** Distinguish lifecycle stages (Intake, Discovery, Architecture, Owner Decision, Implementation, Validation, Release) from engineering work packages (Phase 1, 2A, 2B, etc.) in future roadmap edits.

### F-07 — Product-specific isolation is a design rule, not an enforced provisioning boundary

**Priority: High before repository automation**

The documentation correctly requires separate product repositories, architecture, credentials and data boundaries. No repository provisioner or product-repository policy enforcement exists in this public generic factory.

**Risk:** Future automation could accidentally reuse a repository or configuration unless target identity and permissions are independently checked.

**Recommendation:** Before any provisioner, define and test an explicit product-to-repository registry, immutable repository identity, owner/visibility checks, least-privilege permissions and a no-cross-product test suite. Do not connect the Salon Client Book repository or its factory as part of this work.

## 4. What is genuinely working today

- Factory CI currently exercises the standard-library test suite. The latest Product Brief validator update completed successfully with **69 tests passing**.
- The validators are read-only and require `--dry-run` at their command-line entry points.
- AI output validation is provider-independent and does not call a model.
- The mock adapter does not perform inference or network access.
- The approval validator returns plan-only validation and has no executor.
- Governance documentation consistently says labels, comments and conversational “continue” messages are not machine authorization.
- Provider access, paid services, credentials, production data and deployment remain disabled/unconfigured.

These facts describe the current repository, not proof of product security or production readiness.

## 5. Recommended next work — in order

1. **Lifecycle manifest and state contract (read-only):** define a versioned, local JSON manifest for a product case, its artifact digests, validator results, human review decisions and lifecycle status. No database, network or executor.
2. **Human review checklist:** define what a person must inspect in discovery, evidence, architecture, cost and security before changing a case from draft to owner review.
3. **Read-only consistency checker:** verify that required artifacts belong to the same case/version and that the state transition is allowed. It must never treat a manifest field, label or comment as authorization.
4. **Only then reassess integration:** decide whether a local file-based workflow is sufficient for initial use. Do not introduce cloud infrastructure simply to connect validators.
5. **Keep approval-service and executor work blocked** until critical identity, signing, replay/revocation and recovery gaps have a separately approved solution.

## 6. Explicit exclusions and safety boundary

This audit authorizes no provider/model selection or calls, paid service, infrastructure, credential, repository provisioning, product-repository write, production-data use, billing, deployment, DNS/public launch, destructive operation, signing-key creation or executor.

The public generic factory remains separate from the Salon Client Book repository and its salon-specific factory.

## 7. Audit conclusion

The foundation is progressing, but it is not yet an autonomous SaaS factory. The next best investment is a small, deterministic, zero-cost lifecycle manifest and consistency contract—not an AI agent, cloud approval service or code-writing worker.

**Disposition: READY FOR OWNER REVIEW — DOCUMENTATION AUDIT ONLY.**
