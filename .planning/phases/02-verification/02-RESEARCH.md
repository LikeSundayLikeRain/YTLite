# Phase 2: Verification - Research

**Researched:** 2026-04-20
**Domain:** iOS tweak runtime verification, binary analysis, sideloading
**Confidence:** MEDIUM (device testing is blocked; static analysis path is HIGH confidence)

## Summary

Phase 2 verifies that the patched YTLite IPA works end-to-end: the tweak loads without crash (VRFY-01), no Patreon login prompt appears (VRFY-02), and previously gated features are accessible (VRFY-03). This is fundamentally a manual testing phase -- the patched binary injects into YouTube at runtime via MobileSubstrate and there is no automated test harness.

The critical blocker is that **no iOS device, sideloading tools, or iOS simulator infrastructure exists on this machine**. No Xcode (only Command Line Tools), no iOS SDK, no simulators, no `ideviceinstaller`, no `ios-deploy`, no Sideloadly, no AltStore, no TrollStore. The CI pipeline itself has not been run yet (no workflow runs or releases exist in the GitHub repo).

However, a **static verification path is available** as a complement: `otool` (Apple LLVM 21.0.0), `objdump`, `xxd`, and Python `capstone` 5.0.7 are all installed. These can disassemble the patched dylib to confirm the `dvnLocked` function returns 0 at the instruction level -- providing high confidence that the patch is correct without requiring a device. Full behavioral verification (features actually working) still requires manual device testing.

**Primary recommendation:** Execute in two waves: (1) static analysis of patched dylib to confirm patch correctness, (2) manual device testing with structured checklist once sideloading setup is available. The plan should treat device setup as a prerequisite step with explicit guidance.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Manual device testing via sideloading. The patched IPA must be installed on a real iOS device (or simulator if dylib injection is supported) and exercised by a human tester.
- **D-02:** Use a sideloading tool (AltStore, Sideloadly, or TrollStore depending on device/iOS version) to install the CI-produced IPA. The specific tool is Claude's discretion based on what's available.
- **D-03:** Explicitly verify the three features named in VRFY-03: SponsorBlock, sleep timer, and downloads. These are the known gated features that must work without Patreon login.
- **D-04:** Spot-check additional gated features beyond the three named ones -- premium logo removal, ad blocking, background playback, video quality auto-selection -- to confirm the dvnLocked bypass is comprehensive.
- **D-05:** Verify VRFY-01 (no crash on load) and VRFY-02 (no Patreon prompt) as preconditions before feature testing.
- **D-06:** Produce a structured verification report (markdown) with a pass/fail checklist per feature, organized by requirement (VRFY-01, VRFY-02, VRFY-03).
- **D-07:** Screenshots or screen recordings for key moments: app launch (no gate), settings panel (features visible), and each gated feature in use. Screenshots stored as references in the report.
- **D-08:** Do NOT patch dvnCheck at 0x1eb78 preemptively. Test with only dvnLocked patched first.
- **D-09:** If any feature still shows a Patreon gate or subscription prompt during testing, investigate dvnCheck as a secondary bypass target.

### Claude's Discretion
- Exact sideloading tool choice and setup instructions
- Test report template structure and formatting
- Order of feature verification
- Whether to include a static analysis step (e.g., disassemble the patched dylib to confirm dvnLocked returns 0) as a complement to runtime testing

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VRFY-01 | Patched tweak loads without crash when injected into YouTube app | Static analysis can verify patch correctness (valid ARM64 instructions). Runtime crash testing requires device. |
| VRFY-02 | No Patreon login prompt appears on launch | Static analysis can confirm dvnLocked returns 0. Behavioral confirmation requires device. |
| VRFY-03 | Previously gated features (SponsorBlock, sleep timer, downloads) accessible without login | SponsorBlock and sleep timer are binary-only features (not in source). Device testing required to confirm accessibility. Source confirms download manager and other features use ytlBool() gate pattern. |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Static patch verification | Local workstation (CLI tools) | -- | otool/capstone disassemble the patched dylib offline |
| CI artifact production | GitHub Actions runner | -- | Workflow dispatch builds the IPA; must run remotely |
| IPA sideloading | Physical iOS device | -- | No simulator support for MobileSubstrate tweaks |
| Runtime feature testing | Physical iOS device | -- | Features execute within the YouTube app process |
| Verification report authoring | Local workstation | -- | Markdown report created from test evidence |

## Standard Stack

