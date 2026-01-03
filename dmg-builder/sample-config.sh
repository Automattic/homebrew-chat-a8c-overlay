# Read in the TEAM_ID
echo "Generate a certificate by requesting a new authorized cert from KeychainAccess app on local machine."
echo ""
echo "Pick a 'Developer ID Application' and upload the locally generated request here:"
echo "  https://developer.apple.com/account/resources/certificates/list"
echo ""
echo "Then enter the 10-character team ID alphanumeric string."
read TEAM_ID
TEAM_ID="${TEAM_ID:-ABCDE12345}"
# App specific passwords can be generated at:
#  https://account.apple.com/account/manage
APP_SPECIFIC="abcd-efgh-ijkl-mnop"
# Your developer Apple ID email
APPLE_ID="your.email@domain.com"
# Developer name and team ID comes from developer certificate
DEV_NAME="Your Name"
# Signature should look like this for a "Developer ID Application"
SIGNATURE="Developer ID Application: $DEV_NAME ($TEAM_ID)"
# Profile name is arbitrary
KEYCHAIN_PROFILE="macos-2025"
# The name of the app
APP_NAME="macos-a8c-chat-overlay"
