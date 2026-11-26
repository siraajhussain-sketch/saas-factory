"""Read-only validation for a product case lifecycle manifest."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION="1.0"
STATES=("INTAKE","DISCOVERY","ARCHITECTURE","OWNER_REVIEW","IMPLEMENTATION_PLANNING","IMPLEMENTATION","ACCEPTANCE","RELEASE_REVIEW","RELEASED","CLOSED")
NEXT_STATE={"INTAKE":"DISCOVERY","DISCOVERY":"ARCHITECTURE","ARCHITECTURE":"OWNER_REVIEW","OWNER_REVIEW":"IMPLEMENTATION_PLANNING","IMPLEMENTATION_PLANNING":"IMPLEMENTATION","IMPLEMENTATION":"ACCEPTANCE","ACCEPTANCE":"RELEASE_REVIEW","RELEASE_REVIEW":"RELEASED","RELEASED":None,"CLOSED":None}
DECISIONS={"accepted","rejected","needs_changes","deferred","not_reviewed"}
VALIDATOR_STATUSES={"passed","blocked","warning","not_run"}
SLUG=re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")
SHA256=re.compile(r"^[a-f0-9]{64}$")

class ManifestValidationError(ValueError):
    """Invalid lifecycle manifest or referenced artifact."""

def require(ok: bool, message: str) -> None:
    if not ok: raise ManifestValidationError(message)

def string(value: Any, field: str, limit: int=500) -> str:
    require(isinstance(value,str) and bool(value.strip()),f"{field}: must be a non-empty string")
    require(len(value)<=limit,f"{field}: exceeds {limit} characters")
    return value.strip()

def timestamp(value: Any, field: str) -> None:
    raw=string(value,field,40)
    try: parsed=datetime.fromisoformat(raw[:-1]+"+00:00" if raw.endswith("Z") else raw)
    except ValueError as exc: raise ManifestValidationError(f"{field}: must be an ISO-8601 timestamp") from exc
    require(parsed.tzinfo is not None,f"{field}: timezone is required")

def unique_ids(items: list, field: str) -> set[str]:
    found=set()
    for i,item in enumerate(items):
        require(isinstance(item,dict),f"{field}[{i}]: must be an object")
        ident=string(item.get("id"),f"{field}[{i}].id",80)
        require(bool(SLUG.fullmatch(ident)),f"{field}[{i}].id: invalid identifier")
        require(ident not in found,f"{field}: duplicate id {ident}")
        found.add(ident)
    return found

def resolve_artifact(root: Path, relative: Any, ident: str) -> Path:
    raw=string(relative,f"artifact {ident}.path",500); candidate=Path(raw)
    require(not candidate.is_absolute(),f"artifact {ident}: absolute paths are forbidden")
    require(".." not in candidate.parts,f"artifact {ident}: parent traversal is forbidden")
    base=root.resolve(strict=True); current=base
    for part in candidate.parts:
        current=current/part
        require(not current.is_symlink(),f"artifact {ident}: symlink paths are forbidden")
    try:
        resolved=(base/candidate).resolve(strict=True); resolved.relative_to(base)
    except (OSError,ValueError) as exc:
        raise ManifestValidationError(f"artifact {ident}: path is missing or escapes the root") from exc
    require(resolved.is_file(),f"artifact {ident}: path must reference a regular file")
    return resolved

def validate_manifest(manifest: Any, root: str|Path) -> dict:
    require(isinstance(manifest,dict),"manifest: top-level value must be an object")
    require(manifest.get("schema_version")==SCHEMA_VERSION,"schema_version: unsupported version")
    case_id=string(manifest.get("case_id"),"case_id",80); product_id=string(manifest.get("product_id"),"product_id",80)
    require(bool(SLUG.fullmatch(case_id)),"case_id: invalid identifier"); require(bool(SLUG.fullmatch(product_id)),"product_id: invalid identifier")
    state=manifest.get("lifecycle_state"); require(isinstance(state,str) and state in STATES,"lifecycle_state: unsupported state")
    timestamp(manifest.get("created_at"),"created_at"); timestamp(manifest.get("updated_at"),"updated_at")
    artifacts=manifest.get("artifacts"); runs=manifest.get("validator_runs"); reviews=manifest.get("human_reviews"); history=manifest.get("state_history")
    for value,field in ((artifacts,"artifacts"),(runs,"validator_runs"),(reviews,"human_reviews"),(history,"state_history")):
        require(isinstance(value,list),f"{field}: must be an array")
    artifact_ids=unique_ids(artifacts,"artifacts")
    root_path=Path(root)
    try: root_path.resolve(strict=True)
    except OSError as exc: raise ManifestValidationError("root: directory does not exist") from exc
    require(root_path.is_dir(),"root: must be a directory")
    for item in artifacts:
        ident=item["id"]; kind=string(item.get("kind"),f"artifact {ident}.kind",80)
        require(bool(SLUG.fullmatch(kind)),f"artifact {ident}: invalid kind")
        expected=string(item.get("sha256"),f"artifact {ident}.sha256",64)
        require(bool(SHA256.fullmatch(expected)),f"artifact {ident}: invalid SHA-256")
        actual=hashlib.sha256(resolve_artifact(root_path,item.get("path"),ident).read_bytes()).hexdigest()
        require(actual==expected,f"artifact {ident}: SHA-256 mismatch")
    unique_ids(runs,"validator_runs")
    for i,run in enumerate(runs):
        string(run.get("validator"),f"validator_runs[{i}].validator",100)
        status=run.get("status"); require(isinstance(status,str) and status in VALIDATOR_STATUSES,f"validator_runs[{i}].status: unsupported status")
        timestamp(run.get("recorded_at"),f"validator_runs[{i}].recorded_at")
        refs=run.get("artifact_ids"); require(isinstance(refs,list),f"validator_runs[{i}].artifact_ids: must be an array")
        require(all(isinstance(ref,str) for ref in refs),f"validator_runs[{i}]: artifact references must be strings")
        require(len(refs)==len(set(refs)),f"validator_runs[{i}]: duplicate artifact reference")
        require(all(ref in artifact_ids for ref in refs),f"validator_runs[{i}]: references an unknown artifact")
    unique_ids(reviews,"human_reviews")
    for i,review in enumerate(reviews):
        string(review.get("stage"),f"human_reviews[{i}].stage",80); string(review.get("reviewer_label"),f"human_reviews[{i}].reviewer_label",120)
        decision=review.get("decision"); require(isinstance(decision,str) and decision in DECISIONS,f"human_reviews[{i}].decision: unsupported decision")
        timestamp(review.get("recorded_at"),f"human_reviews[{i}].recorded_at"); string(review.get("notes"),f"human_reviews[{i}].notes",2000)
    require(len(history)>=1,"state_history: at least the initial state is required")
    previous="INTAKE"
    for i,event in enumerate(history):
        require(isinstance(event,dict),f"state_history[{i}]: must be an object")
        timestamp(event.get("recorded_at"),f"state_history[{i}].recorded_at"); string(event.get("reason"),f"state_history[{i}].reason",500)
        source,target=event.get("from"),event.get("to")
        if i==0: require(source is None and target=="INTAKE","state_history[0]: must establish initial INTAKE state")
        else:
            require(source==previous,f"state_history[{i}]: from-state does not match previous state")
            allowed=target=="CLOSED" and source not in {"RELEASED","CLOSED"}
            require(allowed or (isinstance(source,str) and target==NEXT_STATE.get(source)),f"state_history[{i}]: transition is not allowed")
        require(isinstance(target,str) and target in STATES,f"state_history[{i}]: unsupported target state")
        previous=target
    require(previous==state,"lifecycle_state: does not match state_history")
    return {"status":"STRUCTURALLY_VALID_FOR_HUMAN_REVIEW","case_id":case_id,"product_id":product_id,"lifecycle_state":state,
      "checks":{"artifact_count":len(artifacts),"artifact_hashes":"verified","validator_run_count":len(runs),"human_review_record_count":len(reviews),"state_history":"valid","referential_integrity":"valid"},
      "limitations":["Human review records are unverified statements, not authenticated identity or approval.","A lifecycle state never grants permission to write, spend, provision, execute or deploy.","Validator records are historical claims; this tool does not rerun those validators.","Artifact hashes prove byte identity only, not factual accuracy, quality or safety."],
      "side_effects":False,"provider_calls":0,"spend_usd":0,"authorization_granted":False}

def reject_duplicate_keys(pairs: list[tuple[str,Any]]) -> dict:
    result={}
    for key,value in pairs:
        if key in result: raise ManifestValidationError(f"manifest: duplicate JSON key {key}")
        result[key]=value
    return result

def reject_constant(value: str):
    raise ManifestValidationError(f"manifest: invalid numeric constant {value}")

def read_manifest(path: str|Path) -> dict:
    try:
        with Path(path).open("r",encoding="utf-8") as handle:
            return json.load(handle,object_pairs_hook=reject_duplicate_keys,parse_constant=reject_constant)
    except ManifestValidationError: raise
    except (OSError,UnicodeError,json.JSONDecodeError) as exc:
        raise ManifestValidationError(f"manifest: cannot read valid UTF-8 JSON ({type(exc).__name__})") from exc

def main() -> int:
    parser=argparse.ArgumentParser(description="Validate a product lifecycle manifest without executing work.")
    parser.add_argument("--manifest",required=True); parser.add_argument("--root",required=True); parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    if not args.dry_run:
        print("BLOCKED: --dry-run is required; execution is not implemented.",file=sys.stderr); return 2
    try:
        print(json.dumps(validate_manifest(read_manifest(args.manifest),args.root),indent=2)); return 0
    except ManifestValidationError as exc:
        print(json.dumps({"status":"BLOCKED_LIFECYCLE_VALIDATION","reason":str(exc),"side_effects":False,"provider_calls":0,"spend_usd":0,"authorization_granted":False},indent=2)); return 4

if __name__=="__main__": raise SystemExit(main())
