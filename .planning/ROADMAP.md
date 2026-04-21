# Roadmap: YTLite Free Fork

## Overview

Remove the Patreon subscription gate from YTLite v5.2 by binary-patching `dvnLocked` in the pre-compiled dylib, updating the CI pipeline to use the patched binary, and verifying that all previously gated features work without login. Two phases: produce the patched artifact with automated builds, then verify it works end-to-end.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Patch & Pipeline** - Binary-patch dvnLocked, repackage the .deb, and update CI to produce a working IPA from the patched tweak
- [x] **Phase 2: Verification** - Confirm the patched tweak loads, shows no Patreon gate, and unlocks all previously gated features

## Phase Details

### Phase 1: Patch & Pipeline
**Goal**: A patched YTLite dylib exists with dvnLocked returning 0, packaged in a valid .deb, and CI can produce a working YouTube IPA from it on workflow dispatch
**Depends on**: Nothing (first phase)
**Requirements**: PATCH-01, PATCH-02, CICD-01, CICD-02
**Success Criteria** (what must be TRUE):
  1. The `dvnLocked` function in the v5.2 dylib returns 0 (unlocked) instead of 1 at offset 0x1eb64
  2. The patched dylib is repackaged into a valid .deb that can be extracted and injected into a YouTube IPA
  3. The CI workflow no longer downloads from upstream `dayanch96/YTLite` releases -- it uses the patched .deb
  4. Running the CI workflow dispatch produces a YouTube IPA artifact containing the patched tweak
**Plans:** 1 plan

Plans:
- [x] 01-01-PLAN.md — Insert patch step into _build_tweaks.yml (SHA256 verify, extract, patch dvnLocked, verify bytes, repackage .deb)

### Phase 2: Verification
**Goal**: Users can install the patched IPA and use all YTLite features -- including previously gated ones -- without any Patreon login or subscription prompt
**Depends on**: Phase 1
**Requirements**: VRFY-01, VRFY-02, VRFY-03
**Success Criteria** (what must be TRUE):
  1. The patched tweak loads without crash when injected into the YouTube app
  2. No Patreon login prompt or subscription gate appears on launch or during use
  3. Previously gated features (SponsorBlock, sleep timer, downloads) are accessible and functional without login
**Plans:** 2 plans

Plans:
- [x] 02-01-PLAN.md — Static patch verification (capstone disassembly, byte check, otool cross-reference) and CI workflow trigger
- [x] 02-02-PLAN.md — Device testing (sideload IPA, verify all features, produce verification report with evidence)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Patch & Pipeline | 1/1 | Complete | 2026-04-21 |
| 2. Verification | 2/2 | Complete | 2026-04-21 |
