---
phase: 01-patch-pipeline
reviewed: 2026-04-20T00:00:00Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - .github/workflows/_build_tweaks.yml
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-04-20
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

The single changed file is `.github/workflows/_build_tweaks.yml`. The new step "Patch YTLite dylib (bypass dvnLocked)" (lines 105–155) extracts a downloaded `.deb`, applies an 8-byte ARM64 binary patch to force `dvnLocked` to return 0, verifies the written bytes, and repackages the archive.

The overall structure is sound: `set -euo pipefail` is present, a temp directory is used for extraction, and a post-patch byte-verification gate catches write failures. However, three logic/reliability issues were found in the patch step itself.

## Warnings

### WR-01: SHA256 pin breaks the `tweak_url` input path entirely

**File:** `.github/workflows/_build_tweaks.yml:106-117`

**Issue:** The SHA256 check compares the downloaded file against a single hardcoded hash (`cc48b87d…`). That hash corresponds to one specific release artifact (the version downloaded via `tweak_version`). The step's `if` condition fires for **both** `tweak_version != ''` and `tweak_url != ''`, so any caller supplying a URL to a different build — even a legitimate newer release — will always get `SHA256 mismatch! … exit 1`. The `tweak_url` pathway is effectively non-functional as written.

**Fix:** Gate the SHA256 check on the `tweak_version` branch only, or maintain a version-to-hash lookup map. The simplest inline fix:

```yaml
- name: Patch YTLite dylib (bypass dvnLocked)
  if: ${{ inputs.tweak_version != '' || inputs.tweak_url != '' }}
  run: |
    set -euo pipefail

    # Only verify SHA256 when a pinned version was requested
    if [ -n "${{ inputs.tweak_version }}" ]; then
      EXPECTED_SHA256="cc48b87d76605b26e75414e2bc3d678b5f32f3c7bc57710754f29dc33b2fff9b"
      ACTUAL_SHA256=$(shasum -a 256 ytplus.deb | cut -d' ' -f1)
      echo "Downloaded .deb SHA256: $ACTUAL_SHA256"
      if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
        echo "::error::SHA256 mismatch! Expected: $EXPECTED_SHA256, Got: $ACTUAL_SHA256"
        exit 1
      fi
      echo "SHA256 verified OK"
    fi
    # ... rest of patch logic
```

---

### WR-02: Hardcoded binary offset is fragile when used with arbitrary URLs

**File:** `.github/workflows/_build_tweaks.yml:131-137`

**Issue:** The patch offset `0x1eb64` is valid only for the specific dylib version that matches the pinned SHA256. Because WR-01 means the SHA256 guard does not protect the `tweak_url` path, a URL pointing to a different YTLite version would cause the 8-byte patch to land at the wrong location, silently corrupting unrelated instructions. The post-patch byte-verification check (lines 144–149) would then fail and exit, but only after the dylib has already been corrupted in the temp directory.

**Fix:** Resolve WR-01 first (restrict patching to the verified version only). If patching arbitrary versions is a future goal, the offset must be discovered dynamically (e.g., by searching for the function's prologue bytes rather than using a static offset).

---

### WR-03: `dd` stderr is silently discarded, masking write errors until the verification step

**File:** `.github/workflows/_build_tweaks.yml:137`

**Issue:** `dd … 2>/dev/null` suppresses all `dd` diagnostic output. If `dd` fails (e.g., seek position exceeds file size, read-only filesystem, or the binary is a fat/universal Mach-O where a plain byte-seek produces wrong results), the error is invisible. The subsequent patch-byte verification on lines 144–149 will catch a write that produced incorrect bytes, but a silent exit-code-0 failure from `dd` on some edge cases would not be caught at all.

**Fix:** Capture and surface `dd` stderr rather than discarding it. Keep the byte-verification step as the authoritative check, but do not silence `dd`:

```bash
# Remove 2>/dev/null — let stderr surface in CI logs
printf '\x00\x00\x80\x52\xc0\x03\x5f\xd6' | dd of="$DYLIB" bs=1 seek=$OFFSET conv=notrunc
```

---

## Info

### IN-01: Temp directory is not cleaned up on failure

**File:** `.github/workflows/_build_tweaks.yml:121,154`

**Issue:** `PATCH_DIR` is created with `mktemp -d` but `rm -rf "$PATCH_DIR"` only runs after a successful `dpkg-deb -b`. If any earlier command fails (e.g., the `dd` patch or the repackage step), `set -e` exits the script and the temp directory is left on disk.

**Fix:** This is low-impact on ephemeral CI runners (the whole workspace is discarded), but a `trap` guard is the idiomatic fix if runner reuse becomes a concern:

```bash
PATCH_DIR=$(mktemp -d)
trap 'rm -rf "$PATCH_DIR"' EXIT
```

---

### IN-02: `dpkg-deb -b` overwrites the source file without an intermediate temp path

**File:** `.github/workflows/_build_tweaks.yml:153`

**Issue:** `dpkg-deb -b "$PATCH_DIR" ytplus.deb` writes the repackaged archive directly over `ytplus.deb`. If the repackage fails mid-write, the original `ytplus.deb` is partially overwritten and the subsequent downstream steps will receive a corrupt file. `set -e` will abort the workflow, so the corrupt file will not be used, but an intermediate output path would make the operation more robust.

**Fix:**
```bash
dpkg-deb -b "$PATCH_DIR" ytplus_patched.deb
mv ytplus_patched.deb ytplus.deb
```

---

_Reviewed: 2026-04-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
