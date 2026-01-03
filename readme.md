# macOS A8C Chat Overlay

A macOS overlay application for pinning `chat.a8c.com` to a dedicated window with a global keyboard shortcut.

![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![Architecture](https://img.shields.io/badge/architecture-universal%20(arm64%20%7C%20x86__64)-blue)

## Features

- 🪟 Dedicated window for chat.a8c.com
- ⌨️ **Control+Space** global keyboard shortcut to show/hide
- 📍 Menu bar icon for quick access
- 💾 Automatically saves window position and size
- 🔄 Universal binary (supports both Intel and Apple Silicon)

## Installation

### Using Homebrew (Recommended)

```bash
# Add the tap
brew tap automattic/chat-a8c-overlay

# Install the app
brew install --cask macos-a8c-chat-overlay
```

### First Launch

1. The app will open automatically after installation
2. Grant **Accessibility permissions** when prompted (required for Control+Space hotkey)
3. Log in to chat.a8c.com

## Usage

- **Show/Hide Window**: Press `Control+Space` at any time
- **Menu Bar**: Click the menu bar icon for Show, Hide, or Quit options
- **Auto-Start**: Configure via menu bar options to launch at login

## Updating

```bash
brew upgrade --cask macos-a8c-chat-overlay
```

## Uninstalling

```bash
# Standard uninstall
brew uninstall --cask macos-a8c-chat-overlay

# Complete removal (including preferences and logs)
brew uninstall --cask --zap macos-a8c-chat-overlay
```

## System Requirements

- macOS 10.15 (Catalina) or later
- Compatible with both Intel and Apple Silicon Macs

## Troubleshooting

### "App is damaged and can't be opened"

Remove the quarantine attribute:

```bash
xattr -cr /Applications/macos-a8c-chat-overlay.app
```

### Accessibility Permissions

If the Control+Space hotkey isn't working:

1. System Preferences → Security & Privacy → Accessibility
2. Ensure `macos-a8c-chat-overlay.app` is in the list and checked
3. If issues persist, remove and re-add the app

## Building from Source

```bash
git clone https://github.com/Automattic/homebrew-chat-a8c-overlay.git
cd homebrew-chat-a8c-overlay/dmg-builder
./test_build.sh
```

The built .app will be in `dmg-builder/dist/`.

## Credits

Adapted from [macos-grok-overlay](https://github.com/tchlux/macos-grok-overlay) for use with Automattic's A8C Chat.
