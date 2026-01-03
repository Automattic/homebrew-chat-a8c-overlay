# Complete GitHub Setup Guide for Homebrew Distribution

This guide will walk you through setting up your Homebrew tap from scratch, assuming you're new to this process.

---

## 📚 Background: What We're Building

**Goal**: Let Automattic employees install your app with one simple command:
```bash
brew tap automattic/chat-a8c-overlay
brew install --cask macos-a8c-chat-overlay
```

**What is Homebrew?**
- It's a package manager for macOS (like an App Store for developers)
- Instead of downloading .dmg files manually, users type one command to install

**What is a "tap"?**
- A "tap" is a custom Homebrew repository
- Think of it as your own private app store
- Official apps use the main Homebrew repo, but internal tools use taps

**What is a "cask"?**
- A cask is a formula for installing GUI applications (apps with windows/icons)
- It's basically a recipe that tells Homebrew: "Download this .zip, extract this .app, put it in /Applications"

---

## 🎯 Overview: What We'll Do

1. **Create ONE GitHub repository** that contains:
   - Your source code
   - The Homebrew cask formula
   - Release files (.zip) for users to download

2. **Package your app** into a .zip file

3. **Create a GitHub Release** with the .zip file

4. **Test the installation** to make sure it works

---

## PART 1: Create the GitHub Repository

### Step 1: Go to GitHub

Open your browser and go to:
```
https://github.com/organizations/Automattic/repositories/new
```

Or navigate manually:
1. Go to https://github.com/Automattic
2. Click the green "New" button

### Step 2: Fill Out the Form

Here's what to enter in each field:

**Repository name:**
```
homebrew-chat-a8c-overlay
```
**Why this name?** Homebrew requires tap repositories to start with `homebrew-`. The part after `homebrew-` becomes the tap name. So `homebrew-chat-a8c-overlay` creates a tap called `chat-a8c-overlay`.

**Description:**
```
macOS overlay application for chat.a8c.com with Control+Space hotkey
```
**Why?** This shows up on GitHub and helps people understand what this repo is for.

**Public or Private:**
- ✅ Choose **Public**

**Why Public?** Homebrew only works with public repositories. Don't worry - this is fine for internal tools. Only Automattic employees will know about it, and the code isn't sensitive.

**Initialize repository:**
- ✅ Check "Add a README file"
- ✅ Add .gitignore: Choose **Python**
- ✅ Choose a license: **MIT License** (or whatever Automattic prefers)

**Why add README?** Makes it easier to clone immediately.
**Why .gitignore?** Prevents accidentally committing build files and Python cache.

### Step 3: Create Repository

Click the green **"Create repository"** button.

✅ Your repo is now live at: `https://github.com/Automattic/homebrew-chat-a8c-overlay`

---

## PART 2: Package Your App

Now we'll create the .zip file that users will download.

### Step 1: Open Terminal

Navigate to your project:
```bash
cd /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/dmg-builder
```

### Step 2: Run the Package Script

```bash
./package_release.sh
```

**What this does:**
1. Finds your built .app in `dist/`
2. Creates a .zip file: `dist/macos-a8c-chat-overlay.zip`
3. Calculates the SHA256 hash (a unique fingerprint for security)

You'll see output like:
```
✅ Package created successfully!

📍 Location: dmg-builder/dist/macos-a8c-chat-overlay.zip

🔐 SHA256:
abc123def456...  dist/macos-a8c-chat-overlay.zip
```

**IMPORTANT:** Copy that SHA256 hash (the long string like `abc123def456...`). You'll need it later!

---

## PART 3: Upload Your Code to GitHub

### Option A: Using GitHub Web Interface (Easiest for Beginners)

#### Step 1: Prepare Your Files

Create a folder on your Desktop called `homebrew-upload` and copy these files:

```bash
# Create a temporary folder
mkdir ~/Desktop/homebrew-upload
cd ~/Desktop/homebrew-upload

# Copy the source code
cp -r /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/macos_a8c_chat_overlay .
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/*.py .
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/*.md .
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/*.txt .
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/MANIFEST.in .

# Create Casks directory
mkdir Casks
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/macos-a8c-chat-overlay.rb Casks/

# Copy build scripts
cp -r /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/dmg-builder .

# Copy setup guides
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/HOMEBREW_SETUP.md .
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/GITHUB_SETUP_GUIDE.md .
```

