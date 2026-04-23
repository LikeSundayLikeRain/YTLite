#import <substrate.h>
#import <dlfcn.h>

struct BlockLayout {
    void *isa;
    int flags;
    int reserved;
    void (*invoke)(struct BlockLayout *);
};

static void (*orig_ptnRegisterBlock)(struct BlockLayout *block);
static void hook_ptnRegisterBlock(struct BlockLayout *block) {
    if (block && block->invoke) {
        block->invoke(block);
    }
}

static BOOL (*orig_dvnLocked)(void);
static BOOL hook_dvnLocked(void) {
    return NO;
}

static BOOL (*orig_dvnCheck)(void);
static BOOL hook_dvnCheck(void) {
    if (orig_dvnCheck) {
        orig_dvnCheck();
    }
    return YES;
}

%ctor {
    void *ptn = dlsym(RTLD_DEFAULT, "ptnRegisterBlock");
    if (ptn) {
        MSHookFunction(ptn, (void *)&hook_ptnRegisterBlock, (void **)&orig_ptnRegisterBlock);
    }

    void *locked = dlsym(RTLD_DEFAULT, "dvnLocked");
    if (locked) {
        MSHookFunction(locked, (void *)&hook_dvnLocked, (void **)&orig_dvnLocked);
    }

    void *check = dlsym(RTLD_DEFAULT, "dvnCheck");
    if (check) {
        MSHookFunction(check, (void *)&hook_dvnCheck, (void **)&orig_dvnCheck);
    }
}
