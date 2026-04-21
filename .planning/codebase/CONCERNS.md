# Codebase Concerns

**Analysis Date:** 2026-04-20

## Tech Debt

**Monolithic Main File (1400+ lines):**
- Issue: `YTLite.x` is a single 1403-line file containing all hook logic -- ad blocking, UI hiding, player controls, Shorts customization, image downloading, comment management, tab bar customization, speed controls, and more. No separation of concerns.
- Files: `YTLite.x`
- Impact: Extremely difficult to maintain, debug, or extend individual features. Any change risks unintended side effects in unrelated features. Merge conflicts are likely when multiple contributors edit simultaneously.
- Fix approach: Split into feature-focused files (e.g., `Ads.x`, `Player.x`, `Shorts.x`, `TabBar.x`, `Comments.x`, `ImageUtils.x`). The Makefile already uses `$(wildcard *.x Utils/*.m)` so new `.x` files are automatically compiled.

**Duplicate `%hook YTVersionUtils` in Two Files:**
- Issue: `YTVersionUtils` is hooked in both `Sideloading.x` (line 32, for `appName`/`appID`) and `YTLite.x` (line 341, for `appVersion` spoofing). While Logos/Theos allows multiple hooks on the same class across files when hooking different methods, this is fragile and confusing. The hooks serve completely unrelated purposes.
- Files: `Sideloading.x:32`, `YTLite.x:341`
- Impact: Maintenance confusion; a developer may not realize the class is hooked elsewhere. If both files ever hook the same method, undefined behavior results.
- Fix approach: Consolidate all `YTVersionUtils` hooks into a single file, or clearly document the split with comments in both locations.

**Duplicate `%hook YTColdConfig` Blocks:**
- Issue: `YTColdConfig` is hooked in two separate `%hook` blocks within the same file (`YTLite.x`), at lines 224 and 745. This works in Logos but is a code organization smell.
- Files: `YTLite.x:224`, `YTLite.x:745`
- Impact: Developers may add new method hooks to one block without knowing the other exists. Makes it harder to understand all config overrides at a glance.
- Fix approach: Merge both `%hook YTColdConfig` blocks into a single block.

**Hardcoded Version Spoofing ("Temporary Fix"):**
- Issue: The comment on line 340 of `YTLite.x` reads "Temprorary Fix" (note the typo). The code spoofs the app version to `18.18.2` to make Classic Video Quality and Extra Speed Options work. This is a permanent workaround masquerading as temporary.
- Files: `YTLite.x:340-348`, `YTLite.x:350-359`
- Impact: Breaks whenever YouTube changes version-gated behavior. The `YTSettingsCell` hook (line 351) patches the display back to the real version, adding another layer of indirection. Users may experience unexpected behavior from version-dependent features.
- Fix approach: Investigate why these features require version spoofing and implement proper hooks that don't depend on version checks. At minimum, make the fake version configurable rather than hardcoded.

**Inconsistent UserDefaults Access in YTNativeShare.x:**
- Issue: `YTNativeShare.x` redefines `ytlBool` as a macro that creates a new `NSUserDefaults` instance on every call (`[[[NSUserDefaults alloc] initWithSuiteName:@"com.dvntm.ytlite"] boolForKey:key]`), instead of using the shared `YTLUserDefaults` singleton used everywhere else.
- Files: `YTNativeShare.x:31`
- Impact: Allocates a new `NSUserDefaults` object on every preference check. Inconsistent with the rest of the codebase. If the suite name ever changes, this file would be missed.
- Fix approach: Import `YTLite.h` and use the shared `ytlBool` macro backed by `YTLUserDefaults`, or at minimum use a cached instance.

**Massive Settings File with Deep Nesting:**
- Issue: `Settings.x` (653 lines) constructs the entire settings UI in a single method `updateYTLiteSectionWithEntry:`. Each settings category creates an inline block with its own array of items, leading to deeply nested code.
- Files: `Settings.x:113-627`
- Impact: Adding a new setting requires modifying a 500+ line method. Easy to introduce bugs from mismatched braces or incorrect nesting.
- Fix approach: Extract each settings category (General, Navbar, Overlay, Player, Shorts, Tabbar, Other) into its own helper method.

