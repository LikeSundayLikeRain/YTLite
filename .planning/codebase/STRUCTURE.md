# Codebase Structure

**Analysis Date:** 2026-04-20

## Directory Layout

```
YTLite/
├── YTLite.x                # Main tweak hooks (ads, player, UI, tabs, shorts)
├── Settings.x              # Settings panel injected into YouTube's settings
├── Sideloading.x           # Patches for non-jailbreak sideloaded installs
├── YTNativeShare.x         # Native iOS share sheet replacement
├── YTLite.h                # Main header: imports, macros, class declarations
├── YouTubeHeaders.h        # YouTube private API header imports (external)
├── YTLite.plist            # CydiaSubstrate filter (targets com.google.ios.youtube)
├── Makefile                # Theos build configuration
├── control                 # Debian package metadata
├── README.md               # Project documentation
├── Utils/                  # Shared utility classes
│   ├── YTLUserDefaults.h   # Custom NSUserDefaults subclass header
│   ├── YTLUserDefaults.m   # Custom NSUserDefaults subclass implementation
│   ├── NSBundle+YTLite.h   # Bundle category header
│   ├── NSBundle+YTLite.m   # Bundle category implementation
│   ├── Reachability.h      # Network reachability header
│   └── Reachability.m      # Network reachability implementation
├── Resources/              # Depiction assets (screenshots, icons)
│   ├── depiction.json      # Package depiction metadata
│   ├── icon.png            # Tweak icon
│   ├── header.png          # Depiction header image
│   └── scr*.jpg            # Screenshots (1-9)
├── layout/                 # Filesystem layout installed on device
│   └── Library/
│       └── Application Support/
│           └── YTLite.bundle/
│               ├── en.lproj/Localizable.strings
│               ├── ar.lproj/Localizable.strings
│               ├── es.lproj/Localizable.strings
│               ├── fr.lproj/Localizable.strings
│               ├── it.lproj/Localizable.strings
│               ├── ja.lproj/Localizable.strings
│               ├── ko.lproj/Localizable.strings
│               ├── pl.lproj/Localizable.strings
│               ├── ru.lproj/Localizable.strings
│               ├── tr.lproj/Localizable.strings
│               ├── vi.lproj/Localizable.strings
│               ├── zh-Hans.lproj/Localizable.strings
│               └── zh-Hant.lproj/Localizable.strings
├── FAQs/                   # FAQ content
├── .github/                # GitHub templates and CI
│   ├── ISSUE_TEMPLATE/     # Issue templates
│   └── workflows/          # GitHub Actions
└── .planning/              # Planning/analysis documents
```

## Directory Purposes

**Root (`/`):**
- Purpose: All source code lives at the project root (flat structure typical of Theos tweaks)
- Contains: `.x` (Logos/Objective-C++) source files, `.h` headers, build config
- Key files: `YTLite.x`, `Settings.x`, `Sideloading.x`, `YTNativeShare.x`

**Utils/:**
- Purpose: Reusable Objective-C classes shared across all `.x` source files
- Contains: User defaults management, bundle loading, network detection
- Key files: `YTLUserDefaults.m`, `NSBundle+YTLite.m`, `Reachability.m`

**layout/:**
- Purpose: Files installed to device filesystem by the package manager
- Contains: Localization bundles (`.lproj` directories with `Localizable.strings`)
- Key files: `layout/Library/Application Support/YTLite.bundle/en.lproj/Localizable.strings`

**Resources/:**
- Purpose: Package depiction assets for Cydia/Sileo package repositories
- Contains: Screenshots, icon, header image, JSON depiction
- Key files: `Resources/depiction.json`, `Resources/icon.png`

## Key File Locations

**Entry Points:**
- `YTLite.x`: Main tweak logic - all YouTube UI/behavior modifications
- `Settings.x`: Settings panel construction and preference management
- `Sideloading.x`: Conditional sideloading compatibility patches
- `YTNativeShare.x`: Share sheet replacement module

