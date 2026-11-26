import unittest

from control_plane.product_brief_validator import (
    BriefValidationError, validate_brief,
)

VALID_BRIEF = """# Product Brief

**Status:** Draft
**Product name:** Example product
**Owner:** Product owner
**Last updated:** 2026-11-26

## 1. Summary

A concise product summary.

## 2. Problem and customer

- Target buyer: Small business owner
- Primary users: Staff members
- Problem being solved: Manual workflow is error-prone
- Current alternatives: Spreadsheets
- Why this product should exist: Reduce missed follow-ups

## 3. Geography and operating context

- Initial market: UAE
- Applicable jurisdictions: UAE
- Languages: Arabic and English
- Currency and timezone requirements: AED and Asia/Dubai

## 4. Core workflows

Users create and track work items.

## 5. Data and privacy

- Data categories: Contact and business records
- Personal or sensitive data: UNKNOWN
- Data ownership: Each customer organization
- Retention and deletion expectations: UNKNOWN
- Export and audit requirements: CSV export; audit log

## 6. Tenant and authorization model

- Ownership root: Organization
- Membership relationships: Users belong to organizations
- Roles and permissions: Owner and staff
- Resource ownership graph: Organization owns records
- Cross-organization or delegated access: None
- Administrative access model: Restricted support access

## 7. Business model and cost constraints

- Pricing hypothesis: Monthly subscription
- Billing requirements: Deferred
- External providers: UNKNOWN
- Zero-cost alternatives: Local development and free tiers
- Maximum approved development spend: USD 0

## 8. Non-functional requirements

- Security: Server-side authorization
- Availability: Best effort for MVP
- Performance: Responsive common workflows
- Backup and recovery: Documented restore process
- Accessibility: Keyboard-accessible forms
- Localization: Arabic and English

## 9. MVP boundaries

- Included: Core record management
- Explicitly excluded: Automated billing
- Deferred: AI features

## 10. Risks and open questions

Market demand and willingness to pay remain UNKNOWN.

## 11. Acceptance criteria

Discovery package reviewed by the owner.
"""


class ProductBriefValidatorTests(unittest.TestCase):
    def test_complete_brief_passes(self):
        result = validate_brief(VALID_BRIEF)
        self.assertEqual(result["status"], "READY_FOR_DISCOVERY_REVIEW")
        self.assertFalse(result["side_effects"])
        self.assertEqual(result["provider_calls"], 0)
        self.assertEqual(result["spend_usd"], 0)

    def test_unknown_values_are_allowed(self):
        result = validate_brief(VALID_BRIEF.replace(
            "Small business owner", "UNKNOWN"
        ))
        self.assertTrue(result["checks"]["unknown_values_allowed"])

    def test_missing_section_blocks(self):
        brief = VALID_BRIEF.replace("## 11. Acceptance criteria", "## Acceptance")
        with self.assertRaisesRegex(BriefValidationError, "missing required sections"):
            validate_brief(brief)

    def test_blank_labeled_field_blocks(self):
        brief = VALID_BRIEF.replace("- Target buyer: Small business owner", "- Target buyer:")
        with self.assertRaisesRegex(BriefValidationError, "use UNKNOWN"):
            validate_brief(brief)

    def test_template_instruction_blocks(self):
        brief = VALID_BRIEF.replace("A concise product summary.", "Describe the product in one sentence.")
        with self.assertRaisesRegex(BriefValidationError, "instructions"):
            validate_brief(brief)

    def test_todo_blocks(self):
        with self.assertRaisesRegex(BriefValidationError, "placeholders"):
            validate_brief(VALID_BRIEF + "\\nTODO: research competitor pricing")

    def test_empty_document_blocks(self):
        with self.assertRaisesRegex(BriefValidationError, "empty"):
            validate_brief("  ")

    def test_unknown_heading_variant_does_not_substitute(self):
        brief = VALID_BRIEF.replace("## 6. Tenant and authorization model", "## 6. Tenant model")
        with self.assertRaisesRegex(BriefValidationError, "missing required sections"):
            validate_brief(brief)


if __name__ == "__main__":
    unittest.main()
