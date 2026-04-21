# Coding Conventions

**Analysis Date:** 2026-04-20

## Language & Framework

**Primary Language:** Objective-C with Logos preprocessor (`.x` files)
**Build System:** Theos (jailbreak tweak toolchain)
**Target:** iOS 13.0+ / arm64, compiled with Clang / iOS SDK 16.5
**ARC:** Enabled (`-fobjc-arc` in `Makefile`)

## Naming Patterns

**Files:**
- Feature modules: PascalCase matching feature area (`YTLite.x`, `Settings.x`, `Sideloading.x`, `YTNativeShare.x`)
- Headers: PascalCase matching the class or tweak name (`YTLite.h`, `YouTubeHeaders.h`)
- Utility classes: Use Objective-C category naming `NSBundle+YTLite.{h,m}` or plain PascalCase `YTLUserDefaults.{h,m}`, `Reachability.{h,m}`

**Classes:**
- Custom classes use `YTL` prefix: `YTLUserDefaults`
- Category extensions use `+TweakName` pattern: `NSBundle (YTLite)`, `YTSettingsSectionItemManager (Custom)`, `YTSettingsSectionItemManager (YTLite)`

**Functions:**
- Static helper functions use camelCase: `findCell()`, `downloadImageFromURL()`, `genImageFromLayer()`, `newCoverURL()`, `accessGroupID()`, `isSelf()`
- PascalCase for utility functions: `GetCacheSize()`, `YTImageNamed()`
- Use descriptive names reflecting purpose

**Variables:**
- camelCase for local and instance variables: `isTabSelected`, `isOverlayShown`, `rateBeforeSpeedmaster`
- `k` prefix for constants: `kDefaultsSuiteName`, `kQualityIndex`, `kBundlePath`
- User defaults keys use camelCase strings: `@"backgroundPlayback"`, `@"noAds"`, `@"hideShorts"`

**Macros:**
- All-caps or camelCase depending on purpose:
  - `LOC(key)` for localization lookups
  - `ytlBool(key)` and `ytlInt(key)` for reading user defaults
  - `ytlSetBool(value, key)` and `ytlSetInt(value, key)` for writing user defaults
- Defined in `YTLite.h`

**Types/Protocols:**
- Follow Apple/YouTube convention: PascalCase with `YT` or `YTI` prefix for YouTube internal classes

## Code Style

**Formatting:**
- No automated formatter detected (no `.clang-format`, no Prettier, no SwiftLint)
- Indentation: 4 spaces consistently
- Opening braces on same line as control structures
- Single-line method implementations are common for simple hooks:
  ```objc
  - (BOOL)isPlayableInBackground { return ytlBool(@"backgroundPlayback") ? YES : NO; }
  ```

**Linting:**
- No linting tools configured
- Compiler warnings managed via Theos/Clang defaults

**Line Length:**
- No enforced limit; lines commonly extend to 150+ characters for method signatures and inline conditionals

## Import Organization

**Order (in `.x` files):**
1. Main tweak header (`#import "YTLite.h"`)

**Order (in `YTLite.h`):**
1. System frameworks (`<UIKit/UIKit.h>`, `<Foundation/Foundation.h>`, `<Photos/Photos.h>`)
2. Local utility headers (`"Utils/NSBundle+YTLite.h"`, `"Utils/YTLUserDefaults.h"`, `"Utils/Reachability.h"`)
3. External YouTube headers (`"YouTubeHeaders.h"`)

**Order (in `YouTubeHeaders.h`):**
1. External header references using relative paths: `#import "../YouTubeHeader/YTAlertView.h"`

**Path Aliases:**
- None. All imports use relative paths.

## Logos Preprocessor Patterns

**Hook Structure:**
- Use `%hook ClassName` / `%end` blocks to swizzle methods
- Use `%new` to add new methods to existing classes
- Use `%orig` to call the original implementation
- Use `%c(ClassName)` to reference classes at runtime
- Use `%property` to add new properties to hooked classes
- Use `%group` / `%end` for conditional hook groups (see `Sideloading.x`)
- Use `%ctor` for constructor/initialization code

