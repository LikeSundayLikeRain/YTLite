# Phase 2: Verification - Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Confirm the patched YTLite IPA works end-to-end: the tweak loads without crash, no Patreon login prompt appears, and previously gated features (SponsorBlock, sleep timer, downloads) are accessible without login. This phase produces a verification report — it does not modify code or CI.

</domain>

<decisions>
## Implementation Decisions

### Verification Environment
- **D-01:** Manual device testing via sideloading. The patched IPA must be installed on a real iOS device (or simulator if dylib injection is supported) and exercised by a human tester.
- **D-02:** Use a sideloading tool (AltStore, Sideloadly, or TrollStore depending on device/iOS version) to install the CI-produced IPA. The specific tool is Claude's discretion based on what's available.

### Feature Test Scope
- **D-03:** Explicitly verify the three features named in VRFY-03: SponsorBlock, sleep timer, and downloads. These are the known gated features that must work without Patreon login.
- **D-04:** Spot-check additional gated features beyond the three named ones — premium logo removal, ad blocking, background playback, video quality auto-selection — to confirm the dvnLocked bypass is comprehensive.
- **D-05:** Verify VRFY-01 (no crash on load) and VRFY-02 (no Patreon prompt) as preconditions before feature testing.

### Verification Evidence
- **D-06:** Produce a structured verification report (markdown) with a pass/fail checklist per feature, organized by requirement (VRFY-01, VRFY-02, VRFY-03).
- **D-07:** Screenshots or screen recordings for key moments: app launch (no gate), settings panel (features visible), and each gated feature in use. Screenshots stored as references in the report.

### dvnCheck Secondary Gate
- **D-08:** Do NOT patch dvnCheck at 0x1eb78 preemptively. Test with only dvnLocked patched first.
- **D-09:** If any feature still shows a Patreon gate or subscription prompt during testing, investigate dvnCheck as a secondary bypass target. This would trigger a follow-up patch in Phase 1's CI step (or a new plan in Phase 2).

### Claude's Discretion
- Exact sideloading tool choice and setup instructions
- Test report template structure and formatting
- Order of feature verification
- Whether to include a static analysis step (e.g., disassemble the patched dylib to confirm dvnLocked returns 0) as a complement to runtime testing

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §Verification — VRFY-01 (no crash), VRFY-02 (no Patreon prompt), VRFY-03 (gated features accessible)

### Binary Patch Details
- `.planning/PROJECT.md` §Context — dvnLocked at offset 0x1eb64, dvnCheck at 0x1eb78, subscription byte mechanism
- `.planning/phases/01-patch-pipeline/01-CONTEXT.md` §Patch Delivery Method — D-01/D-02 describe the exact patch applied (MOV W0, #0 + RET at 0x1eb64)

### CI Pipeline (produces the artifact under test)
- `.github/workflows/_build_tweaks.yml` lines 105-155 — Patch step: SHA256 verify, extract, patch, verify bytes, repackage
- `.github/workflows/main.yml` — Main IPA builder that consumes patched ytplus.deb

### Feature Reference
- `Settings.x` — Settings panel where gated features are toggled; useful for identifying which features to verify
- `YTLite.x` — Main hook logic; feature gates use `ytlBool(@"key")` pattern

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_build_tweaks.yml` patch step: Already produces the patched IPA artifact — verification consumes this output
- `Settings.x` settings panel: Lists all feature toggles — serves as a checklist of features to verify
- `YTLUserDefaults.m` registerDefaults: Shows which features default to on/off — helps identify expected behavior

### Established Patterns
- Feature gating: All features use `ytlBool(@"key")` — if dvnLocked returns 0, all `dvnLocked`-gated features should unlock uniformly
- CI artifact flow: `_build_tweaks.yml` → upload artifact → `main.yml` downloads and injects into IPA via cyan

### Integration Points
- CI workflow dispatch → IPA artifact download → sideload to device → manual testing
- If dvnCheck needs patching: loops back to `_build_tweaks.yml` patch step (Phase 1 scope)

</code_context>

<specifics>
## Specific Ideas

- The blocker "No iOS device/sideloading setup confirmed yet" (from STATE.md) must be resolved before testing can begin — the plan should address this as a prerequisite step
- Consider a static verification step first: disassemble the patched dylib (e.g., `objdump` or `otool -tv`) to confirm dvnLocked returns 0 before device testing — this can run in CI without a device
- The verification report should be structured so it can serve as release notes evidence if the fork is distributed

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-verification*
*Context gathered: 2026-04-20*