**Repeated Array Literals:**
- Issue: Speed labels and quality labels arrays are defined multiple times across `YTLite.x` and `Settings.x` (e.g., speed labels appear at lines 326, 468, 1304 of `YTLite.x` and lines 343, 348, 371, 376 of `Settings.x`; quality labels at lines 492 of `YTLite.x` and lines 398, 403, 426, 431 of `Settings.x`).
- Files: `YTLite.x:326,468,492,1304`, `Settings.x:343,348,371,376,398,403,426,431`
- Impact: Adding or reordering speed/quality options requires updating every copy. Out-of-sync arrays cause index mismatches leading to crashes or wrong values.
- Fix approach: Define these arrays as constants in a shared header or utility file.

## Known Bugs

**Potential Array Index Out of Bounds -- Startup Tab:**
- Symptoms: Crash when selecting a startup tab if the corresponding tab has been removed.
- Files: `YTLite.x:1220-1221`
- Trigger: The `pivotIdentifiers` array has 5 elements. `ytlInt(@"pivotIndex")` can hold any previously saved value. If user selects "Library" (index 4) as startup then removes the Library tab, the pivot identifier `FElibrary` is passed to `selectItemWithPivotIdentifier:` for a tab that no longer exists. The Settings UI (line 464-472) prevents new selection of hidden tabs but does not reset an already-saved index.
- Workaround: The app likely silently fails (no-op) rather than crashing, but the intended startup behavior is broken.

**Potential Array Index Out of Bounds -- Speed Index:**
- Symptoms: Crash if `speedIndex` or `autoSpeedIndex` holds an out-of-range value.
- Files: `YTLite.x:469`, `YTLite.x:1304,1308`
- Trigger: `speedLabels` array has 11 elements (indices 0-10) for auto speed, but 13 elements (indices 0-12) for hold-to-speed. If user upgrades from a version with fewer options or data corruption occurs, an out-of-range index causes `objectAtIndex:` crash.
- Workaround: None currently. No bounds checking before array access.

**Synchronous Network Call on Main Thread:**
- Symptoms: UI freeze when long-pressing a profile picture to save it.
- Files: `YTLite.x:1023`
- Trigger: `[NSData dataWithContentsOfURL:PFPURL]` is called synchronously on the main thread inside the `savePFP:` gesture handler. On slow networks, this blocks the UI.
- Workaround: None. The entire action sheet presentation depends on the synchronous download completing.

## Security Considerations

**No Photo Library Permission Check Before Save:**
- Risk: The code calls `PHPhotoLibrary` to save images without first checking or requesting authorization. On iOS 14+, this requires explicit permission.
- Files: `YTLite.x:885-888`, `YTLite.x:1028`, `YTLite.x:1077-1083`, `YTLite.x:1117-1124`
- Current mitigation: iOS will show a system permission dialog automatically, but if denied, the error is only shown as a toast. No graceful handling or re-prompt.
- Recommendations: Check `PHPhotoLibrary.authorizationStatus` before attempting saves. Provide a meaningful error message directing users to Settings if permission is denied.

**Unrestricted URL Scheme Opens:**
- Risk: The `shortsToRegular` method constructs a `vnd.youtube://` URL from `contentVideoID` and opens it without sanitization.
- Files: `YTLite.x:448-452`
- Current mitigation: `contentVideoID` comes from YouTube's own API response, so injection risk is low.
- Recommendations: Validate that `contentVideoID` matches expected format (alphanumeric + hyphens/underscores) before constructing the URL.

**Exit(0) for Settings Reset:**
- Risk: `exit(0)` is called after resetting settings, which Apple considers a crash from the user's perspective.
- Files: `Settings.x:598`
- Current mitigation: A confirmation dialog is shown before the action.
- Recommendations: Use `UIApplication`'s proper termination or prompt the user to manually restart. Using `exit(0)` can also cause data loss if other parts of the app have pending writes.

## Performance Bottlenecks