**Standard Hook Pattern (simple toggle):**
```objc
%hook ClassName
- (BOOL)someMethod { return ytlBool(@"settingKey") ? YES : %orig; }
%end
```

**Standard Hook Pattern (conditional execution):**
```objc
%hook ClassName
- (void)someMethod:(id)arg1 { if (!ytlBool(@"settingKey")) %orig; }
%end
```

**Standard Hook Pattern (argument modification):**
```objc
%hook ClassName
- (void)someMethod:(BOOL)arg1 { ytlBool(@"settingKey") ? %orig(NO) : %orig; }
%end
```

**Adding New Methods:**
```objc
%hook ClassName
%new
- (void)customMethod {
    // implementation
}
%end
```

**Adding Properties:**
```objc
%hook ClassName
%property (nonatomic, strong) NSString *customProperty;
%end
```

## User Defaults Access Pattern

**Always use the macros** defined in `YTLite.h` for reading/writing settings:
```objc
// Reading
ytlBool(@"settingKey")     // returns BOOL
ytlInt(@"settingKey")      // returns NSInteger

// Writing
ytlSetBool(value, @"key")
ytlSetInt(value, @"key")
```

These macros use `YTLUserDefaults` which wraps `NSUserDefaults` with suite name `com.dvntm.ytlite`.

**Exception:** `YTNativeShare.x` defines its own `ytlBool` macro using raw `NSUserDefaults` with the same suite name, because it imports different headers from a separate dependency path.

## Error Handling

**Patterns:**
- No exceptions or try/catch blocks used anywhere
- Errors are communicated to the user via toast messages using YouTube's built-in `YTToastResponderEvent`:
  ```objc
  [[%c(YTToastResponderEvent) eventWithMessage:LOC(@"Error") firstResponder:responder] send];
  ```
- Nil checks before method calls (defensive programming):
  ```objc
  if (self.contentVideoID != nil && [self.parentViewController isKindOfClass:...]) { ... }
  ```
- `isKindOfClass:` checks used extensively to verify runtime class types before casting
- `respondsToSelector:` checks for optional/version-dependent methods:
  ```objc
  if ([fc respondsToSelector:@selector(initWithVideoQualitySetting:formatSelectionReason:qualityLabel:)]) { ... }
  ```

## Localization

**Framework:** Custom `NSBundle` category (`NSBundle+YTLite`)
**Macro:** `LOC(key)` defined in `YTLite.h`
**String files:** `Localizable.strings` in `layout/Library/Application Support/YTLite.bundle/{lang}.lproj/`
**Supported languages:** ar, en, es, fr, it, ja, ko, pl, ru, tr, vi, zh-Hans, zh-Hant (13 languages)

**Convention for settings keys:**
- Title key: `@"FeatureName"` (e.g., `@"RemoveAds"`)
- Description key: `@"FeatureNameDesc"` (e.g., `@"RemoveAdsDesc"`)
- The `switchWithTitle:key:` helper in `Settings.x` automatically appends `Desc` to derive the description key.

## Comments

**When to Comment:**
- Section headers use `// Category Name` above each `%hook` or group of hooks
- Attribution comments reference original source: `// YouTube-X (https://github.com/PoomSmart/YouTube-X/)`
- Feature descriptions precede the hook: `// Background Playback`, `// Disable Ads`

**Style:**
- Single-line `//` comments only; no block comments except for license headers in `YTNativeShare.x`
- Comments are placed on the line immediately before the `%hook` directive
- No JSDoc/Doxygen-style documentation

**Attribution Convention:**
```objc
// Feature Name (https://github.com/author/repo)
// OR
// Feature Name @AuthorName (https://link)
```

## Function Design

