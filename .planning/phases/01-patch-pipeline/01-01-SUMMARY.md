---
phase: 01-patch-pipeline
plan: 01
subsystem: infra
tags: [github-actions, binary-patch, arm64, dpkg-deb, ci-cd]

# Dependency graph
requires:
  - phase: none
    provides: first phase, no dependencies
provides:
  - Patch step in _build_tweaks.yml that downloads, verifies, patches, and repackages YTLite dylib
  - SHA256 integrity verification of upstream v5.2 .deb
  - Before/after hex dump audit logging of patch site
  - Post-patch byte verification ensuring dvnLocked returns 0
affects: [02-verification]

# Tech tracking
tech-stack:
  added: []
  patterns: [printf+dd binary patch, dpkg-deb extract/repack, shasum SHA256 verification, xxd hex dump logging]

key-files:
  created: []
  modified: [.github/workflows/_build_tweaks.yml]

key-decisions:
  - "Used printf piped to dd for 8-byte binary write at offset 0x1eb64 -- most readable and consistent with existing workflow shell style"
  - "Guard condition uses inputs.tweak_version OR inputs.tweak_url to match both download paths"
  - "SHA256 check is unconditional -- future versions are out of scope per REQUIREMENTS.md"

patterns-established:
  - "Binary patch via printf+dd with conv=notrunc for in-place writes"
  - "Pre/post verification pattern: SHA256 before extraction, byte check after patching"

requirements-completed: [PATCH-01, PATCH-02, CICD-01, CICD-02]

# Metrics
duration: 2min
completed: 2026-04-21
---

# Phase 1 Plan 1: Insert Patch Step Summary

**Binary patch step in _build_tweaks.yml that SHA256-verifies upstream v5.2 .deb, extracts dylib, patches dvnLocked at 0x1eb64 to return 0, verifies patched bytes, and repackages .deb in-place for transparent downstream consumption**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-21T03:35:12Z
- **Completed:** 2026-04-21T03:37:03Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Inserted "Patch YTLite dylib (bypass dvnLocked)" step into _build_tweaks.yml between download steps and Clone YouTubeHeader
- Implemented all 7 locked decisions (D-01 through D-07) in a single workflow step
- Validated YAML syntax, step ordering (28 steps total), guard condition alignment, and main.yml integration integrity

## Task Commits

Each task was committed atomically:

1. **Task 1: Insert the Patch YTLite dylib step into _build_tweaks.yml** - `973913f` (feat)
2. **Task 2: Validate workflow YAML syntax and integration correctness** - validation-only, no file changes

**Plan metadata:** (pending -- docs commit)

## Files Created/Modified
- `.github/workflows/_build_tweaks.yml` - Added 52-line patch step implementing SHA256 verification, .deb extraction, binary patch via printf+dd, before/after hex dump logging, post-patch byte verification, and .deb repackaging

## Decisions Made
- Used `printf` piped to `dd` for the 8-byte binary write -- most readable and consistent with existing workflow shell style (per D-02)
- Guard condition `inputs.tweak_version != '' || inputs.tweak_url != ''` covers both download paths so patch only runs when a .deb exists
- SHA256 check is unconditional per D-07; future versions are out of scope per REQUIREMENTS.md

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- PyYAML parses YAML `on:` key as boolean `True` (known PyYAML quirk). Adjusted verification script to use `True` as dict key for main.yml parsing. Not a code issue -- only affected the validation script.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- _build_tweaks.yml is ready for workflow dispatch with `tweak_version: "5.2"`
- main.yml requires no changes -- patched ytplus.deb is consumed transparently by the package job
- Phase 2 (Verification) can proceed to confirm the patched IPA works on a device

---
*Phase: 01-patch-pipeline*
*Completed: 2026-04-21*
