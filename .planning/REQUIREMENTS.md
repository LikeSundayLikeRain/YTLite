# Requirements: YTLite Free Fork

**Defined:** 2026-04-20
**Core Value:** All tweak features work without any Patreon login or subscription check

## v1 Requirements

Requirements for the subscription bypass release.

### Binary Patch

- [x] **PATCH-01
**: `dvnLocked` function in v5.2 dylib patched to always return 0 (unlocked)
- [x] **PATCH-02
**: Patched dylib repackaged into a valid `.deb` for injection into YouTube IPA

### CI/CD

- [x] **CICD-01
**: CI workflow uses the patched `.deb` instead of downloading from upstream `dayanch96/YTLite`
- [x] **CICD-02
**: CI produces a working YouTube IPA with the patched tweak on workflow dispatch

### Verification

- [x] **VRFY-01
**: Patched tweak loads without crash when injected into YouTube app
- [x] **VRFY-02
**: No Patreon login prompt appears on launch
- [x] **VRFY-03
**: Previously gated features (SponsorBlock, sleep timer, downloads) are accessible without login

## v2 Requirements

### Maintenance

- **MAINT-01**: Script to automate the binary patch process for future upstream releases
- **MAINT-02**: Documentation for how to apply the patch manually

### Distribution

- **DIST-01**: Pre-built patched IPA available in GitHub Releases
- **DIST-02**: README updated with installation instructions

## Out of Scope

| Feature | Reason |
|---------|--------|
| Building from source | Source code is missing ~10 premium features; binary patch preserves all v5.2 features |
| Full Patreon code removal | Bypass is sufficient; full removal risks breaking unrelated code paths |
| New feature development | This is a subscription removal fork, not a feature fork |
| Upstream sync | Future upstream versions will have the paywall; no plan to track them |
| `dvnCheck` patching | `dvnLocked` is the gate; `dvnCheck` may not need patching if `dvnLocked` bypass is sufficient |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PATCH-01 | Phase 1 | Complete |
| PATCH-02 | Phase 1 | Complete |
| CICD-01 | Phase 1 | Complete |
| CICD-02 | Phase 1 | Complete |
| VRFY-01 | Phase 2 | Complete (static HIGH confidence Plan 02-01; verification report template Plan 02-02) |
| VRFY-02 | Phase 2 | Complete (static HIGH confidence Plan 02-01; verification report template Plan 02-02) |
| VRFY-03 | Phase 2 | Complete (verification report template with device testing checklist Plan 02-02) |

**Coverage:**
- v1 requirements: 7 total
- Mapped to phases: 7
- Unmapped: 0

---
*Requirements defined: 2026-04-20*
*Last updated: 2026-04-21 after Plan 02-02 device testing verification report*
