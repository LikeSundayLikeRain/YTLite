# Verification Report: YTLite v5.2 Patched Fork

**Date:** 2026-04-20
**Tester:** [Name]
**Device:** [Model, iOS version]
**Sideloading Tool:** [AltStore / Sideloadly / TrollStore]
**IPA Source:** [GitHub Release URL or local path]

---

## Static Analysis (Automated -- from Plan 01)

**Date:** 2026-04-20
**Dylib:** YTLite.dylib from com.dvntm.ytlite_5.2_iphoneos-arm.deb
**SHA256 of upstream .deb:** cc48b87d76605b26e75414e2bc3d678b5f32f3c7bc57710754f29dc33b2fff9b

### SHA256 Integrity Check
- **Status:** PASS
- **Expected:** cc48b87d76605b26e75414e2bc3d678b5f32f3c7bc57710754f29dc33b2fff9b
- **Actual:** cc48b87d76605b26e75414e2bc3d678b5f32f3c7bc57710754f29dc33b2fff9b

### Byte Verification at 0x1eb64
- **Status:** PASS
- **Original bytes:** a889009008855339
- **Patched bytes:** 00008052c0035fd6
- **Expected patched:** 00008052c0035fd6

### Disassembly: dvnLocked (0x1eb64)
- **Status:** PASS

| Address | Instruction |
|---------|------------|
| 0x1eb64 | mov w0, #0 |
| 0x1eb68 | ret |

- **Original disassembly (before patch):**

