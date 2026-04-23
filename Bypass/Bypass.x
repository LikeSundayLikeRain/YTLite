#import <substrate.h>
#import <dlfcn.h>
#import <mach-o/dyld.h>
#import <string.h>

static BOOL (*orig_dvnLocked)(void);
static BOOL hook_dvnLocked(void) {
    return NO;
}

static BOOL (*orig_dvnCheck)(void);
static BOOL hook_dvnCheck(void) {
    return YES;
}

static uintptr_t getYTLiteBase(void) {
    for (uint32_t i = 0; i < _dyld_image_count(); i++) {
        const char *name = _dyld_get_image_name(i);
        if (name && strstr(name, "YTLite")) {
            return (uintptr_t)_dyld_get_image_header(i);
        }
    }
    return 0;
}

%ctor {
    void *locked = dlsym(RTLD_DEFAULT, "dvnLocked");
    if (locked) {
        MSHookFunction(locked, (void *)&hook_dvnLocked, (void **)&orig_dvnLocked);
    }

    void *check = dlsym(RTLD_DEFAULT, "dvnCheck");
    if (check) {
        MSHookFunction(check, (void *)&hook_dvnCheck, (void **)&orig_dvnCheck);
    }

    uintptr_t base = getYTLiteBase();
    if (base) {
        // ptnRegisterBlock checks a flag at virtual address 0x121fa00.
        // cmn x8, #1 / cset w8, eq → w8=1 when flag == -1 (authorized).
        // Set it to -1 so ptnRegisterBlock takes the authorized path.
        int64_t *authFlag = (int64_t *)(base + 0x121fa00);
        *authFlag = -1;

        // Also set the registration byte at 0x11524e0 to 0.
        // ptnRegisterBlock reads it, XORs with 1 → 1 = "registered" path.
        uint8_t *regByte = (uint8_t *)(base + 0x11524e0);
        *regByte = 0;

        // Set the lock byte at 0x11524e1 to 1 (unlocked).
        // bic w0, w9, w8 logic: byte=1 → returns 0 (unlocked).
        uint8_t *lockByte = (uint8_t *)(base + 0x11524e1);
        *lockByte = 1;
    }
}
