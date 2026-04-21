# YTLite Free Fork

## What This Is

A fork of YTLite v5.2, an iOS tweak that enhances the YouTube app with features like background playback, ad removal, video downloading, native share sheets, and UI customizations. The upstream v5.2 release introduced a Patreon subscription gate that locks most features behind a login. This fork removes that gate so all features remain free.

## Core Value

All tweak features work without any Patreon login or subscription check — the tweak behaves as if the user is fully subscribed.

## Requirements

### Validated

- :white_check_mark: Background playback — existing
- :white_check_mark: Ad removal (video ads, banner ads, native ads) — existing
- :white_check_mark: Video/audio download — existing
- :white_check_mark: Native share sheet — existing
- :white_check_mark: Video quality auto-selection (WiFi/Cellular) — existing
- :white_check_mark: UI customizations (tab bar, shorts, overlay buttons) — existing
- :white_check_mark: Playback controls (speed, default quality) — existing
- :white_check_mark: Sideloading compatibility — existing
- :white_check_mark: Settings panel in YouTube app — existing
- :white_check_mark: Localization (13 languages) — existing

### Active

- [ ] Patch `dvnLocked` function in the pre-compiled v5.2 dylib to always return 0 (unlocked)
- [ ] Update CI pipeline to use patched binary instead of downloading upstream gated one
- [ ] Verify all features (including premium: SponsorBlock, sleep timer, etc.) work without Patreon login

### Out of Scope

- Full removal of Patreon code — bypass is sufficient, minimal changes preferred
- Building from source — source is missing ~10 premium features; binary patch preserves all v5.2 features
- New feature development — this is a subscription removal fork, not a feature fork
- Upstream sync — no plan to merge future upstream changes (they'll have the paywall)

## Context

- YTLite is an Objective-C++ tweak using the Logos preprocessor (`%hook`, `%group`, `%ctor`)
- Injects into YouTube iOS app via MobileSubstrate/Substitute as a dynamic library
- All features are gated behind `YTLUserDefaults` boolean/integer keys
- The Patreon gate is in the pre-compiled binary only, NOT in this repo's source code
- `dvnLocked` at offset `0x1eb64` reads a subscription byte and returns 1 (locked) or 0 (unlocked) — 4 instructions
- `dvnCheck` at offset `0x1eb78` calls an auth function and returns true/false based on Patreon status
- The CI downloads pre-built `.deb` from `dayanch96/YTLite/releases` — it does NOT compile from source
- Build system uses theos Makefile, but the open-source code is an older version (~v3.0.1) missing premium features
- v5.2 is the latest release that introduced the subscription requirement

## Constraints

- **Minimal changes**: 4-byte binary patch of `dvnLocked` — don't touch anything else
- **Binary target**: `YTLite.dylib` from the v5.2 `.deb` at `Library/MobileSubstrate/DynamicLibraries/`
- **No testing on device yet**: Need iOS device or sideloading setup to verify

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Binary patch over full removal | 4-byte change vs. ripping out Patreon code — minimal risk | -- Pending |
| Patch binary over build from source | Source is missing ~10 premium features (SponsorBlock, sleep timer, etc.); patching preserves all v5.2 features | -- Pending |
| Fork at v5.2 | Last version before subscription was enforced is the baseline | -- Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check -- still the right priority?
3. Audit Out of Scope -- reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-20 after initialization*