| Address | Instruction |
|---------|------------|
| 0x1eb64 | adrp x8, #0x1152000 |
| 0x1eb68 | ldrb w8, [x8, #0x4e1] |

- **Semantic check:** Function returns 0 (unlocked) via MOV W0, #0 + RET

### Disassembly: dvnCheck (0x1eb78) -- Reference Only

| Address | Instruction |
|---------|------------|
| 0x1eb78 | stp x20, x19, [sp, #-0x20]! |
| 0x1eb7c | stp x29, x30, [sp, #0x10] |
| 0x1eb80 | add x29, sp, #0x10 |
| 0x1eb84 | bl #0x2cc54 |
| 0x1eb88 | mov x29, x29 |
| 0x1eb8c | bl #0xb96608 |
| 0x1eb90 | cmp x0, #0 |
| 0x1eb94 | cset w19, ne |

- **Note:** Per D-08, dvnCheck is NOT patched. Recorded for reference if D-09 triggers.
- **Analysis:** dvnCheck saves registers, calls an auth function (bl #0x2cc54), retains the return value via objc_retainAutoreleasedReturnValue, then compares the result to zero and sets w19 to 1 if non-null (i.e., authenticated). This function checks Patreon authentication status but is not the gate itself -- dvnLocked is the gate.

### otool Cross-Reference

```
_dvnLocked:
000000000001eb64	mov	w0, #0x0
000000000001eb68	ret
000000000001eb6c	mov	w9, #0x1
000000000001eb70	bic	w0, w9, w8
000000000001eb74	ret
_dvnCheck:
000000000001eb78	stp	x20, x19, [sp, #-0x20]!
000000000001eb7c	stp	x29, x30, [sp, #0x10]
000000000001eb80	add	x29, sp, #0x10
000000000001eb84	bl	0x2cc54
000000000001eb88	mov	x29, x29
000000000001eb8c	bl	0xb96608 ; symbol stub for: _objc_retainAutoreleasedReturnValue
000000000001eb90	cmp	x0, #0x0
000000000001eb94	cset	w19, ne
000000000001eb98	bl	0xb965d8 ; symbol stub for: _objc_release
000000000001eb9c	mov	x0, x19
```

otool confirms:
- `_dvnLocked` label at 0x1eb64 contains `mov w0, #0x0` followed by `ret` -- matches capstone disassembly
- The dead code at 0x1eb6c-0x1eb74 (original conditional logic) is unreachable after the patch
- `_dvnCheck` label at 0x1eb78 matches our capstone disassembly -- calls auth, checks result

### VRFY-01 Static Confidence
- Patch applies valid ARM64 instructions (no illegal opcodes): PASS
- Function body is self-contained (MOV + RET, no branch): PASS
- **Conclusion:** HIGH confidence that patched tweak will load without crash

### VRFY-02 Static Confidence
- dvnLocked unconditionally returns 0: PASS
- **Conclusion:** HIGH confidence that no Patreon prompt will appear

### CI Artifact Status

- **Workflow runs:** None found
- **IPA artifact:** Not yet produced
- **Blocker:** The `main.yml` workflow requires a `ipa_url` input (URL to a decrypted YouTube IPA). This must be provided by the user to trigger the build.
- **Next step:** User must trigger workflow dispatch via GitHub Actions UI or CLI:
  ```bash
  gh workflow run main.yml -f ipa_url="<DECRYPTED_IPA_URL>" -f tweak_version="5.2"
  ```
- **After CI completes:** Download the IPA from the draft GitHub Release for sideloading in Plan 02.

---

## Prerequisites

Before beginning device testing, confirm all of the following:

- [ ] **CI workflow triggered and IPA available:** Run `gh workflow run main.yml -f ipa_url="<DECRYPTED_IPA_URL>" -f tweak_version="5.2"` and wait for completion (~5-10 min). Verify a draft GitHub Release contains the IPA.
- [ ] **IPA downloaded:** Download `YouTubePlus_{version}.ipa` from the draft GitHub Release to your local machine.
- [ ] **Sideloading tool installed:** AltStore, Sideloadly, or TrollStore is installed and working on your Mac and/or device (see D-02).
- [ ] **IPA installed on device:** The YouTubePlus IPA is sideloaded onto your iOS device and the app icon appears on the home screen.
- [ ] **Advanced Mode enabled:** Settings > YTLite > General > Advanced Mode toggle ON (required for SponsorBlock, sleep timer, and other advanced features per Pitfall 3). Without this, settings categories Overlay, Player, Shorts, Other, and SponsorBlock will be hidden.

---

## VRFY-01: Patched Tweak Loads Without Crash

**Precondition:** This must PASS before proceeding to VRFY-02 and VRFY-03 (per D-05).

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | App launches to home screen (YouTube feed visible) | [ ] PASS / [ ] FAIL | |
| 2 | YTLite section visible in Settings (Settings > YTLite) | [ ] PASS / [ ] FAIL | |
| 3 | No crash within 60 seconds of normal use (scroll feed, tap video) | [ ] PASS / [ ] FAIL | |
| 4 | App survives backgrounding and foregrounding (press Home, reopen) | [ ] PASS / [ ] FAIL | |

**Screenshot:** Save as `evidence/screenshots/vrfy01-launch.png` (home screen with YTLite loaded)

**Static Analysis Verdict:** PASS (HIGH confidence -- valid ARM64 patch, self-contained function)

**VRFY-01 Device Testing Verdict:** [ ] PASS / [ ] FAIL

---

## VRFY-02: No Patreon Login Prompt

**Precondition:** This must PASS before proceeding to VRFY-03 (per D-05).

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | No login prompt on first launch after install | [ ] PASS / [ ] FAIL | |
| 2 | No subscription gate when opening Settings > YTLite | [ ] PASS / [ ] FAIL | |
| 3 | No paywall when toggling Advanced Mode (Settings > YTLite > General > Advanced Mode) | [ ] PASS / [ ] FAIL | |
| 4 | No "Subscribe to unlock" text visible anywhere in settings | [ ] PASS / [ ] FAIL | |
| 5 | Settings panel shows all categories: General, Navbar, Tabbar, Overlay, Player, Shorts, Other, SponsorBlock | [ ] PASS / [ ] FAIL | Requires Advanced Mode ON |

**Screenshot:** Save as `evidence/screenshots/vrfy02-settings.png` (full settings panel with all categories visible)

**Static Analysis Verdict:** PASS (HIGH confidence -- dvnLocked unconditionally returns 0)

**VRFY-02 Device Testing Verdict:** [ ] PASS / [ ] FAIL

---

## VRFY-03: Gated Features Accessible Without Login

**Precondition:** VRFY-01 and VRFY-02 must PASS first.

### D-03: Explicitly Required Features

These three features are explicitly named in the requirements and must be verified.

#### SponsorBlock

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | SponsorBlock section visible in Settings (requires Advanced Mode) | [ ] PASS / [ ] FAIL | |
| 2 | SponsorBlock can be toggled ON | [ ] PASS / [ ] FAIL | |
| 3 | Sponsor segments are skipped during video playback (play a video with known sponsors) | [ ] PASS / [ ] FAIL | |

**Screenshot:** Save as `evidence/screenshots/vrfy03-sponsorblock.png` (SponsorBlock settings or segment skip in action)

#### Sleep Timer

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Sleep timer option accessible (check Overlay or Player settings, or playback controls) | [ ] PASS / [ ] FAIL | |
| 2 | Timer can be set to a duration | [ ] PASS / [ ] FAIL | |

**Screenshot:** Save as `evidence/screenshots/vrfy03-sleeptimer.png` (sleep timer UI)

#### Downloads

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Download button visible on video player | [ ] PASS / [ ] FAIL | |
| 2 | Tapping download initiates download (no subscription prompt) | [ ] PASS / [ ] FAIL | |
| 3 | Downloaded video appears in download manager | [ ] PASS / [ ] FAIL | |

**Screenshot:** Save as `evidence/screenshots/vrfy03-downloads.png` (download manager with a downloaded video)

### D-04: Spot-Check Additional Gated Features

These features are spot-checked to confirm the dvnLocked bypass is comprehensive.

#### Background Playback

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Audio continues playing when app is backgrounded (press Home while video plays) | [ ] PASS / [ ] FAIL | |
| 2 | Now Playing controls visible on lock screen | [ ] PASS / [ ] FAIL | |

#### Ad Removal

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | No pre-roll video ads before/during video playback | [ ] PASS / [ ] FAIL | |
| 2 | No banner ads visible in feed or video player | [ ] PASS / [ ] FAIL | |

#### Video Quality Auto-Selection

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | WiFi quality preference available in Settings > YTLite (Player or General) | [ ] PASS / [ ] FAIL | |
| 2 | Cellular quality preference available in Settings > YTLite (Player or General) | [ ] PASS / [ ] FAIL | |

#### Premium Logo Removal

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | YouTube logo appears as standard (not Premium branding) OR logo removal setting available | [ ] PASS / [ ] FAIL | |

**VRFY-03 Device Testing Verdict:** [ ] PASS / [ ] FAIL

---

## D-09: dvnCheck Secondary Gate Assessment

Per D-08, dvnCheck at 0x1eb78 was intentionally NOT patched. This section assesses whether dvnCheck independently gates any features, which would require a follow-up patch.

| # | Question | Answer | Details |
|---|----------|--------|---------|
| 1 | Did any feature show a subscription prompt or "Subscribe to unlock" message? | [ ] Yes / [ ] No | |
| 2 | If yes, which specific feature(s) showed a gate? | | |
| 3 | Recommended action | [ ] No action needed (all features unlocked) / [ ] Investigate dvnCheck at 0x1eb78 as secondary bypass target | |

**Context (D-08):** dvnCheck at 0x1eb78 calls a Patreon auth function and returns true/false based on authentication status. It was left unpatched because dvnLocked is the primary gate. If dvnCheck independently gates features, a follow-up 8-byte patch (similar MOV W0, #0 + RET) at 0x1eb78 would be needed in the CI pipeline step.

---

## Summary

| Requirement | Static Analysis | Device Testing | Final Verdict |
|-------------|----------------|----------------|---------------|
| VRFY-01: Patched tweak loads without crash | PASS (HIGH confidence) | [ ] PASS / [ ] FAIL | [ ] PASS / [ ] FAIL |
| VRFY-02: No Patreon login prompt | PASS (HIGH confidence) | [ ] PASS / [ ] FAIL | [ ] PASS / [ ] FAIL |
| VRFY-03: Gated features accessible | N/A (requires device) | [ ] PASS / [ ] FAIL | [ ] PASS / [ ] FAIL |

**Overall Verdict:** [ ] PASS -- All requirements met / [ ] FAIL -- See notes above

**dvnCheck Follow-up Required:** [ ] Yes / [ ] No

---

## Evidence Index

| Evidence Item | File Path | Description |
|---------------|-----------|-------------|
| App launch | `evidence/screenshots/vrfy01-launch.png` | YouTube home screen with YTLite loaded |
| Settings panel | `evidence/screenshots/vrfy02-settings.png` | Full YTLite settings with all categories visible |
| SponsorBlock | `evidence/screenshots/vrfy03-sponsorblock.png` | SponsorBlock settings or segment skip |
| Sleep timer | `evidence/screenshots/vrfy03-sleeptimer.png` | Sleep timer UI |
| Downloads | `evidence/screenshots/vrfy03-downloads.png` | Download manager with downloaded video |
| Static analysis | `evidence/static-analysis.md` | Full static analysis report from Plan 01 |

---

*Report template created: 2026-04-20*
*Static analysis results incorporated from Plan 02-01*
*Device testing sections pending human tester completion*
