import unittest

from control_plane.phase2_validator import (
    PackageValidationError, validate_document, validate_evidence_rows,
    validate_package,
)

DISCOVERY = """# Discovery
## 1. Executive assessment
Completed assessment.
## 2. Buyer and user
Buyer details.
## 3. Problem and workflows
Workflow details.
## 4. Alternatives and competition
Alternatives.
## 5. Market and geography
Geography.
## 6. Business model hypotheses
Business model.
## 7. MVP boundary
Included and excluded.
## 8. Risks and unknowns
Risks.
## 9. Recommendation and next decision
Recommendation.
"""
ARCH = """# Architecture
## 1. Context and quality attributes
Context.
## 2. Domain model
Entities.
## 3. Ownership and authorization
Ownership.
## 4. Data and privacy
Data.
## 5. Application and persistence design
Persistence.
## 6. Integrations and dependencies
Dependencies.
## 7. Localization and financial correctness
Localization.
## 8. Security and threat model
Threats.
## 9. Operations
Operations.
## 10. Test and acceptance strategy
Tests.
## 11. Architecture decisions
ADRs.
## 12. Open decisions and risks
Open items.
## 13. Implementation phase proposal
Phase proposal.
"""
EVIDENCE = """# Evidence
| ID | Claim / question | Evidence type | Source / URL | Publisher / author | Published date | Access date | Geography | Confidence | Limitations | Decision informed |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 | Pricing page lists a free tier | Primary source | https://example.com/pricing | Example | 2026-11-01 | 2026-11-26 | Global | Medium | May change | Cost choice |
## Evidence types
Types.
## Confidence guidance
Confidence.
## Rules
Rules.
"""


class Phase2ValidatorTests(unittest.TestCase):
    def test_complete_package_passes_structure_only(self):
        result = validate_package(DISCOVERY, ARCH, EVIDENCE)
        self.assertEqual(result["status"], "READY_FOR_HUMAN_REVIEW")
        self.assertEqual(result["checks"]["evidence_rows"], 1)
        self.assertFalse(result["side_effects"])
        self.assertEqual(result["provider_calls"], 0)
        self.assertEqual(result["spend_usd"], 0)

    def test_missing_heading_blocks(self):
        with self.assertRaisesRegex(PackageValidationError, "missing required sections"):
            validate_document("# Discovery\n## 1. Executive assessment\n", "discovery", "discovery")

    def test_unfinished_placeholder_blocks(self):
        with self.assertRaisesRegex(PackageValidationError, "placeholder"):
            validate_document(DISCOVERY + "\nTODO: confirm buyer.\n", "discovery", "discovery")

    def test_empty_evidence_register_blocks(self):
        with self.assertRaisesRegex(PackageValidationError, "at least one"):
            validate_evidence_rows("# Evidence\n| ID | Claim |\n|---|---|\n")

    def test_source_evidence_requires_url(self):
        invalid = EVIDENCE.replace("https://example.com/pricing", "Not provided")
        with self.assertRaisesRegex(PackageValidationError, "source URL"):
            validate_evidence_rows(invalid)

    def test_evidence_row_requires_all_columns(self):
        invalid = EVIDENCE.replace("| Global | Medium | May change | Cost choice |", "| Global | Medium |")
        with self.assertRaisesRegex(PackageValidationError, "11 register columns"):
            validate_evidence_rows(invalid)

    def test_assumption_is_allowed_without_url(self):
        row = "| A1 | Buyer willingness to pay is unknown | assumption | Owner hypothesis; unverified | Owner | unknown | 2026-11-26 | Initial market | Low | Not validated | Interview plan |"
        self.assertEqual(validate_evidence_rows(EVIDENCE + "\n" + row), 2)

    def test_unknown_evidence_type_blocks(self):
        invalid = EVIDENCE.replace("Primary source", "Internet fact")
        with self.assertRaisesRegex(PackageValidationError, "unrecognized evidence type"):
            validate_evidence_rows(invalid)


if __name__ == "__main__":
    unittest.main()
