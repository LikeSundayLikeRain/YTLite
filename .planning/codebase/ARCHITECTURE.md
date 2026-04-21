# Architecture

**Analysis Date:** 2026-04-20

## Pattern Overview

**Overall:** iOS Runtime Method Hooking (Tweak/Injection Pattern)

**Key Characteristics:**
- Logos preprocessor (`%hook`, `%group`, `%ctor`) to swizzle Objective-C methods at runtime
- Injects into the YouTube iOS app process (`com.google.ios.youtube`) via MobileSubstrate/Substitute
- Feature-flag driven: all modifications gated behind `YTLUserDefaults` boolean/integer keys
- No standalone app binary; the tweak is a dynamic library loaded into YouTube's process

## Layers

**Hook Layer (Runtime Patches):**
- Purpose: Intercepts YouTube app method calls to modify behavior
- Location: `*.x` files in project root
- Contains: Logos-syntax Objective-C++ hook definitions
- Depends on: YouTube app's private classes (declared in `YTLite.h` and `YouTubeHeaders.h`)
- Used by: Loaded by MobileSubstrate at YouTube app launch

**Settings Layer (User Preferences UI):**
- Purpose: Provides a settings panel within YouTube's native settings
- Location: `Settings.x`
- Contains: Custom settings section injected into `YTSettingsSectionItemManager`
- Depends on: Hook Layer (reads same user defaults), YouTube's settings classes
- Used by: End users via YouTube Settings > YTLite

**Utility Layer (Shared Helpers):**
- Purpose: Provides reusable infrastructure (user defaults, bundle loading, network reachability)
- Location: `Utils/*.m`, `Utils/*.h`
- Contains: `YTLUserDefaults`, `NSBundle+YTLite`, `Reachability`
- Depends on: Foundation, SystemConfiguration frameworks
- Used by: Hook Layer and Settings Layer

**Sideloading Compatibility Layer:**
- Purpose: Patches bundle identifiers and keychain access for non-App Store installations
- Location: `Sideloading.x`
- Contains: Hooks that fix identity/keychain issues when YouTube is sideloaded (e.g., via AltStore)
- Depends on: Security framework, `dlfcn.h`
- Used by: Automatically activated when app is not from App Store

**Native Share Layer:**
- Purpose: Replaces YouTube's custom share sheet with iOS native `UIActivityViewController`
- Location: `YTNativeShare.x`
- Contains: Protobuf parsing of share entity, presentation of native share UI
- Depends on: Google Protobuf Objective-C runtime, YouTube's share command classes
- Used by: Triggered when user shares content (if `nativeShare` setting enabled)

## Data Flow

**Feature Toggle Flow:**

1. User toggles setting in YTLite settings panel (`Settings.x`)
2. `YTLUserDefaults` persists boolean/integer to `NSUserDefaults` suite `com.dvntm.ytlite`
3. At runtime, hooks read preference via `ytlBool(key)` / `ytlInt(key)` macros
4. Hook conditionally applies or skips modification based on current value

**Method Hook Flow:**

1. YouTube app launches, MobileSubstrate loads `YTLite.dylib`
2. `%ctor` (constructor) runs: validates state, shows first-run prompt
3. Logos runtime patches registered methods on YouTube's Objective-C classes
4. When YouTube calls a hooked method, the tweak's implementation runs first
5. Tweak either returns modified value, calls `%orig` (original), or skips it

**Video Quality Auto-Selection Flow:**

1. `YTPlayerViewController` `-loadWithPlayerTransition:playbackConfig:` fires
2. After 1.0s delay, `-autoQuality` method is invoked
3. Checks network status via `Reachability` (WiFi vs Cellular)
4. Reads corresponding quality index from user defaults
5. Finds closest available format from `activeVideo.selectableVideoFormats`
6. Applies `MLQuickMenuVideoQualitySettingFormatConstraint` to player

**State Management:**
- All state stored in `NSUserDefaults` suite `com.dvntm.ytlite`
- Singleton access via `[YTLUserDefaults standardUserDefaults]`
- Default values registered on first access: ads disabled, background playback enabled, upload button removed
- No database, no files, no network state

## Key Abstractions

**YTLUserDefaults:**
- Purpose: Centralized preference store for all tweak settings
- File: `Utils/YTLUserDefaults.h`, `Utils/YTLUserDefaults.m`
- Pattern: Singleton NSUserDefaults subclass with suite name `com.dvntm.ytlite`

**NSBundle+YTLite:**
- Purpose: Locates the tweak's resource bundle for localization and assets
- File: `Utils/NSBundle+YTLite.h`, `Utils/NSBundle+YTLite.m`
- Pattern: Category on NSBundle with class property, supports rootless/roothide jailbreaks

**Reachability:**
- Purpose: Determines current network type (WiFi vs Cellular) for quality selection
- File: `Utils/Reachability.h`, `Utils/Reachability.m`
- Pattern: Third-party singleton wrapper around SCNetworkReachability

**LOC() Macro:**
- Purpose: Localized string lookup from tweak bundle
- Definition: `YTLite.h` line 9
- Pattern: `#define LOC(key) [NSBundle.ytl_defaultBundle localizedStringForKey:key value:nil table:nil]`

**ytlBool() / ytlInt() Macros:**
- Purpose: Concise preference reading throughout hook code
- Definition: `YTLite.h` lines 11-12
- Pattern: Direct access to `[YTLUserDefaults standardUserDefaults]`

## Entry Points

**Main Constructor (`YTLite.x` %ctor):**
- Location: `YTLite.x` line 1383
- Triggers: MobileSubstrate injects dylib when YouTube launches
- Responsibilities: Validate Shorts-only mode state, show advanced mode prompt on first run

**Sideloading Constructor (`Sideloading.x` %ctor):**
- Location: `Sideloading.x` line 143
- Triggers: Same injection point, runs conditionally
- Responsibilities: Detect sideloaded install, activate identity patches if not from App Store

**Settings Entry (`Settings.x` updateYTLiteSectionWithEntry:):**
- Location: `Settings.x` line 113
- Triggers: YouTube settings screen renders category list
- Responsibilities: Build and register the YTLite settings section with all sub-pages

## Error Handling

**Strategy:** Minimal - silent fallback to original behavior

**Patterns:**
- If a hook's condition is not met, `%orig` (original implementation) is called unchanged
- Network/download errors shown via `YTToastResponderEvent` toast messages
- Photo library save errors surfaced with localized error description in toast
- No crash reporting; hooks are designed to be no-ops when disabled

## Cross-Cutting Concerns

**Logging:** None. No logging framework used; relies on silent operation.

**Validation:** Preferences validated at point of use (e.g., checking quality index bounds against available formats).

**Authentication:** Not applicable - tweak does not handle auth. Sideloading layer fixes keychain access groups for YouTube's own auth flow.

**Localization:** All user-facing strings use `LOC()` macro. 13 languages supported via `.lproj` directories in the bundle.

**Conditional Compilation:** `ROOTLESS` and `ROOTHIDE` build flags control jailbreak environment targeting. `TWEAK_VERSION` passed via `-DTWEAK_VERSION=` compiler flag from Makefile.

---

*Architecture analysis: 2026-04-20*