#### Step 2: Upload to GitHub

1. Go to your repository: https://github.com/Automattic/homebrew-chat-a8c-overlay
2. Click "Add file" → "Upload files"
3. Drag all the files from `~/Desktop/homebrew-upload` into the upload area
4. In "Commit changes" box at the bottom:
   - **Title**: `Initial commit - macOS A8C Chat Overlay`
   - **Description**: `Added source code, Homebrew cask, and build scripts`
5. Click **"Commit changes"**

### Option B: Using Git (If You're Comfortable with Git)

```bash
# Clone the repo
cd ~/Desktop
git clone https://github.com/Automattic/homebrew-chat-a8c-overlay.git
cd homebrew-chat-a8c-overlay

# Copy all files
cp -r /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/macos_a8c_chat_overlay .
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/*.py .
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/*.md .
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/*.txt .
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/MANIFEST.in .

# Create Casks directory and copy formula
mkdir Casks
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/macos-a8c-chat-overlay.rb Casks/

# Copy build scripts
cp -r /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/dmg-builder .

# Copy guides
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/HOMEBREW_SETUP.md .
cp /Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/GITHUB_SETUP_GUIDE.md .

# Commit and push
git add .
git commit -m "Initial commit - macOS A8C Chat Overlay"
git push origin main
```

---

## PART 4: Create a GitHub Release

This is where you upload the .zip file for users to download.

### Step 1: Go to Releases

1. Go to: https://github.com/Automattic/homebrew-chat-a8c-overlay
2. Click **"Releases"** (in the right sidebar)
3. Click **"Create a new release"**

### Step 2: Fill Out the Release Form

**Choose a tag:**
- Click "Choose a tag" dropdown
- Type: `v0.0.18`
- Click "Create new tag: v0.0.18 on publish"

**Why?** This creates a version number. The `v` prefix is standard for releases.

**Release title:**
```
v0.0.18 - Initial Release
```

**Description:**
```
## What's New

Initial release of macOS A8C Chat Overlay for Automattic employees.

### Features
- Overlay window for chat.a8c.com
- Control+Space keyboard shortcut to show/hide
- Menu bar icon for quick access
- Auto-saves window position

### Installation

```bash
brew tap automattic/chat-a8c-overlay
brew install --cask macos-a8c-chat-overlay
```

### System Requirements
- macOS 10.15 (Catalina) or later
- Works on both Intel and Apple Silicon Macs
```

**Attach files:**
1. Click **"Attach binaries by dropping them here or selecting them"**
2. Navigate to: `/Users/ricardoramos/Claude-Anthropic/macos-chat-A8C-overlay-main/dmg-builder/dist/`
3. Select `macos-a8c-chat-overlay.zip`
4. Upload it

**Set as the latest release:**
- ✅ Check "Set as the latest release"

### Step 3: Publish

Click the green **"Publish release"** button.

✅ Your release is now live! The .zip file is available at:
```
https://github.com/Automattic/homebrew-chat-a8c-overlay/releases/download/v0.0.18/macos-a8c-chat-overlay.zip
```

---

## PART 5: Update the Cask with SHA256

Remember that SHA256 hash from earlier? Now we'll add it to the cask formula.

### Step 1: Edit the Cask File

1. Go to: https://github.com/Automattic/homebrew-chat-a8c-overlay
2. Navigate to: **Casks/macos-a8c-chat-overlay.rb**
3. Click the **pencil icon** (✏️) to edit

### Step 2: Replace SHA256

Find this line:
```ruby
sha256 :no_check  # For initial testing; replace with actual SHA256 after first release
```

Replace it with (use YOUR hash from the package script):
```ruby
sha256 "abc123def456..."  # Replace abc123def456... with your actual SHA256
```

**Example:** If your SHA256 was `a1b2c3d4e5f6...`, you'd write:
```ruby
sha256 "a1b2c3d4e5f6..."
```

### Step 3: Commit the Change

Scroll down to "Commit changes":
- **Title**: `Update SHA256 for v0.0.18 release`
- **Description**: (leave blank or add notes)
- Click **"Commit changes"**