**Size:**
- Hook methods are typically 1-30 lines
- Helper functions (static) can be larger: `downloadImageFromURL` (~35 lines), `autoQuality` (~50 lines)
- Settings builder methods are long due to UI construction (~500+ lines in `updateYTLiteSectionWithEntry:`)

**Parameters:**
- Follow Objective-C conventions with named parameters
- Static C functions use positional parameters

**Return Values:**
- Boolean hooks return `YES`/`NO` (not `true`/`false`)
- Ternary pattern is standard: `return ytlBool(@"key") ? YES : %orig;`

## Module Design

**Exports:**
- Each `.x` file is a self-contained module focused on one concern:
  - `YTLite.x`: All feature hooks (main tweak logic)
  - `Settings.x`: Settings UI construction
  - `Sideloading.x`: Sideloading compatibility patches
  - `YTNativeShare.x`: Native share sheet replacement

**Header Organization:**
- `YTLite.h`: Main header with macros, forward declarations, and interface extensions
- `YouTubeHeaders.h`: Imports external YouTube header dependencies
- `Utils/`: Self-contained utility classes with `.h`/`.m` pairs

**Barrel Files:** Not applicable (Objective-C uses header imports)

## Singleton Pattern

Use `dispatch_once` for singleton initialization:
```objc
+ (YTLUserDefaults *)standardUserDefaults {
    static dispatch_once_t onceToken;
    static YTLUserDefaults *defaults = nil;
    dispatch_once(&onceToken, ^{
        defaults = [[self alloc] initWithSuiteName:kDefaultsSuiteName];
    });
    return defaults;
}
```

## UI Patterns

**Action Sheets:**
```objc
YTDefaultSheetController *sheetController = [%c(YTDefaultSheetController) sheetControllerWithParentResponder:nil];
[sheetController addAction:[%c(YTActionSheetAction) actionWithTitle:LOC(@"Title") iconImage:image style:0 handler:^{
    // action
}]];
[sheetController presentFromViewController:vc animated:YES completion:nil];
```

**Alert Dialogs:**
```objc
YTAlertView *alertView = [%c(YTAlertView) confirmationDialogWithAction:^{
    // confirm action
} actionTitle:LOC(@"Yes") cancelTitle:LOC(@"No")];
alertView.title = LOC(@"Warning");
alertView.subtitle = LOC(@"Message");
[alertView show];
```

**Toast Messages:**
```objc
[[%c(YTToastResponderEvent) eventWithMessage:LOC(@"Message") firstResponder:responder] send];
```

**Gesture Recognizers:**
```objc
UILongPressGestureRecognizer *longPress = [[UILongPressGestureRecognizer alloc] initWithTarget:self action:@selector(handler:)];
longPress.minimumPressDuration = 0.3;
[self addGestureRecognizer:longPress];
```

## Settings Construction Pattern

Use the custom `switchWithTitle:key:` helper for toggle settings:
```objc
[self switchWithTitle:@"FeatureName" key:@"userDefaultsKey"]
```

Use `linkWithTitle:description:link:` for link items:
```objc
[self linkWithTitle:@"Author" description:LOC(@"Description") link:@"https://..."]
```

Group settings into picker-based sub-pages:
```objc
NSArray <YTSettingsSectionItem *> *rows = @[
    [self switchWithTitle:@"Feature1" key:@"key1"],
    [self switchWithTitle:@"Feature2" key:@"key2"]
];
YTSettingsPickerViewController *picker = [[%c(YTSettingsPickerViewController) alloc]
    initWithNavTitle:LOC(@"Category") pickerSectionTitle:nil rows:rows
    selectedItemIndex:NSNotFound parentResponder:[self parentResponder]];
[settingsViewController pushViewController:picker];
```

## Delayed Execution Pattern

Use `performSelector:withObject:afterDelay:` for deferred actions after player load:
```objc
[self performSelector:@selector(autoFullscreen) withObject:nil afterDelay:0.75];
[self performSelector:@selector(autoQuality) withObject:nil afterDelay:1.0];
```

---

*Convention analysis: 2026-04-20*
