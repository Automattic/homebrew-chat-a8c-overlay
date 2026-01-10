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

#### 1. Open your Terminal and Run the following commands (brew might autoupdate itself, that's normal)

```bash
# Add the tap
brew tap automattic/chat-a8c-overlay

# Install the app
brew install --cask macos-a8c-chat-overlay
```
#### After you ran them it should look something like this
<img width="608" height="396" alt="Screenshot 2026-01-10 at 3 30 35 a m" src="https://github.com/user-attachments/assets/bc8d07e1-f52b-4fc5-b84b-82b70d5a04a8" />


#### 2. The app will try to open automatically after installation, but **will be flagged by the OS security**, this is normal.
<img width="304" height="341" alt="Screenshot 2026-01-10 at 3 30 57 a m" src="https://github.com/user-attachments/assets/beedeb13-2f58-42d0-ab37-92a868a72b40" />



#### 3. Open **Settings > Privacy & Security > Scroll down to the bottom under the "Security" section** and click "Open anyway" twice. (You'll be asked to authenticate via Touch ID)
![ScreenRecording22026-01-10at3 33 48a m -ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/f3a4b427-7ad5-423f-8d0e-c5e32234dd03)



#### 4. Once the app is running you'll be prompted to input your matticspace credentials
![ScreenRecording32026-01-10at3 33 48a m -ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/b322b0f9-0682-4ddf-993d-6ad55b3bb7bb)



#### 5. Next you have to grant **Accessibility permissions** when prompted (required for Control+Space hotkey)
![ScreenRecording42026-01-10at3 37 41a m -ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/2048915a-1892-499d-beb4-63ea30d92341)



#### 6. Once you've granted the **Accessibility permissions**, close the app from the menu bar, and re-open it from your applications folder.
![ScreenRecording2026-01-10at3 39 47a m -ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/d0a993e2-b021-4b76-bc4f-462d2688eb44)



#### 7. After following these instructions, the app will be correctly installed and the keyboard shorcut should now work.  





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
- Homebrew already installed
- Works only while proxied

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

## Other installation methods – Building from Source

```bash
git clone https://github.com/Automattic/homebrew-chat-a8c-overlay.git
cd homebrew-chat-a8c-overlay/dmg-builder
./test_build.sh
```

The built .app will be in `dmg-builder/dist/`.

## Credits

Adapted from [macos-grok-overlay](https://github.com/tchlux/macos-grok-overlay) for use with Automattic's A8C Chat.
