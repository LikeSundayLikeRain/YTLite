#!/usr/bin/env python3
"""
Static verification of the dvnLocked binary patch in YTLite v5.2 dylib.

Downloads the upstream .deb, verifies SHA256, extracts the dylib, simulates the patch,
and uses Capstone to disassemble the patched instructions at offset 0x1eb64.

Also disassembles dvnCheck at 0x1eb78 for reference (NOT patched per D-08).
Cross-references with otool output.
"""

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

# --- Constants ---
DEB_URL = "https://github.com/dayanch96/YTLite/releases/download/v5.2/com.dvntm.ytlite_5.2_iphoneos-arm.deb"
EXPECTED_SHA256 = "cc48b87d76605b26e75414e2bc3d678b5f32f3c7bc57710754f29dc33b2fff9b"
DYLIB_REL_PATH = "Library/MobileSubstrate/DynamicLibraries/YTLite.dylib"
PATCH_OFFSET = 0x1EB64
PATCH_BYTES = b"\x00\x00\x80\x52\xc0\x03\x5f\xd6"
EXPECTED_HEX = "00008052c0035fd6"
DVNCHECK_OFFSET = 0x1EB78
DVNCHECK_SIZE = 32  # Read enough bytes to capture dvnCheck function


def download_deb(dest_path: str) -> None:
    """Download the upstream v5.2 .deb file."""
    print(f"Downloading .deb from {DEB_URL} ...")
    urllib.request.urlretrieve(DEB_URL, dest_path)
    print(f"Downloaded to {dest_path}")


