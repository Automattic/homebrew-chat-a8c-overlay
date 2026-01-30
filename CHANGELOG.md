# Changelog

All notable changes to LibreChat A8C Overlay will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.0.20] - 2025-01-30

### Added

- **Reset Window Size**: New menu item to reset the overlay window to its default size (550x580) and center it on screen. Useful when the window edges are off-screen and cannot be grabbed to resize.

- **Generic Error Page**: When navigation fails (e.g., proxy disconnected, network issues), a custom error page is now shown with a "Try Again" button. The error page displays the specific error code and description, with a helpful tip about the Automattic proxy.

- **File Download Support (WIP)**: Added infrastructure for handling blob URL downloads (e.g., "Download as PNG" feature). JSON exports work; PNG downloads still have issues with blob URL timing that need further investigation.

### Changed

- **Mission Control Behavior**: The overlay now participates in Mission Control animations like a regular macOS window. Previously it stayed fixed while other windows moved during Mission Control gestures (four-finger swipe up).

### Known Issues

- PNG/image downloads from LibreChat's export feature don't work yet due to blob URL revocation timing. The blob URL is revoked before the app can fetch the data. JSON exports work correctly.

---

## [0.0.19] - 2025-01-16

### Added

- **Accessibility Permission Prompt**: The app now detects when Accessibility permissions are missing and shows a helpful dialog guiding users to System Settings. Once permissions are granted, it automatically prompts to restart the app.

- **External Links Open in Browser**: Clicking links to external websites (anything outside chat.a8c.com) now opens them in your default browser instead of navigating within the overlay.

- **Direct Download Option**: You can now download the app directly from GitHub Releases without needing Homebrew.

### Changed

- **New App Name**: Renamed from "macos-a8c-chat-overlay" to "LibreChat A8C Overlay" for better branding.

- **New Menu Bar Icon**: Updated to use the LibreChat flame logo. The icon now automatically adapts to light and dark menu bar appearances using macOS template image system.

- **New Bundle Identifier**: Changed from `com.github-tchlux.macosa8c-chatoverlay` to `com.automattic.librechat-a8c-overlay` for proper Automattic branding.

- **Improved README**: Completely rewritten installation instructions with step-by-step guides for both direct download and Homebrew methods.

### Fixed

- **Cleaned Up Debug Code**: Removed debug print statements that were accidentally left in the codebase.

- **Removed Unused Imports**: Cleaned up unnecessary imports in listener.py.

### Important Notes for Existing Users

Due to the bundle identifier change, existing users will need to:

1. **Re-grant Accessibility permissions** - macOS will treat this as a new app
2. **Window position will reset** - Your saved window position/size will return to default

Custom keyboard shortcuts saved in `~/Library/Logs/macos-a8c-chat-overlay/custom_trigger.json` will be preserved.

---

## [0.0.18] - 2025-01-12

### Added

- Detailed installation instructions with screenshots and GIFs
- Visual guides for security and accessibility permission setup

### Changed

- Updated README with comprehensive step-by-step installation guide

---

## [0.0.17] - 2025-01-10

### Added

- Custom keyboard shortcut support via "Set New Trigger" menu option
- Autolauncher installation/uninstallation via menu bar
- Window position and size persistence across app restarts

### Changed

- Improved menu bar icon visibility

---

## [0.0.16] - 2025-01-08

### Fixed

- Fixed compatibility issues with macOS Tahoe
- Resolved window focus handling

---

## [0.0.15] - 2025-01-05

### Added

- Initial public release
- Dedicated floating window for chat.a8c.com
- Control+Space global keyboard shortcut
- Menu bar icon with Show/Hide/Quit options
- Universal binary support (Intel and Apple Silicon)
- Homebrew cask installation support

---

## [0.0.1 - 0.0.14] - 2025-01-01 to 2025-01-04

### Development

- Initial development and internal testing
- Core functionality implementation
- Build system setup with py2app
- Code signing and notarization workflow

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 0.0.20 | 2025-01-30 | Reset window size, error page, Mission Control fix |
| 0.0.19 | 2025-01-16 | Rebranding, new icon, accessibility prompt, external links |
| 0.0.18 | 2025-01-12 | Documentation improvements |
| 0.0.17 | 2025-01-10 | Custom shortcuts, autolauncher |
| 0.0.16 | 2025-01-08 | macOS Tahoe compatibility |
| 0.0.15 | 2025-01-05 | Initial public release |

---

## Upgrade Guide

### From 0.0.18 or earlier to 0.0.19

This version includes significant changes. After upgrading:

1. **Grant Accessibility permissions again**
   - Go to System Settings > Privacy & Security > Accessibility
   - Enable "LibreChat A8C Overlay"
   - The app will prompt you to restart

2. **Window position will reset**
   - Resize and position the window as desired
   - The new position will be saved automatically

3. **Your custom shortcut is preserved**
   - If you set a custom trigger, it will still work after the restart
