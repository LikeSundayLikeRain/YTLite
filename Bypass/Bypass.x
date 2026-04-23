#import <substrate.h>
#import <dlfcn.h>

static BOOL (*orig_dvnLocked)(void);
static BOOL hook_dvnLocked(void) {
    return NO;
}

static BOOL (*orig_dvnCheck)(void);
static BOOL hook_dvnCheck(void) {
    return YES;
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
}