**Why do this?** The SHA256 is a security check. When users install, Homebrew verifies the downloaded file matches this hash. This prevents corrupted or tampered downloads.

---

## PART 6: Test the Installation

Now let's test if it works!

### Step 1: Add the Tap

Open Terminal and run:
```bash
brew tap automattic/chat-a8c-overlay
```

**What this does:** Tells Homebrew "Hey, there's a custom app repository at github.com/Automattic/homebrew-chat-a8c-overlay"

**Why `automattic/chat-a8c-overlay`?** Homebrew automatically drops the `homebrew-` prefix. So `homebrew-chat-a8c-overlay` becomes `chat-a8c-overlay`.

You should see:
```
==> Tapping automattic/chat-a8c-overlay
Cloning into '/usr/local/Homebrew/Library/Taps/automattic/homebrew-chat-a8c-overlay'...
Tapped 1 cask (13 files, 123KB).
```

### Step 2: Install the App

```bash
brew install --cask macos-a8c-chat-overlay
```

**What this does:**
1. Downloads `macos-a8c-chat-overlay.zip` from GitHub
2. Verifies the SHA256 matches
3. Extracts the .app
4. Moves it to `/Applications/`
5. Runs any post-installation steps

You should see:
```
==> Downloading https://github.com/Automattic/homebrew-chat-a8c-overlay/releases/download/v0.0.18/macos-a8c-chat-overlay.zip
==> Installing Cask macos-a8c-chat-overlay
==> Moving App 'macos-a8c-chat-overlay.app' to '/Applications/macos-a8c-chat-overlay.app'
🍺  macos-a8c-chat-overlay was successfully installed!
```

### Step 3: Grant Permissions

1. The app should open automatically
2. macOS will ask for **Accessibility permissions**
3. Click "Open System Preferences"
4. Click the lock icon and enter your password
5. Check the box next to `macos-a8c-chat-overlay`

### Step 4: Test It!

Press **Control+Space** - the chat window should appear!

---

## 🎉 Success! What's Next?

### For Automattic Employees

Share these instructions with your team:

```markdown
## Install A8C Chat Overlay

1. Open Terminal
2. Run these commands:

```bash
brew tap automattic/chat-a8c-overlay
brew install --cask macos-a8c-chat-overlay
```

3. Grant Accessibility permissions when prompted
4. Press Control+Space to show/hide the chat!

### Update to latest version:
```bash
brew upgrade --cask macos-a8c-chat-overlay
```
```

### For Future Updates

When you make changes and want to release a new version:

1. **Update version in `setup.py`**:
   ```python
   version = "0.0.19"
   ```

2. **Build and package**:
   ```bash
   cd dmg-builder
   ./test_build.sh
   ./package_release.sh
   ```

3. **Create new GitHub release**:
   - Tag: `v0.0.19`
   - Upload new .zip
   - Copy new SHA256

4. **Update cask formula**:
   - Update version: `version "0.0.19"`
   - Update SHA256 with new hash
   - Commit changes

5. **Users update with**:
   ```bash
   brew upgrade --cask macos-a8c-chat-overlay
   ```

---

## 🐛 Troubleshooting

### "App is damaged and can't be opened"

This happens because the app isn't notarized with Apple. Users can fix it with:

```bash
xattr -cr /Applications/macos-a8c-chat-overlay.app
```

Then try opening again.

### Can't find the tap

Make sure the repo name is exactly `homebrew-chat-a8c-overlay` (with the `homebrew-` prefix).

### Wrong SHA256 error

Re-run `./package_release.sh` to get the correct hash, then update the cask formula.

---

## 📝 Summary

**What you created:**
- ✅ GitHub repository: `Automattic/homebrew-chat-a8c-overlay`
- ✅ Homebrew cask formula in `Casks/macos-a8c-chat-overlay.rb`
- ✅ Release with .zip file at `v0.0.18`
- ✅ Working installation for ~200 employees

**Users install with:**
```bash
brew tap automattic/chat-a8c-overlay
brew install --cask macos-a8c-chat-overlay
```

**You update by:**
1. Change version in code
2. Build & package
3. Create new release
4. Update cask SHA256
