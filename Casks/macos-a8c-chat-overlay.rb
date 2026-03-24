cask "macos-a8c-chat-overlay" do
  version "0.0.22"
  sha256 "d3c9207850182559ad63513d1ba09acbc3e108d6b631c97606571166545c200b"

  url "https://github.com/Automattic/homebrew-chat-a8c-overlay/releases/download/v#{version}/LibreChat-A8C-Overlay.zip"
  name "LibreChat A8C Overlay"
  desc "macOS overlay application for chat.a8c.com with customizable hotkey"
  homepage "https://github.com/Automattic/homebrew-chat-a8c-overlay"

  # Requires macOS 10.15 or later (based on universal2 build)
  depends_on macos: ">= :catalina"

  app "LibreChat A8C Overlay.app"

  # Launch app after installation
  postflight do
    system_command "open",
                   args: ["-a", "#{appdir}/LibreChat A8C Overlay.app"]
  end

  # Clean up on uninstall
  uninstall quit: "com.automattic.librechat-a8c-overlay",
            launchctl: "com.automattic.librechat-a8c-overlay"

  zap trash: [
    "~/Library/Logs/macos-a8c-chat-overlay",
    "~/Library/Preferences/com.automattic.librechat-a8c-overlay.plist",
  ]
end