### Core (Static Analysis)
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| otool | Apple LLVM 21.0.0 | Mach-O disassembly and header inspection | Ships with Xcode CLI tools; native ARM64 support [VERIFIED: local machine] |
| capstone (Python) | 5.0.7 | Programmable ARM64 disassembly | Industry-standard disassembly framework; already installed [VERIFIED: pip3 show] |
| xxd | system | Hex dump/verify patch bytes | Lightweight, already used in CI patch step [VERIFIED: local machine] |
| objdump | Apple LLVM 21.0.0 | Alternative disassembler for cross-reference | Ships with Xcode CLI tools [VERIFIED: local machine] |

### Core (Sideloading -- NOT currently available)
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| AltStore / AltServer | latest | Free sideloading (7-day signing) | Apple ID available, no jailbreak, iOS 14+ [ASSUMED] |
| Sideloadly | latest | GUI sideloading tool (7-day signing) | Alternative to AltStore, supports Windows/macOS [ASSUMED] |
| TrollStore | 2.x | Permanent IPA installation (no re-sign) | Device on exploitable iOS version (15.0-16.6.1, 17.0) [ASSUMED] |
| ios-deploy | latest | CLI deployment to connected device | For scripted installs from command line [ASSUMED] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| AltStore | Sideloadly | Sideloadly has simpler UX but same 7-day limit |
| AltStore | TrollStore | TrollStore is permanent but requires specific iOS versions |
| Device testing | iOS Simulator | Simulators cannot load MobileSubstrate tweaks -- NOT viable |

## Architecture Patterns

### System Architecture Diagram

```
[GitHub Actions CI] --> [Patched IPA artifact]
        |                        |
        v                        v
[Static Analysis]        [Manual Device Testing]
(otool/capstone on       (sideload IPA, exercise
 extracted dylib)         features, capture evidence)
        |                        |
        v                        v
[Patch Correctness       [Behavioral Verification
 Report: bytes OK,        Report: no crash, no gate,
 instructions valid]      features work]
        |                        |
        +--------+-------+-------+
                 |
                 v
       [Final Verification Report]
       (structured markdown, VRFY-01/02/03)
```

### Recommended Verification Structure
```
.planning/phases/02-verification/
├── 02-RESEARCH.md          # This file
├── 02-CONTEXT.md           # User decisions (exists)
├── 02-01-PLAN.md           # Verification plan
├── evidence/               # Test evidence
│   ├── static-analysis.md  # Disassembly output
│   └── screenshots/        # Device test screenshots
└── 02-VERIFICATION.md      # Final report
```

### Pattern 1: Static Binary Verification
**What:** Extract the patched dylib from the CI-produced .deb, disassemble the function at offset 0x1eb64, and confirm it contains `MOV W0, #0` + `RET`.
**When to use:** Before device testing (fast, no hardware needed, high confidence for patch correctness).
**Example:**
```python
# Source: capstone documentation + project context
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

# Read patched dylib bytes at offset 0x1eb64
with open("YTLite.dylib", "rb") as f:
    f.seek(0x1eb64)
    code = f.read(8)

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
for insn in md.disasm(code, 0x1eb64):
    print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")
# Expected output:
# 0x1eb64: mov w0, #0
# 0x1eb68: ret
```

### Pattern 2: otool Disassembly Verification
**What:** Use macOS-native otool to disassemble around the patch site.
**When to use:** Quick cross-reference without Python.
**Example:**
```bash
# Extract dylib from .deb first
dpkg-deb -R ytplus.deb extracted/
DYLIB="extracted/Library/MobileSubstrate/DynamicLibraries/YTLite.dylib"

# Disassemble around patch offset (show 4 instructions)
otool -tv -p _dvnLocked "$DYLIB" 2>/dev/null || \
  otool -tv "$DYLIB" | grep -A4 "1eb64:"

# Verify raw bytes
xxd -s 0x1eb64 -l 8 "$DYLIB"
# Expected: 0001eb64: 0000 8052 c003 5fd6
```

### Pattern 3: Manual Feature Verification Checklist
**What:** Structured walkthrough of each gated feature with pass/fail recording.
**When to use:** After sideloading the IPA on a device.
**Example template:**
```markdown
## VRFY-01: No Crash on Load
- [ ] YouTube app launches to home screen
- [ ] YTLite section visible in Settings
- [ ] No crash within 30 seconds of normal use

## VRFY-02: No Patreon Prompt
- [ ] No login prompt on first launch
- [ ] No subscription gate when opening Settings > YTLite
- [ ] No paywall when accessing Advanced mode toggle

## VRFY-03: Gated Features Accessible
- [ ] SponsorBlock: segments skipped during video playback
- [ ] Sleep Timer: timer button visible on overlay / tab bar menu
- [ ] Downloads: Download manager active when tapping download
- [ ] Background Playback: audio continues when app backgrounded
- [ ] Ad Removal: no video/banner ads during playback
- [ ] Video Quality Auto-Select: WiFi/cellular quality settings work
```

