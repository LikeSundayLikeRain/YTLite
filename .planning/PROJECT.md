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

- [ ] Bypass Patreon subscription check so all features return "subscribed"
- [ ] Set up theos build environment to compile the tweak
- [ ] Verify all features work without Patreon login after bypass

### Out of Scope

- Full removal of Patreon code — bypass is sufficient, minimal changes preferred
- New feature development — this is a subscription removal fork, not a feature fork
- Upstream sync — no plan to merge future upstream changes (they'll have the paywall)

## Context

- YTLite is an Objective-C++ tweak using the Logos preprocessor (`%hook`, `%group`, `%ctor`)
- Injects into YouTube iOS app via MobileSubstrate/Substitute as a dynamic library
- All features are gated behind `YTLUserDefaults` boolean/integer keys
- The Patreon gate likely checks subscription status and conditionally enables/disables feature flags
- Build system uses theos Makefile
- v5.2 is the latest release that introduced the subscription requirement

## Constraints

- **Minimal changes**: Bypass only — don't refactor or remove Patreon infrastructure
- **Build toolchain**: Requires theos SDK for iOS tweak compilation
- **No testing on device yet**: Build environment needs to be set up first

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Bypass approach over full removal | Minimal code changes, less risk of breaking things, easier to maintain | -- Pending |
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
