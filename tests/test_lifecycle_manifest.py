import hashlib, tempfile, unittest
from pathlib import Path
from control_plane.lifecycle_manifest import ManifestValidationError, validate_manifest

class LifecycleManifestTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
  (self.root/"brief.md").write_text("# Product brief\n",encoding="utf-8")
  digest=hashlib.sha256((self.root/"brief.md").read_bytes()).hexdigest()
  self.manifest={"schema_version":"1.0","case_id":"case-demo-001","product_id":"product-demo","lifecycle_state":"INTAKE",
   "created_at":"2026-11-26T10:00:00Z","updated_at":"2026-11-26T10:00:00Z",
   "artifacts":[{"id":"brief-v1","kind":"product_brief","path":"brief.md","sha256":digest}],
   "validator_runs":[{"id":"brief-check-1","validator":"product_brief_validator","status":"passed","recorded_at":"2026-11-26T10:01:00Z","artifact_ids":["brief-v1"]}],
   "human_reviews":[{"id":"review-1","stage":"intake","reviewer_label":"Owner (recorded label)","decision":"not_reviewed","recorded_at":"2026-11-26T10:02:00Z","notes":"No review has been performed."}],
   "state_history":[{"from":None,"to":"INTAKE","recorded_at":"2026-11-26T10:00:00Z","reason":"Case created"}]}
 def tearDown(self): self.temp.cleanup()
 def test_valid_manifest_passes_without_authorizing(self):
  result=validate_manifest(self.manifest,self.root)
  self.assertEqual(result["status"],"STRUCTURALLY_VALID_FOR_HUMAN_REVIEW"); self.assertFalse(result["authorization_granted"]); self.assertFalse(result["side_effects"])
 def test_hash_mismatch_blocks(self):
  self.manifest["artifacts"][0]["sha256"]="0"*64
  with self.assertRaisesRegex(ManifestValidationError,"SHA-256 mismatch"): validate_manifest(self.manifest,self.root)
 def test_parent_traversal_blocks(self):
  self.manifest["artifacts"][0]["path"]="../outside.md"
  with self.assertRaisesRegex(ManifestValidationError,"parent traversal"): validate_manifest(self.manifest,self.root)
 def test_absolute_path_blocks(self):
  self.manifest["artifacts"][0]["path"]=str(self.root/"brief.md")
  with self.assertRaisesRegex(ManifestValidationError,"absolute paths"): validate_manifest(self.manifest,self.root)
 def test_missing_artifact_blocks(self):
  self.manifest["artifacts"][0]["path"]="missing.md"
  with self.assertRaisesRegex(ManifestValidationError,"missing or escapes"): validate_manifest(self.manifest,self.root)
 def test_symlink_blocks(self):
  (self.root/"linked.md").symlink_to(self.root/"brief.md"); self.manifest["artifacts"][0]["path"]="linked.md"
  with self.assertRaisesRegex(ManifestValidationError,"symlink"): validate_manifest(self.manifest,self.root)
 def test_unknown_artifact_reference_blocks(self):
  self.manifest["validator_runs"][0]["artifact_ids"]=["not-here"]
  with self.assertRaisesRegex(ManifestValidationError,"unknown artifact"): validate_manifest(self.manifest,self.root)
 def test_invalid_state_transition_blocks(self):
  self.manifest["lifecycle_state"]="IMPLEMENTATION"
  self.manifest["state_history"].append({"from":"INTAKE","to":"IMPLEMENTATION","recorded_at":"2026-11-26T10:03:00Z","reason":"Skip stages"})
  with self.assertRaisesRegex(ManifestValidationError,"transition is not allowed"): validate_manifest(self.manifest,self.root)
 def test_state_must_match_history(self):
  self.manifest["lifecycle_state"]="DISCOVERY"
  with self.assertRaisesRegex(ManifestValidationError,"does not match state_history"): validate_manifest(self.manifest,self.root)
 def test_review_record_does_not_authorize(self):
  self.manifest["human_reviews"][0]["decision"]="accepted"
  result=validate_manifest(self.manifest,self.root)
  self.assertFalse(result["authorization_granted"]); self.assertIn("not authenticated",result["limitations"][0])
 def test_naive_timestamp_blocks(self):
  self.manifest["updated_at"]="2026-11-26T10:00:00"
  with self.assertRaisesRegex(ManifestValidationError,"timezone is required"): validate_manifest(self.manifest,self.root)

if __name__=="__main__": unittest.main()
