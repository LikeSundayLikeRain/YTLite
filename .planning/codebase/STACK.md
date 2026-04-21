# Technology Stack

**Analysis Date:** 2026-04-20

## Languages

**Primary:**
- Objective-C / Logos (`.x` files) - All tweak logic, hooks, and settings UI
- Objective-C (`.m` / `.h` files) - Utility classes (`Utils/*.m`)

**Secondary:**
- YAML - GitHub Actions CI/CD workflows (`.github/workflows/*.yml`)
- JSON - Sileo depiction metadata (`Resources/depiction.json`)
- Apple Strings format - Localization files (`layout/Library/Application Support/YTLite.bundle/*.lproj/Localizable.strings`)

## Runtime

**Environment:**
- iOS (jailbroken / sideloaded) - ARM64 architecture only
- Minimum deployment target: iOS 13.0
- SDK: iPhoneOS 16.5

**Substrate:**
- Cydia Substrate (MobileSubstrate) - Required runtime dependency for method hooking
- Target app: `com.google.ios.youtube` (YouTube for iOS)

**Package Manager:**
- Debian package format (`.deb`) - Distributed via Cydia/Sileo/Zebra package managers
- Package ID: `com.dvntm.ytlite`

## Frameworks

**Core (Apple System Frameworks):**
- UIKit - UI manipulation and gesture recognition
- Foundation - Core data types, NSUserDefaults, NSBundle, NSFileManager
- SystemConfiguration - Network reachability detection (Wi-Fi vs cellular)

**Additional Apple Frameworks Used:**
- Photos (`Photos/Photos.h`) - Saving images/screenshots to photo library
- Security (via `SecItemCopyMatching`, `SecItemAdd`) - Keychain access for sideloading support
- `dlfcn.h` - Dynamic linker functions for sideloading bundle identity checks

**Build System:**
- [Theos](https://github.com/theos/theos) - iOS tweak build toolchain
  - Ref: commit `9bc73406cf80b711ef4d02c15ff1dedc4478a275` (pinned in CI)
  - Tweak type: `tweak.mk` (MobileSubstrate-based)

**Logos Preprocessor:**
- Part of Theos toolchain
- Syntax: `%hook`, `%end`, `%orig`, `%new`, `%ctor`, `%group`, `%init`, `%c()`
- Compiles `.x` files into standard Objective-C with runtime hooking calls

## Key Dependencies

**Critical (Runtime):**
- MobileSubstrate (`mobilesubstrate`) - The only declared package dependency; provides method swizzling/hooking runtime
- YouTubeHeader (external) - Private YouTube class declarations at `../YouTubeHeader/` (by PoomSmart)
- Google Protobuf Objective-C runtime (`../protobuf/objectivec/`) - Used by `YTNativeShare.x` for deserializing share entities

**Vendored Utilities:**
- Reachability (`Utils/Reachability.h`, `Utils/Reachability.m`) - Tony Million's network reachability library (BSD licensed), used for Wi-Fi/cellular quality switching
- NSBundle+YTLite (`Utils/NSBundle+YTLite.h`, `Utils/NSBundle+YTLite.m`) - Custom category for loading the tweak's resource bundle with roothide/rootless support
- YTLUserDefaults (`Utils/YTLUserDefaults.h`, `Utils/YTLUserDefaults.m`) - Custom NSUserDefaults subclass using suite name `com.dvntm.ytlite`

**Optional Integrations (CI-built companions):**
- YouPiP (PoomSmart) - Picture-in-Picture support
- YTUHD (Tonwalter888) - Ultra HD video quality
- YouQuality (PoomSmart) - Quality selection overlay
- Return-YouTube-Dislikes (PoomSmart) - Dislike count restoration
- YTABConfig (PoomSmart) - A/B testing configuration
- DontEatMyContent (therealFoxster) - Dynamic Island/notch content fix
- YTVideoOverlay (PoomSmart) - Shared video overlay framework
- YouGroupSettings (PoomSmart) - Grouped settings framework
- OpenYouTubeSafariExtension (BillyCurtis) - Safari extension for opening YouTube links

## Configuration

**Tweak Preferences:**
- Storage: `NSUserDefaults` with suite name `com.dvntm.ytlite`
- Implementation: `Utils/YTLUserDefaults.m` (custom subclass with registered defaults)
- Access macros in `YTLite.h`:
  - `ytlBool(key)` - Read boolean preference
  - `ytlInt(key)` - Read integer preference
  - `ytlSetBool(value, key)` - Write boolean preference
  - `ytlSetInt(value, key)` - Write integer preference
- Default values (from `YTLUserDefaults.m`):
  - `noAds`: YES
  - `backgroundPlayback`: YES
  - `removeUploads`: YES
  - `speedIndex`: 1
  - `autoSpeedIndex`: 3
  - `wiFiQualityIndex`: 0
  - `cellQualityIndex`: 0
  - `pivotIndex`: 0

**Build Configuration:**
- `Makefile` - Theos build configuration
  - `DEBUG=0`, `FINALPACKAGE=1` (release mode)
  - `ARCHS = arm64`
  - `TARGET := iphone:clang:16.5:13.0`
  - `PACKAGE_VERSION = 3.0.1`
  - Compiler flags: `-fobjc-arc -DTWEAK_VERSION=$(PACKAGE_VERSION)`
  - Source files: `$(wildcard *.x Utils/*.m)` (all `.x` and utility `.m` files)
- `control` - Debian package metadata
- `YTLite.plist` - MobileSubstrate filter; loads only into `com.google.ios.youtube`

**Package Schemes:**
- Standard (default): iphoneos-arm
- Rootless: `THEOS_PACKAGE_SCHEME=rootless` (via `make ROOTLESS=1`)
- Roothide: `THEOS_PACKAGE_SCHEME=roothide` (via `make ROOTHIDE=1`)

**Localization:**
- 13 languages: ar, en, es, fr, it, ja, ko, pl, ru, tr, vi, zh-Hans, zh-Hant
- Bundle path: `layout/Library/Application Support/YTLite.bundle/{lang}.lproj/Localizable.strings`
- Access macro: `LOC(key)` defined in `YTLite.h`

## Platform Requirements

**Development:**
- macOS with Xcode Command Line Tools
- Theos build system installed (`$THEOS` environment variable)
- iPhoneOS 16.5 SDK (available via `theos/sdks`)
- `make`, `ldid` (code signing), `dpkg` (package building)

**Production (Jailbroken):**
- iOS 13.0+ on ARM64 device
- Jailbreak with MobileSubstrate/Substitute support
- YouTube for iOS installed (`com.google.ios.youtube`)

**Production (Sideloaded):**
- iOS device (no jailbreak required)
- Decrypted YouTube IPA
- `cyan` / `pyzule-rw` tool for IPA injection
- Signing service (AltStore, TrollStore, etc.)

---

*Stack analysis: 2026-04-20*
