# Homebrew Tap Setup Guide

## For Maintainers: Setting Up the Tap

### 1. Create the Tap Repository

Create a new repository on GitHub:
- **Organization**: Automattic
- **Name**: `homebrew-tap` (must start with "homebrew-")
- **Visibility**: Public (required for Homebrew)

### 2. Initialize the Tap Structure

```bash
# Clone the new repo
git clone https://github.com/Automattic/homebrew-tap.git
cd homebrew-tap

# Create the Casks directory
mkdir -p Casks

# Copy the cask formula
cp path/to/macos-a8c-chat-overlay.rb Casks/

# Create README
cat > README.md << 'EOF'
# Automattic Homebrew Tap

Internal Homebrew tap for Automattic tools.

## Available Casks

- **macos-a8c-chat-overlay**: macOS overlay for chat.a8c.com with Control+Space hotkey

## Installation

```bash
# Add the tap
brew tap automattic/tap

# Install the app
brew install --cask macos-a8c-chat-overlay
```

## Updating

```bash
brew upgrade --cask macos-a8c-chat-overlay
```
EOF

# Commit and push
git add .
git commit -m "Initial tap setup with macos-a8c-chat-overlay cask"
git push
```

### 3. Create a Release

Every time you want to distribute a new version:

```bash
# In the macos-a8c-chat-overlay project directory
cd dmg-builder/dist

# Create a zip file for distribution
ditto -c -k --keepParent macos-a8c-chat-overlay.app macos-a8c-chat-overlay.zip

# Calculate SHA256 (you'll need this)
shasum -a 256 macos-a8c-chat-overlay.zip

# Example output:
# abc123def456... macos-a8c-chat-overlay.zip
```

Then on GitHub:
1. Go to https://github.com/Automattic/macos-a8c-chat-overlay
2. Click "Releases" → "Create a new release"
3. Tag: `v0.0.18` (must match version in cask)
4. Title: `v0.0.18`
5. Upload `macos-a8c-chat-overlay.zip`
6. Publish release

### 4. Update the Cask Formula

After creating the release, update the cask with the real SHA256:

```ruby
cask "macos-a8c-chat-overlay" do
  version "0.0.18"
  sha256 "abc123def456..."  # Replace with actual SHA256 from step 3
  # ... rest of file
end
```

Commit and push to the homebrew-tap repo.

---

## For Users: Installing the App

### One-Time Setup

```bash
# Add the Automattic tap
brew tap automattic/tap
```

### Install the App

```bash
# Install
brew install --cask macos-a8c-chat-overlay

# The app will open automatically
# Grant Accessibility permissions when prompted
```

### Enable Auto-Start (Optional)

If the app doesn't auto-configure startup, run:

```bash
/Applications/macos-a8c-chat-overlay.app/Contents/MacOS/macos-a8c-chat-overlay --install-startup
```

### Usage

- Press **Control+Space** to show/hide the chat window
- Click the menu bar icon for options
- The app runs in the background after installation

### Updating

```bash
# Check for updates
brew update

# Upgrade to latest version
brew upgrade --cask macos-a8c-chat-overlay
```

### Uninstalling

```bash
# Uninstall the app
brew uninstall --cask macos-a8c-chat-overlay

# Optional: Remove all data
brew uninstall --cask --zap macos-a8c-chat-overlay
```

---

## Version Management

### Releasing a New Version

1. **Update version in `setup.py`**:
   ```python
   version = "0.0.19"
   ```

2. **Build the app**:
   ```bash
   cd dmg-builder
   ./test_build.sh
   ```

3. **Package for release**:
   ```bash
   cd dist
   ditto -c -k --keepParent macos-a8c-chat-overlay.app macos-a8c-chat-overlay.zip
   shasum -a 256 macos-a8c-chat-overlay.zip
   ```

4. **Create GitHub release** with the zip file

5. **Update cask formula** in homebrew-tap:
   - Update `version "0.0.19"`
   - Update `sha256 "..."`
   - Commit and push

6. **Users update** with:
   ```bash
   brew upgrade --cask macos-a8c-chat-overlay
   ```

---

## Troubleshooting

### "App is damaged and can't be opened"

This happens because the app isn't notarized. Users can bypass with:

```bash
xattr -cr /Applications/macos-a8c-chat-overlay.app
```

Or in the cask, add this to handle it automatically:

```ruby
postflight do
  system_command "xattr",
                 args: ["-cr", "#{appdir}/macos-a8c-chat-overlay.app"]
end
```

### Accessibility Permissions

Users must manually grant Accessibility permissions in:
**System Preferences → Security & Privacy → Accessibility**

Add `macos-a8c-chat-overlay.app` to the list.

---

## Quick Reference

### Maintainer Commands
```bash
# Build
cd dmg-builder && ./test_build.sh

# Package
cd dist && ditto -c -k --keepParent macos-a8c-chat-overlay.app macos-a8c-chat-overlay.zip

# Get SHA256
shasum -a 256 macos-a8c-chat-overlay.zip
```

### User Commands
```bash
# Install
brew tap automattic/tap
brew install --cask macos-a8c-chat-overlay

# Update
brew upgrade --cask macos-a8c-chat-overlay

# Uninstall
brew uninstall --cask macos-a8c-chat-overlay
```