def verify_sha256(file_path: str) -> tuple[str, bool]:
    """Verify SHA256 of the downloaded .deb."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    actual = sha256.hexdigest()
    match = actual == EXPECTED_SHA256
    return actual, match


def extract_deb(deb_path: str, extract_dir: str) -> None:
    """Extract .deb using ar + tar (works without dpkg-deb)."""
    print(f"Extracting .deb to {extract_dir} ...")
    # .deb is an ar archive; extract it first
    ar_dir = os.path.join(extract_dir, "_ar")
    os.makedirs(ar_dir, exist_ok=True)
    subprocess.run(["ar", "x", deb_path], cwd=ar_dir, check=True)

    # Find data.tar.* (could be data.tar.xz, data.tar.gz, data.tar.zst, etc.)
    data_tar = None
    for fname in os.listdir(ar_dir):
        if fname.startswith("data.tar"):
            data_tar = os.path.join(ar_dir, fname)
            break

    if data_tar is None:
        raise FileNotFoundError("No data.tar.* found in .deb archive")

    # Extract data tarball
    subprocess.run(["tar", "xf", data_tar, "-C", extract_dir], check=True)
    print(f"Extracted data archive: {os.path.basename(data_tar)}")


def read_bytes_at(file_path: str, offset: int, size: int) -> bytes:
    """Read `size` bytes from `file_path` at `offset`."""
    with open(file_path, "rb") as f:
        f.seek(offset)
        return f.read(size)


def write_bytes_at(file_path: str, offset: int, data: bytes) -> None:
    """Write `data` to `file_path` at `offset` (in-place)."""
    with open(file_path, "r+b") as f:
        f.seek(offset)
        f.write(data)


def disassemble(code: bytes, address: int) -> list[tuple[int, str, str]]:
    """Disassemble ARM64 code using Capstone. Returns list of (address, mnemonic, op_str)."""
    cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    results = []
    for insn in cs.disasm(code, address):
        results.append((insn.address, insn.mnemonic, insn.op_str))
    return results


def run_otool_cross_reference(dylib_path: str) -> str:
    """Run otool -tv on the dylib and extract the address range around 0x1eb64."""
    try:
        result = subprocess.run(
            ["otool", "-tv", dylib_path],
            capture_output=True, text=True, timeout=60
        )
        lines = result.stdout.splitlines()
        # Find lines near our patch address
        relevant = []
        for i, line in enumerate(lines):
            # Look for addresses in range 0x1eb50 - 0x1eb90
            if any(f"0{addr:x}" in line.lower() or f"{addr:x}" in line.lower()
                   for addr in range(0x1EB50, 0x1EB98, 4)):
                # Include some context
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                for j in range(start, end):
                    if lines[j] not in relevant:
                        relevant.append(lines[j])
        if relevant:
            return "\n".join(relevant)
        else:
            return "(No matching addresses found in otool output for range 0x1eb50-0x1eb98)"
    except Exception as e:
        return f"(otool error: {e})"


def main():
    results = {}
    tmpdir = tempfile.mkdtemp(prefix="ytlite_verify_")

    try:
        # Step 1: Download .deb
        deb_path = os.path.join(tmpdir, "ytlite.deb")
        download_deb(deb_path)

        # Step 2: Verify SHA256
        actual_sha256, sha256_ok = verify_sha256(deb_path)
        results["sha256"] = {"actual": actual_sha256, "pass": sha256_ok}
        print(f"\n=== SHA256 Verification ===")
        print(f"Expected: {EXPECTED_SHA256}")
        print(f"Actual:   {actual_sha256}")
        print(f"Status:   {'PASS' if sha256_ok else 'FAIL'}")

        if not sha256_ok:
            print("FATAL: SHA256 mismatch. Aborting.")
            sys.exit(1)

        # Step 3: Extract .deb
        extract_dir = os.path.join(tmpdir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        extract_deb(deb_path, extract_dir)

        # Step 4: Locate dylib
        dylib_path = os.path.join(extract_dir, DYLIB_REL_PATH)
        if not os.path.exists(dylib_path):
            print(f"FATAL: Dylib not found at {dylib_path}")
            sys.exit(1)
        print(f"\nDylib found: {dylib_path}")

        # Step 5: Read original bytes at 0x1eb64
        original_bytes = read_bytes_at(dylib_path, PATCH_OFFSET, 8)
        original_hex = original_bytes.hex()
        results["original_bytes"] = original_hex
        print(f"\n=== Original Bytes at 0x{PATCH_OFFSET:x} ===")
        print(f"Hex: {original_hex}")

        # Step 6: Disassemble original bytes
        orig_disasm = disassemble(original_bytes, PATCH_OFFSET)
        print("Original disassembly:")
        for addr, mnem, ops in orig_disasm:
            print(f"  0x{addr:x}: {mnem} {ops}")

        # Step 7: Simulate patch on a copy
        patched_dylib = os.path.join(tmpdir, "YTLite_patched.dylib")
        shutil.copy2(dylib_path, patched_dylib)
        write_bytes_at(patched_dylib, PATCH_OFFSET, PATCH_BYTES)

        # Step 8: Read patched bytes
        patched_bytes = read_bytes_at(patched_dylib, PATCH_OFFSET, 8)
        patched_hex = patched_bytes.hex()
        bytes_ok = patched_hex == EXPECTED_HEX
        results["patched_bytes"] = {"actual": patched_hex, "pass": bytes_ok}
        print(f"\n=== Patched Bytes at 0x{PATCH_OFFSET:x} ===")
        print(f"Hex:      {patched_hex}")
        print(f"Expected: {EXPECTED_HEX}")
        print(f"Status:   {'PASS' if bytes_ok else 'FAIL'}")

        # Step 9: Disassemble patched bytes
        patched_disasm = disassemble(patched_bytes, PATCH_OFFSET)
        print("\nPatched disassembly (dvnLocked):")
        for addr, mnem, ops in patched_disasm:
            print(f"  0x{addr:x}: {mnem} {ops}")

        # Step 10: Verify instruction semantics
        insn_valid = len(patched_disasm) >= 2
        mov_ok = False
        ret_ok = False
        if insn_valid:
            mnem0, ops0 = patched_disasm[0][1], patched_disasm[0][2]
            mnem1 = patched_disasm[1][1]
            mov_ok = mnem0 == "mov" and "w0" in ops0 and "#0" in ops0
            ret_ok = mnem1 == "ret"

        results["mov_check"] = mov_ok
        results["ret_check"] = ret_ok
        print(f"\nSemantic checks:")
        print(f"  MOV W0, #0: {'PASS' if mov_ok else 'FAIL'}")
        print(f"  RET:        {'PASS' if ret_ok else 'FAIL'}")

        # Step 11: Disassemble dvnCheck at 0x1eb78 (reference only, NOT patched)
        dvncheck_bytes = read_bytes_at(dylib_path, DVNCHECK_OFFSET, DVNCHECK_SIZE)
        dvncheck_disasm = disassemble(dvncheck_bytes, DVNCHECK_OFFSET)
        results["dvncheck_disasm"] = dvncheck_disasm
        print(f"\n=== dvnCheck at 0x{DVNCHECK_OFFSET:x} (Reference Only -- NOT patched) ===")
        for addr, mnem, ops in dvncheck_disasm:
            print(f"  0x{addr:x}: {mnem} {ops}")

        # Step 12: otool cross-reference
        otool_output = run_otool_cross_reference(patched_dylib)
        results["otool"] = otool_output
        print(f"\n=== otool Cross-Reference ===")
        print(otool_output)

        # Step 13: VRFY-01 and VRFY-02 static confidence
        no_illegal = insn_valid  # All bytes decoded to valid instructions
        self_contained = mov_ok and ret_ok and len(patched_disasm) == 2
        returns_zero = mov_ok and ret_ok

        results["vrfy01_valid_insns"] = no_illegal
        results["vrfy01_self_contained"] = self_contained
        results["vrfy02_returns_zero"] = returns_zero

        print(f"\n=== VRFY-01 Static Confidence ===")
        print(f"  Valid ARM64 instructions: {'PASS' if no_illegal else 'FAIL'}")
        print(f"  Self-contained (MOV+RET, no branch): {'PASS' if self_contained else 'FAIL'}")
        vrfy01_confidence = "HIGH" if (no_illegal and self_contained) else "LOW"
        print(f"  Conclusion: {vrfy01_confidence} confidence patched tweak will load without crash")

        print(f"\n=== VRFY-02 Static Confidence ===")
        print(f"  dvnLocked unconditionally returns 0: {'PASS' if returns_zero else 'FAIL'}")
        vrfy02_confidence = "HIGH" if returns_zero else "LOW"
        print(f"  Conclusion: {vrfy02_confidence} confidence no Patreon prompt will appear")

        # Summary
        all_pass = sha256_ok and bytes_ok and mov_ok and ret_ok and no_illegal and self_contained and returns_zero
        print(f"\n{'=' * 50}")
        print(f"OVERALL: {'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}")
        print(f"{'=' * 50}")

        # Store results for report generation
        results["all_pass"] = all_pass
        results["vrfy01_confidence"] = vrfy01_confidence
        results["vrfy02_confidence"] = vrfy02_confidence
        results["patched_disasm"] = patched_disasm
        results["original_disasm"] = orig_disasm

        if not all_pass:
            sys.exit(1)

    finally:
        # Cleanup
        shutil.rmtree(tmpdir, ignore_errors=True)

    return results


if __name__ == "__main__":
    main()