**Expensive `setFrame:` Hook on ASDisplayNode:**
- Problem: The `ASDisplayNode` `setFrame:` hook (lines 921-963) runs on *every* frame change of *every* display node in the app, performing string comparisons on accessibility identifiers and class checks.
- Files: `YTLite.x:921-963`
- Cause: `setFrame:` is one of the most frequently called methods in the Texture/AsyncDisplayKit framework. The hook adds conditional logic (string comparison, `isKindOfClass:`, supernode traversal) to every invocation, even when the `commentManager` and `postManager` features are disabled.
- Improvement path: Move the feature-enabled check (`ytlBool(...)`) to the very first line and return early with `%orig` before any other work. Better yet, avoid hooking `setFrame:` entirely and find a less frequently called method to attach comment/post data.

**Description String Matching for UI Elements:**
- Problem: Multiple hooks use `[description] containsString:` to identify UI elements, which is unreliable and slow. The `-description` method allocates a new string every time and its format is not part of any stable API contract.
- Files: `YTLite.x:39-48` (element data), `YTLite.x:172,176` (premium logo), `YTLite.x:656` (findCell), `YTLite.x:935,955` (comment/post detection), `YTLite.x:1000` (gesture attachment)
- Cause: No stable identifiers available for some YouTube internal views, so description strings are used as a workaround.
- Improvement path: Where possible, use `accessibilityIdentifier` instead of `description`. For the premium logo hook on `UIImageView`, the description-based matching is particularly fragile since Apple can change `UIImage`'s description format in any iOS update.

**Gesture Recognizers Added Repeatedly:**
- Problem: In `_ASDisplayView`'s `setKeepalive_node:` hook (line 988), a new `UILongPressGestureRecognizer` is added every time the method is called, without checking if one already exists. Similarly, `YTReelContentView`'s `setPlaybackView:` (line 835) and `YTEngagementPanelView`'s `layoutSubviews` (line 1253) add buttons/gestures on every call.
- Files: `YTLite.x:988-1007`, `YTLite.x:835-847`, `YTLite.x:1253-1277`
- Cause: No deduplication logic for gesture recognizer or subview addition.
- Improvement path: Check for existing gesture recognizers before adding new ones (e.g., by tagging or checking if one with the target/action already exists). The `copyInfoButton` in `layoutSubviews` already checks `viewWithTag:999` (line 1267), but gesture recognizers in the other locations do not.

**Synchronous Cache Size Calculation:**
- Problem: `GetCacheSize()` in `Settings.x` enumerates all files in the cache directory synchronously to compute total size. This runs on the main thread as part of settings display.
- Files: `Settings.x:9-24`
- Cause: Iterates every file with `subpathsOfDirectoryAtPath:` and reads attributes for each.
- Improvement path: Compute cache size asynchronously and cache the result, updating it in the background.

## Fragile Areas

**YouTube App Update Breakage:**
- Files: All `.x` files, `YouTubeHeaders.h`
- Why fragile: The entire tweak relies on hooking YouTube's private Objective-C classes and methods. Any YouTube app update can rename, remove, or change the signature of hooked classes/methods (e.g., `YTColdConfig`, `YTIElementRenderer`, `YTReelPlayerViewController`). The YouTubeHeaders are maintained externally and reference private APIs.
- Safe modification: Always test against the specific YouTube version being targeted. Use `respondsToSelector:` checks before calling methods that may not exist in newer versions. The `autoQuality` method (line 528) already does this correctly.
- Test coverage: None (no automated tests exist).

**Private API Reliance via valueForKey:**
- Files: `YTLite.x:137,325,334,441,631,924,968,1306,1308,1343`, `Settings.x:49,50,116,495,496`
- Why fragile: Extensive use of `valueForKey:` to access private instance variables (prefixed with `_`). These ivars can be renamed or removed in any YouTube update without warning.
- Safe modification: Wrap every `valueForKey:` call in a nil-check and provide fallback behavior.
- Test coverage: None.

