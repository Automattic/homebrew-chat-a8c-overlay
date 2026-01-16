# LibreChat A8C Overlay

A macOS overlay application for pinning `chat.a8c.com` to a dedicated window with a customizable global keyboard shortcut.

![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![Architecture](https://img.shields.io/badge/architecture-universal%20(arm64%20%7C%20x86__64)-blue)
![Version](https://img.shields.io/badge/version-0.0.19-green)

---

<p align="center">
  <a href="https://github.com/Automattic/homebrew-chat-a8c-overlay/releases/latest/download/LibreChat-A8C-Overlay.zip">
    <img src="https://img.shields.io/badge/Download-LibreChat%20A8C%20Overlay-blue?style=for-the-badge&logo=apple&logoColor=white" alt="Download LibreChat A8C Overlay" height="60">
  </a>
</p>

<p align="center">
  <strong>macOS 10.15+ &bull; Universal Binary (Intel & Apple Silicon)</strong><br>
  <sub>Click the button above to download the latest version</sub>
</p>

---

## Features

- Dedicated floating window for chat.a8c.com
- **Control+Space** global keyboard shortcut to show/hide (customizable)
- Menu bar icon for quick access
- Automatically saves window position and size
- External links open in your default browser
- Light/Dark mode adaptive menu bar icon
- Universal binary (supports both Intel and Apple Silicon)
- Auto-prompts for restart after granting Accessibility permissions

---

## Installation

Choose one of the following methods:

### Method 1: Direct Download (Recommended for most users)

This is the easiest way to install if you don't have Homebrew or prefer not to use the Terminal.

#### Step 1: Download the App

Click the download button above, or [click here to download](https://github.com/Automattic/homebrew-chat-a8c-overlay/releases/latest/download/LibreChat-A8C-Overlay.zip).

#### Step 2: Extract and Move to Applications

1. Open your **Downloads** folder
2. Double-click `LibreChat-A8C-Overlay.zip` to extract it
3. Drag `LibreChat A8C Overlay.app` to your **Applications** folder

<!-- TODO: Add screenshot showing drag to Applications -->

#### Step 3: Open the App (First Time Security Prompt)

Since the app is not from the Mac App Store, macOS will show a security warning the first time you open it.

1. Double-click `LibreChat A8C Overlay.app` in your Applications folder
2. You'll see a message saying the app "cannot be opened because the developer cannot be verified"
3. Click **Cancel** (don't click "Move to Trash")

<!-- TODO: Add screenshot of security warning -->

#### Step 4: Allow the App in Security Settings

1. Open **System Settings** (or System Preferences on older macOS)
2. Go to **Privacy & Security**
3. Scroll down to the **Security** section
4. You'll see a message about "LibreChat A8C Overlay" being blocked
5. Click **Open Anyway**
6. Enter your password or use Touch ID when prompted
7. Click **Open** in the confirmation dialog

<!-- TODO: Add gif showing Security settings flow -->

#### Step 5: Grant Accessibility Permissions

The app needs Accessibility permissions to detect your keyboard shortcut. When you first open the app:

1. A dialog will appear explaining that Accessibility permissions are required
2. Click **Open System Settings**
3. In the Accessibility list, find **LibreChat A8C Overlay**
4. Toggle the switch **ON** to enable it
5. The app will detect the permission change and prompt you to restart
6. Click **Restart Now**

<!-- TODO: Add gif showing Accessibility permission flow -->

#### Step 6: Login with Your Credentials

After the app restarts, you'll see the chat.a8c.com login page. Enter your Matticspace credentials to log in.

<!-- Reuse existing screenshot -->
![Login Screen](https://github.com/user-attachments/assets/b322b0f9-0682-4ddf-993d-6ad55b3bb7bb)

#### Step 7: You're Done!

Press **Control+Space** anywhere on your Mac to show or hide the chat overlay.

---

### Method 2: Using Homebrew

For users comfortable with the Terminal, Homebrew provides automatic updates.

#### Step 1: Install via Homebrew

Open Terminal and run the following commands:

```bash
# Add the tap (only needed once)
brew tap automattic/chat-a8c-overlay

# Install the app
brew install --cask macos-a8c-chat-overlay
```

After running these commands, it should look something like this:

<img width="608" height="396" alt="Homebrew installation" src="https://github.com/user-attachments/assets/bc8d07e1-f52b-4fc5-b84b-82b70d5a04a8" />

#### Step 2: Handle the Security Warning

The app will try to open automatically, but macOS will block it:

<img width="304" height="341" alt="Security warning" src="https://github.com/user-attachments/assets/beedeb13-2f58-42d0-ab37-92a868a72b40" />

1. Open **System Settings > Privacy & Security**
2. Scroll down to the **Security** section
3. Click **Open Anyway** next to the LibreChat A8C Overlay message
4. Authenticate with Touch ID or your password

![Security settings flow](https://github.com/user-attachments/assets/f3a4b427-7ad5-423f-8d0e-c5e32234dd03)

#### Step 3: Grant Accessibility Permissions

When the app opens, it will prompt you to grant Accessibility permissions:

1. Click **Open System Settings** in the dialog
2. Toggle **ON** the switch for LibreChat A8C Overlay
3. The app will detect this and prompt you to restart
4. Click **Restart Now**

![Accessibility permissions](https://github.com/user-attachments/assets/2048915a-1892-499d-beb4-63ea30d92341)

#### Step 4: Login and Use

Enter your Matticspace credentials and you're ready to go!

---

## Usage

| Action | How |
|--------|-----|
| **Show/Hide Window** | Press `Control+Space` anywhere |
| **Access Menu** | Click the flame icon in the menu bar |
| **Set Custom Shortcut** | Menu bar > Set New Trigger |
| **Auto-Start at Login** | Menu bar > Install Autolauncher |
| **Quit the App** | Menu bar > Quit |

### Customizing the Keyboard Shortcut

Don't like Control+Space? You can set your own shortcut:

1. Click the menu bar icon
2. Select **Set New Trigger**
3. Press your desired key combination (e.g., `Command+Shift+C`)
4. The new shortcut is saved automatically

---

## Updating

### If you installed via Direct Download:

1. Download the latest version from the button at the top of this page
2. Replace the old app in your Applications folder with the new one
3. Re-grant Accessibility permissions if prompted

### If you installed via Homebrew:

```bash
brew upgrade --cask macos-a8c-chat-overlay
```

---

## Uninstalling

### If you installed via Direct Download:

1. Quit the app from the menu bar
2. Drag `LibreChat A8C Overlay.app` from Applications to the Trash
3. Optionally, remove preferences:
   ```bash
   rm -rf ~/Library/Logs/macos-a8c-chat-overlay
   rm -f ~/Library/Preferences/com.automattic.librechat-a8c-overlay.plist
   ```

### If you installed via Homebrew:

```bash
# Standard uninstall
brew uninstall --cask macos-a8c-chat-overlay

# Complete removal (including preferences and logs)
brew uninstall --cask --zap macos-a8c-chat-overlay
```

---

## System Requirements

- macOS 10.15 (Catalina) or later
- Works only while connected to Automattic's proxy/VPN

---

## Troubleshooting

### "App is damaged and can't be opened"

This can happen if the download was interrupted or the app wasn't properly signed. Try:

```bash
xattr -cr /Applications/LibreChat\ A8C\ Overlay.app
```

Then try opening the app again.

### Control+Space (or custom shortcut) isn't working

1. **Check Accessibility permissions:**
   - Go to System Settings > Privacy & Security > Accessibility
   - Make sure LibreChat A8C Overlay is in the list and **enabled**

2. **Try removing and re-adding the permission:**
   - Click the `-` button to remove the app
   - Click the `+` button and add it again from Applications
   - Restart the app

3. **Restart the app:**
   - Quit from the menu bar
   - Open the app again

4. **Check for conflicts:**
   - Another app might be using the same shortcut
   - Try setting a different shortcut via Menu bar > Set New Trigger

### The app doesn't appear in the menu bar

1. Check if the app is running in Activity Monitor
2. Try quitting and reopening the app
3. Make sure you're not in full-screen mode (some full-screen apps hide menu bar icons)

### Login page doesn't load

1. Make sure you're connected to Automattic's proxy/VPN
2. Try refreshing: Menu bar > Show, then close and reopen

---

## Building from Source

For developers who want to build from source:

```bash
git clone https://github.com/Automattic/homebrew-chat-a8c-overlay.git
cd homebrew-chat-a8c-overlay/dmg-builder
./test_build.sh
```

The built `.app` will be in `dmg-builder/dist/`.

---

## Credits

- Based on [macos-grok-overlay](https://github.com/tchlux/macos-grok-overlay) by tchlux
- Uses the [LibreChat](https://github.com/danny-avila/LibreChat) flame logo

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes in each version.
