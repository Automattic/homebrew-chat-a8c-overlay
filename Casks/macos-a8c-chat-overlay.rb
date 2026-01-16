cask "macos-a8c-chat-overlay" do
  version "0.0.19"
  sha256 "ab2868c09cbe0eb23e422b94a8d6884ecafc9fcdb0e9d92e76e9556714d56838"

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
