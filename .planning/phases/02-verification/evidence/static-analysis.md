# Static Analysis Report: dvnLocked Patch Verification

**Date:** 2026-04-20
**Dylib:** YTLite.dylib from com.dvntm.ytlite_5.2_iphoneos-arm.deb
**SHA256 of upstream .deb:** cc48b87d76605b26e75414e2bc3d678b5f32f3c7bc57710754f29dc33b2fff9b

## SHA256 Integrity Check
- **Status:** PASS
- **Expected:** cc48b87d76605b26e75414e2bc3d678b5f32f3c7bc57710754f29dc33b2fff9b
- **Actual:** cc48b87d76605b26e75414e2bc3d678b5f32f3c7bc57710754f29dc33b2fff9b

## Byte Verification at 0x1eb64
- **Status:** PASS
- **Original bytes:** a889009008855339
- **Patched bytes:** 00008052c0035fd6
- **Expected patched:** 00008052c0035fd6

## Disassembly: dvnLocked (0x1eb64)
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

## Disassembly: dvnCheck (0x1eb78) -- Reference Only

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

## otool Cross-Reference

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

## VRFY-01 Static Confidence
- Patch applies valid ARM64 instructions (no illegal opcodes): PASS
- Function body is self-contained (MOV + RET, no branch): PASS
- **Conclusion:** HIGH confidence that patched tweak will load without crash

## VRFY-02 Static Confidence
- dvnLocked unconditionally returns 0: PASS
- **Conclusion:** HIGH confidence that no Patreon prompt will appear
