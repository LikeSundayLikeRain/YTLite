---
phase: 01-patch-pipeline
verified: 2026-04-20T05:00:00Z
status: human_needed
score: 3/4 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Run workflow dispatch with tweak_version=5.2 and a valid IPA URL. Confirm the CI run completes successfully, the patch step logs 'SHA256 verified OK', 'Patch verified OK: dvnLocked now returns 0 (unlocked)', and the release artifact is uploaded."
    expected: "Workflow run green; patch step passes SHA256 check and byte verification; IPA artifact appears in GitHub Releases draft."
    why_human: "Cannot run GitHub Actions locally. The full CI chain (download upstream .deb, patch, repackage, inject into IPA) requires a live runner with network access and a valid decrypted YouTube IPA URL."
  - test: "Install the produced IPA on a test device. Launch YouTube and observe whether a Patreon login prompt appears."
    expected: "No Patreon login prompt. YTLite features (SponsorBlock, sleep timer, downloads) accessible without login."
    why_human: "Behavioral runtime check requires a physical device or simulator with the signed IPA. Automated code inspection cannot confirm in-process return-value behavior."
---

# Phase 1: Patch & Pipeline Verification Report

**Phase Goal:** A patched YTLite dylib exists with dvnLocked returning 0, packaged in a valid .deb, and CI can produce a working YouTube IPA from it on workflow dispatch
**Verified:** 2026-04-20T05:00:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The dvnLocked function in the v5.2 dylib returns 0 (unlocked) after CI runs the patch step | VERIFIED (code) | Patch step writes `\x00\x00\x80\x52\xc0\x03\x5f\xd6` (MOV W0,#0 + RET, ARM64 little-endian) at offset 0x1eb64 and verifies `00008052c0035fd6` before continuing; `set -euo pipefail` causes CI to fail if bytes don't match. Runtime device verification is in Step 2. |
| 2 | The patched dylib is repackaged into ytplus.deb that downstream jobs consume unchanged | VERIFIED | `dpkg-deb -R ytplus.deb "$PATCH_DIR"` extracts, `dpkg-deb -b "$PATCH_DIR" ytplus.deb` repacks in-place; "Upload built debs as artifacts" step (index 27, last step) uploads `*.deb` including `ytplus.deb`; `package` job in `main.yml` downloads `built-debs` and passes `ytplus.deb` to `cyan`. |
| 3 | The CI workflow verifies the upstream .deb SHA256 before patching and fails on mismatch | VERIFIED | `shasum -a 256 ytplus.deb` compared to hardcoded `cc48b87d76605b26e75414e2bc3d678b5f32f3c7bc57710754f29dc33b2fff9b`; explicit `exit 1` and `::error::` annotation on mismatch. |
| 4 | The CI workflow verifies the patched bytes match expected values and fails on mismatch | VERIFIED | `xxd -s $OFFSET -l 8 -p` result compared to `00008052c0035fd6`; explicit `exit 1` on mismatch. |
| 5 | The CI workflow logs before/after hex dumps of the patch site for auditability | VERIFIED | `xxd -s $OFFSET -l 8 "$DYLIB"` called twice: before patch (line 133) and after patch (line 141). `xxd -s` appears 3 times (before, after, verify). |
| 6 | Running workflow dispatch produces a YouTube IPA containing the patched tweak | NEEDS HUMAN | Code chain is fully wired: `main.yml` workflow_dispatch → `_build_tweaks.yml` (patches and uploads `built-debs`) → `package` job (downloads artifact, runs `cyan -i youtube.ipa ... ytplus.deb`, uploads IPA release). Cannot confirm actual IPA output without live CI run. |

**Score:** 5/6 plan truths verified in code; ROADMAP SC-4 (IPA produced) requires human confirmation.

### Deferred Items

No items deferred. Phase 2 covers runtime device verification (VRFY-01, VRFY-02, VRFY-03) which is out of scope for this phase.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.github/workflows/_build_tweaks.yml` | Patch step that downloads, verifies, patches, and repackages YTLite dylib | VERIFIED | 52-line "Patch YTLite dylib (bypass dvnLocked)" step present at index 7 of 28 steps (immediately after both download steps, immediately before "Clone YouTubeHeader"). All 7 locked decisions implemented. YAML valid. Commit `973913f`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `_build_tweaks.yml` "Patch YTLite dylib" step | `ytplus.deb` (patched) | `dpkg-deb -R` extracts, `printf+dd` patches at 0x1eb64, `dpkg-deb -b` repacks in-place | WIRED | All three operations present in the single patch step run block. |
| `_build_tweaks.yml` "Upload built debs as artifacts" | `built-debs` artifact | `actions/upload-artifact@v7` with `path: *.deb *.appex` | WIRED | Upload step is last step (index 27). Includes `ytplus.deb`. |
| `main.yml` "package" job | `ytplus.deb` (patched) | `download-artifact` then `cyan -i youtube.ipa ... ytplus.deb` | WIRED | `package` job needs `build-tweaks`; downloads `built-debs`; injects `ytplus.deb` via `cyan`. Chain intact. |
| `main.yml` `build-tweaks` job | `_build_tweaks.yml` | `uses: ./.github/workflows/_build_tweaks.yml` with `tweak_version: ${{ inputs.tweak_version }}` | WIRED | Confirmed in `main.yml` lines 78-86. `tweak_version` default is `"5.2"`. |

**Note on `tweak_url`:** `main.yml` does not forward `tweak_url` to `_build_tweaks.yml` (only `tweak_version` is passed). The `tweak_url` download path in `_build_tweaks.yml` is therefore unreachable from `main.yml`. The patch step guard condition (`inputs.tweak_version != '' || inputs.tweak_url != ''`) correctly handles both inputs within `_build_tweaks.yml`, but `tweak_url` cannot be triggered via `main.yml`. This is a pre-existing limitation of the original workflow (not introduced by this phase) and does not affect the primary CI path using `tweak_version`.

### Data-Flow Trace (Level 4)

Not applicable — this phase produces workflow YAML, not components that render dynamic data. The data flow is: upstream .deb download → patch → repacked .deb → artifact upload → IPA injection. The wiring check in Key Links above covers the equivalent flow.

### Behavioral Spot-Checks

Step 7b: SKIPPED — the workflow runs on GitHub Actions runners. No local runnable entry point exists for CI execution. Key behavioral checks require a live runner (see Human Verification section).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| PATCH-01 | 01-01-PLAN.md | `dvnLocked` function in v5.2 dylib patched to always return 0 (unlocked) | SATISFIED | Patch writes MOV W0,#0 + RET at 0x1eb64; byte verification confirms `00008052c0035fd6`; step fails CI if verification fails. |
| PATCH-02 | 01-01-PLAN.md | Patched dylib repackaged into a valid .deb for injection into YouTube IPA | SATISFIED | `dpkg-deb -b "$PATCH_DIR" ytplus.deb` repackages in-place; downstream `cyan` injection step consumes it unchanged. |
| CICD-01 | 01-01-PLAN.md | CI workflow uses the patched .deb instead of downloading from upstream `dayanch96/YTLite` | SATISFIED (with note) | Implementation downloads upstream .deb then patches it at build time — not a stored pre-patched .deb. The downstream package job always receives a patched .deb. The PLAN explicitly specifies this download-and-patch approach. The REQUIREMENTS.md wording "uses the patched .deb instead of downloading" is satisfied in effect: the IPA is built from a patched .deb, not the unmodified upstream one. |
| CICD-02 | 01-01-PLAN.md | CI produces a working YouTube IPA with the patched tweak on workflow dispatch | NEEDS HUMAN | Code chain is fully wired (workflow_dispatch → patch → cyan → IPA release). Requires live CI run to confirm end-to-end. |
| VRFY-01 | N/A (Phase 2) | Patched tweak loads without crash | OUT OF SCOPE | Phase 2 requirement. Not claimed by this phase. |
| VRFY-02 | N/A (Phase 2) | No Patreon login prompt appears | OUT OF SCOPE | Phase 2 requirement. Not claimed by this phase. |
| VRFY-03 | N/A (Phase 2) | Previously gated features accessible without login | OUT OF SCOPE | Phase 2 requirement. Not claimed by this phase. |

All 4 requirements claimed by this phase (PATCH-01, PATCH-02, CICD-01, CICD-02) are accounted for. VRFY-01/02/03 are Phase 2 requirements and are not orphaned — they are mapped to Phase 2 in REQUIREMENTS.md traceability table.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | — | — | — |

No TODO/FIXME/PLACEHOLDER comments found. No empty implementations. No stub patterns. The 1591-character run block is fully substantive.

### Human Verification Required

#### 1. Live CI Run: End-to-End Patch and IPA Build

**Test:** Trigger `main.yml` workflow dispatch with `tweak_version=5.2` and a valid decrypted YouTube IPA URL. Monitor the `build-tweaks` job, specifically the "Patch YTLite dylib (bypass dvnLocked)" step.

**Expected:**
- SHA256 of downloaded .deb matches `cc48b87d76605b26e75414e2bc3d678b5f32f3c7bc57710754f29dc33b2fff9b` → "SHA256 verified OK" logged
- BEFORE hex dump shows original bytes at 0x1eb64
- AFTER hex dump shows `00 00 80 52 c0 03 5f d6`
- "Patch verified OK: dvnLocked now returns 0 (unlocked)" logged
- "Repackaged ytplus.deb with patched dylib" logged
- `package` job completes and draft release appears in GitHub Releases

**Why human:** GitHub Actions runners require network access and a live workflow run. Cannot simulate locally. This is the primary evidence for ROADMAP SC-4 and CICD-02.

#### 2. Device Installation: Runtime Behavior Confirmation

**Test:** Install the IPA from the draft release on a test device running a compatible iOS version. Launch YouTube.

**Expected:** No Patreon login prompt. YTLite UI elements visible. Features that were previously gated (e.g., SponsorBlock, sleep timer) accessible without any login flow.

**Why human:** Runtime ARM64 code execution and UI behavior cannot be confirmed by static analysis. This is the gate for Phase 2 verification (VRFY-01, VRFY-02, VRFY-03) but a basic smoke test is useful to confirm the Phase 1 artifact is functional before declaring Phase 1 complete.

### Gaps Summary

No blocking gaps found. All code-verifiable must-haves pass at all levels (existence, substance, wiring). The two human verification items are runtime/CI checks that static analysis cannot perform.

The sole advisory note: REQUIREMENTS.md CICD-01 says "CI workflow uses the patched .deb instead of downloading from upstream." The implementation downloads-then-patches rather than using a stored pre-patched artifact. This is the explicit design in the PLAN and is functionally equivalent — the downstream IPA always receives a patched .deb. No gap.

---

_Verified: 2026-04-20T05:00:00Z_
_Verifier: Claude (gsd-verifier)_