**Configuration:**
- `Makefile`: Build targets, architecture, SDK version, frameworks
- `YTLite.plist`: Substrate filter (which app to inject into)
- `control`: Debian package metadata (name, version, dependencies)

**Core Logic:**
- `YTLite.x` lines 1-100: Ad blocking and background playback
- `YTLite.x` lines 108-200: Navigation bar and UI element removal
- `YTLite.x` lines 300-546: Player behavior (quality, speed, fullscreen, captions)
- `YTLite.x` lines 700-860: Shorts modifications
- `YTLite.x` lines 860-1140: Image/comment/post management features
- `YTLite.x` lines 1140-1250: Tab bar customization
- `YTLite.x` lines 1300-1400: Speedmaster and RTL fixes

**Headers/Declarations:**
- `YTLite.h`: All interface declarations for YouTube classes used in hooks
- `YouTubeHeaders.h`: External imports from YouTubeHeader repository

**Preferences:**
- `Utils/YTLUserDefaults.m`: Default values, suite name, reset logic

**Localization:**
- `layout/Library/Application Support/YTLite.bundle/en.lproj/Localizable.strings`: English strings

## Naming Conventions

**Files:**
- Source files: PascalCase with `.x` extension for Logos (e.g., `YTLite.x`, `Settings.x`, `Sideloading.x`)
- Headers: PascalCase with `.h` extension (e.g., `YTLite.h`, `YouTubeHeaders.h`)
- Utility classes: PascalCase `.h`/`.m` pairs matching class name (e.g., `YTLUserDefaults.h/.m`)
- Categories: `ClassName+CategoryName.h/.m` (e.g., `NSBundle+YTLite.h/.m`)

**Directories:**
- PascalCase for code directories: `Utils/`, `Resources/`
- Lowercase for system layout: `layout/`

**Preference Keys:**
- camelCase strings: `@"backgroundPlayback"`, `@"noAds"`, `@"hideShorts"`, `@"shortsProgress"`
- Boolean keys prefixed with descriptive verbs: `no`, `hide`, `remove`, `disable`
- Index keys suffixed with `Index`: `@"speedIndex"`, `@"pivotIndex"`, `@"wiFiQualityIndex"`

## Where to Add New Code

**New Feature (Hook):**
- Primary code: Add `%hook` blocks in `YTLite.x` (group by feature area using comments)
- Settings toggle: Add `[self switchWithTitle:@"FeatureName" key:@"featureKey"]` in appropriate section of `Settings.x`
- Localization: Add keys to all `.lproj/Localizable.strings` files in `layout/Library/Application Support/YTLite.bundle/`
- If new YouTube class declarations needed: Add `@interface` in `YTLite.h`

**New Utility Class:**
- Implementation: `Utils/ClassName.h` and `Utils/ClassName.m`
- Import: Add `#import "Utils/ClassName.h"` in `YTLite.h`
- Build: Automatically included via `$(wildcard *.x Utils/*.m)` in Makefile

**New Settings Section:**
- Add in `Settings.x` inside `updateYTLiteSectionWithEntry:` method
- Follow existing pattern: create `YTSettingsSectionItem` with `itemWithTitle:` and push `YTSettingsPickerViewController`

**New Localization:**
- Create new `xx.lproj/Localizable.strings` in `layout/Library/Application Support/YTLite.bundle/`
- Copy all keys from `en.lproj/Localizable.strings` and translate values

**New Sideloading Fix:**
- Add hooks inside the `%group gSideloading` block in `Sideloading.x`

## Special Directories

**layout/:**
- Purpose: Mirrors device filesystem; contents are copied to jailbroken device during install
- Generated: No (manually maintained)
- Committed: Yes

**Resources/:**
- Purpose: Package repository depiction assets (not installed to device)
- Generated: No
- Committed: Yes

**.github/:**
- Purpose: GitHub issue templates and CI workflows
- Generated: No
- Committed: Yes

---

*Structure analysis: 2026-04-20*
