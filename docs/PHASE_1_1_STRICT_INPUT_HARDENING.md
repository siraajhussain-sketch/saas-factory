# Phase 1.1 — Strict Input Hardening

**Status:** Implemented as a read-only validator hardening phase. No issuer or executor is included.

## Scope completed

- Reject duplicate JSON object keys at every file-input boundary.
- Reject non-standard JSON constants (NaN, Infinity and -Infinity).
- Require a JSON object at the document root.
- Require approval nonces to use exactly 64 lowercase hexadecimal characters.
- Reject non-NFC paths, control/format characters, backslashes, traversal, empty segments, platform stream markers, and path segments ending in dots or spaces.
- Retain resolved-path confinement checks so symlink targets outside the repository root are rejected.
- Add adversarial tests for parsing, path normalization, symlink escape and nonce format.

## What this does not solve

The validator cannot prove that a nonce was generated randomly or is unique. It has no durable ledger and cannot prevent a previously valid signed approval from being replayed. The nonce rule is a format constraint only.

The HMAC verifier remains a local prototype. It does not authenticate the named approver, protect a signing key from workflow compromise, or support independent revocation. There is no executor, repository writer, provider call, spend, environment or deployment capability.

## Verification

The standard-library test suite is run in CI. Passing tests establish only the tested local validation behavior; they do not make this an approval service or production security boundary.