### Anti-Patterns to Avoid
- **Testing on simulator:** MobileSubstrate/Substitute does not work in the iOS Simulator. The tweak injects at runtime via dynamic library loading which requires a jailbroken or sideloaded environment on a real device. [VERIFIED: known iOS tweak limitation]
- **Assuming patch correctness equals feature correctness:** The patch makes `dvnLocked` return 0, but features could have additional gates (e.g., `dvnCheck`). D-08/D-09 address this by testing first and investigating secondary gates only if needed.
- **Skipping static analysis:** Even though device testing is the gold standard, static analysis catches patch application errors (wrong offset, wrong endianness) before wasting time on a device install.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ARM64 disassembly | Manual byte-to-instruction mapping | capstone / otool | ARM64 encoding is complex; tools handle it correctly |
| .deb extraction | Custom archive parser | dpkg-deb -R | Standard Debian format; dpkg-deb handles control files correctly |
| IPA installation | Manual codesigning + install | AltStore/Sideloadly/TrollStore | Signing, entitlements, and provisioning are non-trivial |
| Hex verification | Visual byte comparison | xxd + script assertion | Human hex comparison is error-prone; script is deterministic |

**Key insight:** This phase is verification, not implementation. The tools already exist (CI produces the artifact, sideloading tools install it, testing is manual). The plan should orchestrate the process, not build new tooling.

## Common Pitfalls

### Pitfall 1: No Decrypted IPA URL Available
**What goes wrong:** The CI workflow requires a `ipa_url` input pointing to a decrypted YouTube IPA. Without one, the workflow cannot run.
**Why it happens:** Decrypted IPAs are not publicly hosted and must be obtained from a jailbroken device or specific sources.
**How to avoid:** Document where to obtain a decrypted IPA (e.g., extract from a jailbroken device with CrackerXI+, or use a known source). The workflow input explicitly states "URL to the decrypted IPA file."
**Warning signs:** Workflow fails at "Download and validate IPA" step with mime-type error.

### Pitfall 2: 7-Day Signing Expiry (AltStore/Sideloadly)
**What goes wrong:** The sideloaded IPA expires after 7 days and the app no longer launches.
**Why it happens:** Free Apple Developer accounts have 7-day provisioning profile limits.
**How to avoid:** Re-sign before testing, or use TrollStore if device iOS version is compatible.
**Warning signs:** App icon grayed out, "Unable to Verify App" error on launch.

### Pitfall 3: SponsorBlock/Sleep Timer Not Visible Without Advanced Mode
**What goes wrong:** Tester reports features are missing, but they are hidden behind the "Advanced Mode" toggle in settings.
**Why it happens:** The source code shows `if (ytlBool(@"advancedMode"))` gates many settings categories (Overlay, Player, Shorts, Other). SponsorBlock and sleep timer may require Advanced Mode to be enabled.
**How to avoid:** Enable Advanced Mode in YTLite Settings before testing gated features.
**Warning signs:** Settings panel shows only General, Navbar, and Tabbar categories (missing Overlay, Player, Shorts, Other, SponsorBlock).

### Pitfall 4: Confusing Source-Code Features with Binary-Only Features
**What goes wrong:** Tester looks for SponsorBlock in source code to understand behavior, but it does not exist there.
**Why it happens:** The ~10 premium features (SponsorBlock, sleep timer, download manager enhancements) exist only in the pre-compiled v5.2 binary, not in this repo's source. The source is an older version (~v3.0.1).
**How to avoid:** Understand that verification of these features is purely behavioral (observe on device). Static analysis can confirm dvnLocked returns 0, but cannot confirm individual feature behavior.
**Warning signs:** grep for "SponsorBlock" in .x files returns no results.

### Pitfall 5: dvnCheck Secondary Gate Blocking Features
**What goes wrong:** dvnLocked returns 0 (verified), but some features still show a subscription prompt.
**Why it happens:** `dvnCheck` at offset 0x1eb78 may independently gate certain features by calling a Patreon auth function.
**How to avoid:** Per D-08/D-09, test with dvnLocked-only patch first. If any gate persists, investigate dvnCheck as secondary target.
**Warning signs:** dvnLocked verification passes but user sees "Subscribe to unlock" for specific features.

## Code Examples

