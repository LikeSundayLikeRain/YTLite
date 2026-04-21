# Phase 1: Patch & Pipeline - Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Binary-patch the `dvnLocked` function in the pre-compiled YTLite v5.2 dylib to always return 0 (unlocked), repackage it into a valid `.deb`, and update the CI pipeline to produce a working YouTube IPA from the patched tweak on workflow dispatch. No source code changes, no new features, no Patreon code removal beyond the 4-byte bypass.

</domain>

<decisions>
## Implementation Decisions

### Patch Delivery Method
- **D-01:** A shell script in CI downloads the upstream v5.2 `.deb`, extracts `YTLite.dylib`, patches 4 bytes at offset `0x1eb64` to make `dvnLocked` return 0, and repackages into a new `.deb`. No pre-patched binaries committed to the repo.
- **D-02:** The patch uses `printf` or `dd` to write the ARM64 instruction bytes for `MOV W0, #0; RET` at the target offset. Keeps the patch minimal, auditable, and reproducible.

### CI Modification Scope
- **D-03:** Add the patch step to the existing `_build_tweaks.yml` workflow — insert it after the "Download YouTube Plus" step and before the artifact upload. No new workflow files.
- **D-04:** The existing `tweak_version` input defaults to `"5.2"` and continues to work as-is. The download URL still points to `dayanch96/YTLite/releases` but the binary is patched before being uploaded as an artifact.

### Patch Verification
- **D-05:** After patching, read the bytes at offset `0x1eb64` and assert they match the expected patched instruction. Fail the CI build if the byte check fails.
- **D-06:** Log the before/after bytes (hex dump of the 8 bytes around the patch site) for auditability in CI logs.

### Upstream Version Pinning
- **D-07:** Verify the downloaded `.deb` against a known SHA256 checksum before patching. Hard-code the expected hash for the v5.2 release. Fail if the hash doesn't match — ensures we never patch an unexpected binary.

### Claude's Discretion
- Exact ARM64 instruction encoding for the patch (MOV W0, #0 + RET vs. alternatives that achieve the same result)
- Whether to use `dd`, `printf`, or a Python one-liner for the byte write
- Temp directory structure during extract/repack
- Exact hex dump format for the CI log output

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### CI Pipeline
- `.github/workflows/_build_tweaks.yml` — Reusable build workflow; lines 89-93 download the upstream .deb by version; patch step inserts after this
- `.github/workflows/main.yml` — Main IPA builder; calls `_build_tweaks.yml`; line 121 injects `ytplus.deb` into IPA via cyan

### Binary Target
- `.planning/PROJECT.md` §Context — Documents `dvnLocked` at offset `0x1eb64` (4 instructions), `dvnCheck` at `0x1eb78`, and the subscription byte mechanism
- `.planning/REQUIREMENTS.md` §Binary Patch — PATCH-01 (patch dvnLocked), PATCH-02 (repackage .deb)
- `.planning/REQUIREMENTS.md` §CI/CD — CICD-01 (use patched .deb), CICD-02 (produce working IPA)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_build_tweaks.yml` download steps: Already download `.deb` by version or URL and save as `ytplus.deb` — patch step slots in after
- `main.yml` inject step: Already handles `ytplus.deb` injection via `cyan` — no changes needed downstream

### Established Patterns
- CI uses `wget` for downloads, `file --mime-type` for validation (see `main.yml` line 110-113)
- Homebrew for tool installation (`brew install make ldid dpkg`) — `dpkg-deb` is available for .deb extract/repack
- Artifacts passed between jobs via `actions/upload-artifact` / `actions/download-artifact`

### Integration Points
- Patch step inserts between "Download YouTube Plus (by version)" and "Upload built debs as artifacts" in `_build_tweaks.yml`
- No changes needed to `main.yml` or the `package` job — they already consume `ytplus.deb` as-is

</code_context>

<specifics>
## Specific Ideas

- The patch is exactly 4 bytes at a known offset — this is a surgical binary edit, not a general-purpose patching framework
- `dvnLocked` reads a subscription byte and returns 1 (locked) or 0 (unlocked) — patching it to always return 0 bypasses the gate entirely
- `dvnCheck` at `0x1eb78` may not need patching if `dvnLocked` bypass is sufficient (per PROJECT.md Out of Scope)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-patch-pipeline*
*Context gathered: 2026-04-20*
