cask "macos-a8c-chat-overlay" do
  version "0.0.18"
  sha256 "0fe7c51c8bd15b0c33668965c9998ea8c44c743336f399be3f9cbee843d0a977"

  url "https://github.com/Automattic/homebrew-chat-a8c-overlay/releases/download/v#{version}/macos-a8c-chat-overlay.zip"
  name "A8C Chat Overlay"
  desc "macOS overlay application for chat.a8c.com with Control+Space hotkey"
  homepage "https://github.com/Automattic/homebrew-chat-a8c-overlay"

  # Requires macOS 10.15 or later (based on universal2 build)
  depends_on macos: ">= :catalina"

  app "macos-a8c-chat-overlay.app"

  # Optional: Auto-enable accessibility and install startup item
  postflight do
    system_command "open",
                   args: ["-a", "#{appdir}/macos-a8c-chat-overlay.app"]
  end

  # Clean up on uninstall
  uninstall quit: "com.github-tchlux.macosa8c-chatoverlay",
            launchctl: "com.github-tchlux.macosa8c-chatoverlay"

  zap trash: [
    "~/Library/Logs/macos-a8c-chat-overlay",
    "~/Library/Preferences/com.github-tchlux.macosa8c-chatoverlay.plist",
  ]
end
