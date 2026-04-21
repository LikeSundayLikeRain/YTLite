# Phase 1: Patch & Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-20
**Phase:** 01-patch-pipeline
**Areas discussed:** Patch delivery method, CI modification scope, Patch verification, Upstream version pinning
**Mode:** --auto (all decisions auto-selected)

---

## Patch Delivery Method

| Option | Description | Selected |
|--------|-------------|----------|
| Patch script in CI | Shell script downloads .deb, extracts dylib, patches bytes, repackages. No pre-patched binaries in repo. | ✓ |
| Commit pre-patched .deb | Store the already-patched .deb in the repo. Simpler CI but bloats repo with binary. | |
| Separate patch tool | Standalone script users run locally; CI calls the same script. More flexible but over-engineered for 4 bytes. | |

**User's choice:** Patch script in CI (auto-selected, recommended default)
**Notes:** Keeps the repo clean, makes the patch reproducible and auditable in CI logs. No binary blobs in version control.

---

## CI Modification Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Add step to existing _build_tweaks.yml | Minimal change — insert patch step after download, before artifact upload. | ✓ |
| New dedicated workflow | Separate workflow for patching. Cleaner separation but unnecessary complexity for a single step. | |
| Fork entire CI | Rewrite CI from scratch. Maximum control but high effort for no benefit. | |

**User's choice:** Add step to existing _build_tweaks.yml (auto-selected, recommended default)
**Notes:** Preserves existing CI structure. The download step already saves as `ytplus.deb`; patch step modifies it in-place before upload.

---

## Patch Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Byte check at offset | Read bytes at 0x1eb64 after patching, assert they match expected instruction. | ✓ |
| Disassemble and check | Use objdump/otool to disassemble and verify the function. More thorough but heavier dependency. | |
| No verification | Trust the patch worked. Fast but risky. | |

**User's choice:** Byte check at offset (auto-selected, recommended default)
**Notes:** Simple hex comparison is sufficient for a 4-byte patch. Log before/after bytes for auditability.

---

## Upstream Version Pinning

| Option | Description | Selected |
|--------|-------------|----------|
| SHA256 checksum | Verify downloaded .deb against hard-coded hash. Fail if mismatch. | ✓ |
| File size check | Verify file size only. Weaker guarantee. | |
| No pinning | Download whatever is at the URL. Risk of patching wrong binary. | |

**User's choice:** SHA256 checksum (auto-selected, recommended default)
**Notes:** Hard-code expected SHA256 for v5.2 .deb. Ensures we never accidentally patch an unexpected binary.

---

## Claude's Discretion

- Exact ARM64 instruction encoding for MOV W0, #0 + RET
- Choice of byte-writing tool (dd, printf, or Python)
- Temp directory structure during extract/repack
- Hex dump format for CI log output

## Deferred Ideas

None — discussion stayed within phase scope
