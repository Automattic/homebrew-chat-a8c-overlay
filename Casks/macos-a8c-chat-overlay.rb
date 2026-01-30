cask "macos-a8c-chat-overlay" do
  version "0.0.20"
  sha256 "8ea0bb6d3101748bb6d3169cc0f45ee0eac412dd00bac53c0e462b99a1a83b88"

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