### Extracting Dylib from CI Artifact for Static Analysis
```bash
# Source: CI workflow _build_tweaks.yml pattern
# Download the .deb artifact from GitHub Actions or Releases
gh run download <run-id> -n built-debs -D ./artifacts/

# Extract the dylib
PATCH_DIR=$(mktemp -d)
dpkg-deb -R artifacts/ytplus.deb "$PATCH_DIR"
DYLIB="$PATCH_DIR/Library/MobileSubstrate/DynamicLibraries/YTLite.dylib"

# Verify patch bytes match expected
ACTUAL=$(xxd -s 0x1eb64 -l 8 -p "$DYLIB")
EXPECTED="00008052c0035fd6"
if [ "$ACTUAL" = "$EXPECTED" ]; then
    echo "PASS: dvnLocked patch verified (MOV W0, #0 + RET)"
else
    echo "FAIL: Expected $EXPECTED, got $ACTUAL"
fi
```

### Full Disassembly Verification Script
```python
#!/usr/bin/env python3
"""Static verification of dvnLocked patch in YTLite.dylib"""
# Source: capstone docs + project offset knowledge
import sys
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

PATCH_OFFSET = 0x1eb64
EXPECTED_BYTES = bytes.fromhex("00008052c0035fd6")

def verify_patch(dylib_path):
    with open(dylib_path, "rb") as f:
        f.seek(PATCH_OFFSET)
        patch_bytes = f.read(8)

    # Byte-level check
    if patch_bytes != EXPECTED_BYTES:
        print(f"FAIL: Bytes at 0x{PATCH_OFFSET:x} = {patch_bytes.hex()}")
        print(f"      Expected: {EXPECTED_BYTES.hex()}")
        return False

    # Disassembly check
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    instructions = list(md.disasm(patch_bytes, PATCH_OFFSET))

    print(f"Disassembly at 0x{PATCH_OFFSET:x}:")
    for insn in instructions:
        print(f"  0x{insn.address:x}: {insn.mnemonic}\t{insn.op_str}")

    # Verify semantics
    if len(instructions) >= 2:
        if instructions[0].mnemonic == "mov" and "w0" in instructions[0].op_str and "#0" in instructions[0].op_str:
            if instructions[1].mnemonic == "ret":
                print("\nPASS: dvnLocked returns 0 (unlocked)")
                return True

    print("\nFAIL: Unexpected instruction sequence")
    return False

if __name__ == "__main__":
    dylib_path = sys.argv[1] if len(sys.argv) > 1 else "YTLite.dylib"
    sys.exit(0 if verify_patch(dylib_path) else 1)
```