**Premium Logo Detection via Image Description:**
- Files: `YTLite.x:164-181`
- Why fragile: The `UIImageView` `setImage:` hook matches against `[image description]` containing specific strings like `"Resources: youtube_logo)"`. This hooks *every* `UIImageView.setImage:` call in the entire app, and the matching depends on `UIImage`'s internal description format which Apple does not guarantee.
- Safe modification: Find an alternative identification method, such as checking the image view's position in the view hierarchy or using a more targeted hook.
- Test coverage: None.

**Element Removal by Index Path:**
- Files: `YTLite.x:702-725`
- Why fragile: `cellForItemAtIndexPath:` calls `deleteItemsAtIndexPaths:` during cell creation, which mutates the collection view's data source during a layout pass. This is inherently risky and can cause `NSInternalInconsistencyException` crashes if the timing is wrong or if the collection view's batch update state is unexpected.
- Safe modification: Use `performBatchUpdates:` for safe collection view mutations, or hide cells rather than deleting them.
- Test coverage: None.

## Scaling Limits

**Feature Flag Proliferation:**
- Current capacity: ~60+ boolean preferences managed via individual `ytlBool()` calls with string keys.
- Limit: Each preference is a separate string-keyed `NSUserDefaults` entry. There is no schema, no migration system, and no validation. The `registerDefaults` method in `YTLUserDefaults.m` only covers 8 of the 60+ keys.
- Scaling path: Introduce a structured preferences model with typed properties, default value registration for all keys, and version-based migration.

**Localization Coverage:**
- Current capacity: 13 language bundles in `layout/Library/Application Support/YTLite.bundle/`.
- Limit: Adding new features requires updating localization strings in all 13 bundles. No tooling exists to check for missing translations.
- Scaling path: Add a script to validate that all `LOC()` keys used in code have corresponding entries in every `.lproj/Localizable.strings` file.

## Dependencies at Risk

**YouTubeHeader (External, Unversioned):**
- Risk: `YouTubeHeaders.h` imports from `../YouTubeHeader/` (a sibling directory). This external dependency is not vendored, not versioned, and not declared in the build system. If the headers repository changes structure or is deleted, the project cannot build.
- Impact: Complete build failure.
- Migration plan: Vendor the required headers into the project, or pin to a specific commit via git submodule.

**Reachability (Vendored, Unmaintained):**
- Risk: `Utils/Reachability.h` and `Utils/Reachability.m` are a vendored copy of Tony Million's Reachability library. This library has not been updated for modern iOS APIs (NWPathMonitor available since iOS 12).
- Impact: Low immediate risk, but the library uses deprecated `SystemConfiguration` patterns.
- Migration plan: Replace with `NWPathMonitor` from the Network framework (available since iOS 12, which is below the minimum target of iOS 13.0).

## Missing Critical Features

**No Automated Tests:**
- Problem: Zero test files exist in the project. No unit tests, integration tests, or any automated verification.
- Blocks: Confident refactoring, regression detection, and safe contribution by new developers.

**No Settings Migration System:**
- Problem: When preference keys change between versions, user settings are silently lost. There is no versioned migration to map old keys to new ones.
- Blocks: Safe renaming or restructuring of preference keys.

**No Crash/Error Reporting:**
- Problem: Hooks that fail (e.g., due to YouTube API changes) fail silently or crash without any diagnostic information being captured.
- Blocks: Debugging issues reported by users who cannot provide crash logs.

## Test Coverage Gaps

**No Tests Whatsoever:**
- What's not tested: All hook logic, settings UI, preferences storage, image download/save, tab management, speed controls, quality selection, ad blocking, Shorts customization.
- Files: `YTLite.x`, `Settings.x`, `Sideloading.x`, `YTNativeShare.x`, `Utils/YTLUserDefaults.m`, `Utils/NSBundle+YTLite.m`
- Risk: Any change can introduce regressions that are only caught by end users. The monolithic structure makes it impossible to test features in isolation.
- Priority: High -- at minimum, unit tests for `YTLUserDefaults` and the utility functions (`downloadImageFromURL`, `genImageFromLayer`, `newCoverURL`, `autoQuality` logic) would catch the most impactful regressions.

---

*Concerns audit: 2026-04-20*
