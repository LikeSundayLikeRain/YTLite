# External Integrations

**Analysis Date:** 2026-04-20

## APIs & External Services

**YouTube (Host App - Hooked at Runtime):**
- The tweak injects into the YouTube iOS app (`com.google.ios.youtube`) via MobileSubstrate
- All YouTube APIs are accessed indirectly through hooking YouTube's own Objective-C classes
- No direct YouTube API calls are made by the tweak itself
- Private class declarations: `YouTubeHeaders.h` imports from `../YouTubeHeader/` (PoomSmart's reverse-engineered headers)

**SponsorBlock:**
- Built-in SponsorBlock integration (referenced in localization strings and README)
- Localization keys: `EnableSponsorBlock`, `EnableSponsorBlockDesc`, `SbPlayerButton`, `SbPlayerButtonDesc`
- Allows skipping sponsored segments in videos
- Implementation details are within the compiled tweak; settings are exposed through the YTLite preferences UI in `Settings.x`

**YouTube URL Generation:**
- `YTLite.x` line 580: Generates shareable timestamped links in format `https://www.youtube.com/watch?v={id}&t={seconds}s`
- `YTNativeShare.x`: Constructs share URLs for videos, playlists, channels, and clips:
  - Videos: `https://youtube.com/watch?v={id}`
  - Playlists: `https://youtube.com/playlist?list={id}`
  - Channels: `https://youtube.com/channel/{id}`
  - Clips: `https://youtube.com/clip/{id}`

**Image CDN Workaround (Russian Users):**
- `YTLite.x` lines 1355-1375: Replaces `yt3.ggpht.com` / `yt3.googleusercontent.com` hosts with `yt4.ggpht.com` / `yt4.googleusercontent.com`
- Toggle: `fixAlbums` preference
- Purpose: Fixes album cover/thumbnail loading issues for users in Russia

## Data Storage

**Databases:**
- None (no custom databases)

**Preferences:**
- `NSUserDefaults` with suite name `com.dvntm.ytlite`
- Implementation: `Utils/YTLUserDefaults.m`
- Stores all tweak settings (booleans, integers) for feature toggles
- Reset capability via `[YTLUserDefaults resetUserDefaults]`

**Keychain (Sideloading Only):**
- `Sideloading.x` lines 13-29: Reads/writes keychain items for `bundleSeedID` to obtain the access group
- Used for `SSOKeychainHelper` and `SSOKeychainCore` hooks to fix Google Sign-In on sideloaded installs
- Security framework functions: `SecItemCopyMatching`, `SecItemAdd`

**File Storage:**
- Photo library access via `Photos` framework (`PHPhotoLibrary`, `PHAssetCreationRequest`)
- `UIImageWriteToSavedPhotosAlbum` for saving profile pictures
- Clipboard access via `UIPasteboard` for copy operations (text, images)

**Caching:**
- Uses YouTube's native cache directory
- `Settings.x` lines 9-24: `GetCacheSize()` function reads `NSCachesDirectory` to display and clear cache size

## Authentication & Identity

**Auth Provider:**
- Google Sign-In (YouTube's built-in authentication)
- The tweak does not implement its own authentication system for YouTube

**Sideloading Identity Fixes (`Sideloading.x`):**
- Patches `NSBundle` to return correct `com.google.ios.youtube` bundle identifier
- Patches `YTVersionUtils`, `GCKBUtils`, `GPCDeviceInfo`, `OGLBundle`, `GVROverlayView`, `OGLPhenotypeFlagServiceImpl` for consistent app identity
- Patches `SSOConfiguration` for correct OAuth client identity
- Patches `SSOKeychainHelper` / `SSOKeychainCore` for correct keychain access group
- Patches `NSFileManager.containerURLForSecurityApplicationGroupIdentifier` to redirect App Group directory to Documents
- Patches `GULAppEnvironmentUtil.isFromAppStore` to return YES
- Conditional: Only activates when no App Store receipt exists (sideloaded detection at `Sideloading.x` line 144)

**Patreon Integration:**
- Localization keys reference Patreon login (`Log-inViaPatreon`, `ManageAccount`, `FeaturesNotActivated`)
- Likely used for feature gating/premium features
- Settings link: `Settings.x` does not directly call Patreon API; links to donation pages only

## Monitoring & Observability

**Error Tracking:**
- None (no crash reporting or analytics SDK)

**Logs:**
- No custom logging framework
- Uses YouTube's built-in toast notification system (`YTToastResponderEvent`) for user-facing messages
- Alert dialogs via `YTAlertView` for confirmations and warnings

## CI/CD & Deployment

**Hosting:**
- GitHub repository: `dayanch96/YTLite`
- GitHub Releases for distribution (draft releases)
- Sileo/Cydia repository depiction: `Resources/depiction.json`

**CI Pipeline (GitHub Actions):**
- `.github/workflows/main.yml` - "Create YouTube Plus app" (production IPA builder)
  - Manual trigger (`workflow_dispatch`) with configurable tweak integrations
  - Builds optional companion tweaks from source via Theos
  - Downloads decrypted YouTube IPA from user-provided URL
  - Injects tweaks using `cyan` (pyzule-rw) tool
  - Uploads patched IPA as draft GitHub Release

- `.github/workflows/ytp_beta.yml` - "[BETA] Create YouTube Plus app"
  - Same as main but accepts direct tweak URL instead of version number
  - For testing pre-release tweak builds

- `.github/workflows/cyan_ts.yml` - "Generate TrollFools/Cyan files"
  - Generates `.cyan` files (for Cyan tweak injector) and `.zip` files (for TrollFools)
  - Alternative distribution format for non-jailbroken devices

- `.github/workflows/_build_tweaks.yml` - "Build Tweaks (Helper)"
  - Reusable workflow called by all three main workflows
  - Sets up Theos environment with cached dependencies
  - Clones and builds each optional companion tweak
  - Installs build dependencies: `make`, `ldid`, `dpkg` via Homebrew
  - Downloads iPhoneOS 16.5 SDK from `theos/sdks`
  - Clones `YouTubeHeader` and `PSHeader` for compilation

**CI Dependencies:**
- Runner: `macos-latest`
- Tools: `brew install make ldid dpkg`
- Python: `pipx install pyzule-rw` (cyan IPA injector)
- Actions: `actions/checkout@v6`, `actions/cache@v5`, `actions/download-artifact@v8`, `actions/upload-artifact@v7`, `softprops/action-gh-release@v3`, `levibostian/action-hide-sensitive-inputs@v1`

## Protobuf Integration

**Google Protocol Buffers (Objective-C runtime):**
- Used in `YTNativeShare.x` for deserializing YouTube's internal share entity format
- Imports: `GPBDescriptor.h`, `GPBMessage.h`, `GPBUnknownField.h`, `GPBUnknownFieldSet.h`
- Source: `../protobuf/objectivec/` (external dependency, not vendored in repo)
- Used to parse `serializedShareEntity` from `YTIUpdateShareSheetCommand` to extract video/playlist/channel/clip IDs

## Network Connectivity

**Reachability (`Utils/Reachability.h`, `Utils/Reachability.m`):**
- Tony Million's Reachability library (vendored, BSD license)
- Monitors network status: `NotReachable`, `ReachableViaWiFi`, `ReachableViaWWAN`
- Uses `SystemConfiguration` framework (`SCNetworkReachability` APIs)
- Purpose: Allows setting different video quality preferences for Wi-Fi vs cellular connections

**Direct Network Calls:**
- `YTLite.x` line 881-882: `NSURLSession.sharedSession` for downloading images (profile pictures, post images)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## External Links (Settings UI)

**Donation Links (in `Settings.x`):**
- PayPal: `https://paypal.me/dayanch96`
- GitHub Sponsors: `https://github.com/sponsors/dayanch96`
- Buy Me a Coffee: `https://www.buymeacoffee.com/dayanch96`
- Boosty: `https://boosty.to/dayanch96`

**Credit Links (in `Settings.x`):**
- Developer and contributor GitHub/Twitter profiles
- Open-source project references (PoomSmart, MiRO92, Tony Million, jkhsjdhjs)

## Environment Configuration

**Required env vars:**
- `THEOS` - Path to Theos installation (build-time only)
- No runtime environment variables; all configuration is via `NSUserDefaults`

**Secrets:**
- No secrets required for the tweak itself
- CI workflows require GitHub token (implicit via `GITHUB_TOKEN`) for release uploads
- IPA URL is provided at workflow dispatch time (user input, hidden via `action-hide-sensitive-inputs`)

---

*Integration audit: 2026-04-20*