### Sideloading with AltStore (Reference)
```bash
# Source: AltStore documentation [ASSUMED]
# Prerequisites: AltServer running on macOS, device connected via USB/WiFi

# 1. Install AltServer (macOS)
# Download from https://altstore.io/ and run AltServer.app

# 2. Install AltStore on device
# AltServer menu bar -> Install AltStore -> select device

# 3. Sideload the IPA
# On device: AltStore -> My Apps -> + -> select YouTubePlus.ipa
# Or via AltServer: AltServer -> Sideload .ipa -> select file and device
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Cydia Impactor for sideloading | AltStore / Sideloadly / TrollStore | 2019-2022 | Cydia Impactor no longer works; modern tools handle Apple's signing changes [ASSUMED] |
| MobileSubstrate (Saurik) | Substitute/ElleKit (modern jailbreaks) | 2020+ | Both work for tweak loading; Substitute is default on modern jailbreaks [ASSUMED] |
| Manual IPA re-signing | AltStore handles re-signing automatically | 2019+ | No need for manual codesign commands [ASSUMED] |

**Deprecated/outdated:**
- Cydia Impactor: No longer functional for sideloading [ASSUMED]
- AppSync Unified without jailbreak: Requires jailbreak, not applicable to stock devices [ASSUMED]

## Assumptions Log

> List all claims tagged [ASSUMED] in this research. The planner and discuss-phase use this
> section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | AltStore supports iOS 14+ with free Apple ID signing | Standard Stack | Wrong iOS version requirements could block sideloading |
| A2 | TrollStore works on iOS 15.0-16.6.1 and 17.0 | Standard Stack | Device may not be on compatible iOS version |
| A3 | SponsorBlock and sleep timer may require Advanced Mode enabled | Pitfall 3 | Tester may miss testing these features |
| A4 | MobileSubstrate tweaks cannot load in iOS Simulator | Anti-Patterns | If wrong, simulator testing would be possible (unlikely) |
| A5 | The ~10 premium features are binary-only and not in source | Pitfall 4 | If some are in source, we could add unit tests (unlikely based on grep results) |
| A6 | Cydia Impactor no longer works for sideloading | State of the Art | Minor -- just means one fewer sideloading option |

**If this table is empty:** N/A -- 6 assumptions identified above.

## Open Questions

1. **What iOS device and version is available for testing?**
   - What we know: No device is currently connected. No sideloading tools installed.
   - What's unclear: Does the user have an iOS device? What iOS version? Is it jailbroken?
   - Recommendation: Plan should include a prerequisite step asking the user to confirm device availability and iOS version, which determines the sideloading tool.

2. **Where to obtain a decrypted YouTube IPA?**
   - What we know: The CI workflow requires a `ipa_url` input with a direct download link to a decrypted IPA.
   - What's unclear: Whether the user already has one or needs guidance on obtaining it.
   - Recommendation: Plan should document this as a prerequisite with options (CrackerXI+ from jailbroken device, or community sources).

3. **Has the CI workflow been triggered yet?**
   - What we know: No workflow runs or releases exist in the repo. Phase 1 code is committed but not exercised.
   - What's unclear: Whether the user has already run it outside of what's visible.
   - Recommendation: Plan should include triggering the CI workflow as the first actionable step (produces the artifact to test).

4. **Does dvnCheck independently gate any features?**
   - What we know: D-08 says don't patch it preemptively. D-09 says investigate if features are still gated.
   - What's unclear: Which specific features (if any) use dvnCheck as a secondary gate.
   - Recommendation: Test all features with dvnLocked-only patch first. Document any that remain gated for potential dvnCheck follow-up.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| otool | Static analysis | Yes | Apple LLVM 21.0.0 | objdump (also available) |
| capstone (Python) | Programmable disassembly | Yes | 5.0.7 | otool CLI |
| xxd | Byte verification | Yes | system | od / hexdump |
| dpkg-deb | .deb extraction | Yes (via brew) | system | ar + tar manual extraction |
| Xcode + iOS SDK | Simulator testing | No | -- | Not viable (tweaks need real device) |
| xcodebuild | Building from source | No | -- | Not needed (binary patch only) |
| AltStore/Sideloadly | IPA installation | No | -- | Must be installed by user |
| ios-deploy | CLI device deploy | No | -- | AltStore GUI alternative |
| ideviceinstaller | Device management | No | -- | libimobiledevice (must install) |
| Physical iOS device | Runtime testing | Not detected | -- | BLOCKER for VRFY-01/02/03 runtime |
| gh CLI | Download CI artifacts | Yes | -- | Manual download from GitHub |
| GitHub Actions | IPA production | Yes (remote) | -- | -- |

**Missing dependencies with no fallback:**
- Physical iOS device for runtime behavioral testing (VRFY-01, VRFY-02, VRFY-03 full verification)
- Sideloading tool (depends on device and iOS version)

**Missing dependencies with fallback:**
- Xcode/iOS SDK: Not needed -- this is binary patch verification, not source compilation
- Static analysis tools ARE available as partial verification

## Sources

### Primary (HIGH confidence)
- Local machine tool verification: `otool`, `objdump`, `xxd`, `capstone` all confirmed installed and functional
- `.github/workflows/_build_tweaks.yml` lines 105-155: Exact patch mechanism (printf+dd at 0x1eb64)
- `.github/workflows/main.yml`: Full CI pipeline producing IPA via cyan injection
- `Settings.x`: Feature toggle pattern using `ytlBool(@"key")` with `advancedMode` gating
- `YTLite.x`: Feature implementations using `ytlBool()` gate pattern
- Phase 1 verification report: Confirms CI code is wired correctly, pending live run

### Secondary (MEDIUM confidence)
- `YTLUserDefaults.m` / `YTLite.h`: `ytlBool` macro reads from NSUserDefaults with suite `com.dvntm.ytlite`
- Feature list from localization strings (ko.lproj/Localizable.strings): SponsorBlock, SleepTimer, DownloadManager confirmed as features
- README.md: Lists SponsorBlock and download features

### Tertiary (LOW confidence)
- Sideloading tool compatibility and iOS version requirements [ASSUMED from training data]
- dvnCheck secondary gating behavior [unknown until tested]

## Metadata

**Confidence breakdown:**
- Standard stack (static analysis): HIGH -- tools verified on local machine
- Standard stack (sideloading): LOW -- no tools available, no device confirmed
- Architecture: HIGH -- verification flow is straightforward and well-understood
- Pitfalls: MEDIUM -- based on iOS tweak ecosystem knowledge and source code analysis
- Feature gate mechanism: HIGH -- confirmed via source code grep (ytlBool pattern)

**Research date:** 2026-04-20
**Valid until:** 2026-05-20 (stable -- binary patch and iOS sideloading ecosystem change slowly)
