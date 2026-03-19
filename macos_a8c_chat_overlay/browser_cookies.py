"""
Read cookies from the user's default browser for SSO authentication.

Supports Firefox (plaintext) and Chrome/Chromium variants (AES-encrypted).
Safari cookies are not accessible on macOS Tahoe+.
"""

import ctypes
import ctypes.util
import glob
import os
import shutil
import sqlite3
import subprocess
import tempfile
from hashlib import pbkdf2_hmac

from LaunchServices import LSCopyDefaultHandlerForURLScheme

# Map bundle IDs to browser identifiers
BUNDLE_ID_MAP = {
    "org.mozilla.firefox": "firefox",
    "com.google.chrome": "chrome",
    "com.brave.browser": "brave",
    "com.microsoft.edgemac": "edge",
    "company.thebrowser.browser": "arc",
    "org.chromium.chromium": "chromium",
    "com.apple.safari": "safari",
}

# Chrome-family cookie DB paths (relative to ~)
CHROMIUM_PATHS = {
    "chrome": "Library/Application Support/Google/Chrome",
    "brave": "Library/Application Support/BraveSoftware/Brave-Browser",
    "edge": "Library/Application Support/Microsoft Edge",
    "arc": "Library/Application Support/Arc/User Data",
    "chromium": "Library/Application Support/Chromium",
}

# Keychain service names for Chrome-family browsers
CHROMIUM_KEYCHAIN_SERVICES = {
    "chrome": "Chrome Safe Storage",
    "brave": "Brave Safe Storage",
    "edge": "Microsoft Edge Safe Storage",
    "arc": "Arc Safe Storage",
    "chromium": "Chromium Safe Storage",
}


# Cache for Chrome encryption key (avoids repeated Keychain prompts)
_chromium_key_cache = {}


def detect_default_browser():
    """Detect the user's default browser. Returns a string like 'firefox', 'chrome', etc."""
    bundle_id = LSCopyDefaultHandlerForURLScheme("http")
    if bundle_id:
        browser = BUNDLE_ID_MAP.get(str(bundle_id).lower())
        if browser:
            print(f"SSO: detected default browser: {browser} ({bundle_id})", flush=True)
            return browser
    print(f"SSO: unknown default browser ({bundle_id}), falling back to chrome", flush=True)
    return "chrome"


def read_browser_cookies(domains):
    """Read cookies for the given domains from the user's default browser.

    Args:
        domains: list of domain patterns to match (e.g., ["%chat.a8c.com%", "%wordpress.com%"])

    Returns:
        list of dicts with keys: host, name, value, path, secure, httponly, expiry
    """
    browser = detect_default_browser()
    if browser == "firefox":
        return _read_firefox_cookies(domains)
    elif browser in CHROMIUM_PATHS:
        return _read_chromium_cookies(domains, browser)
    elif browser == "safari":
        print("SSO: Safari cookies are not accessible on macOS Tahoe+", flush=True)
        return []
    else:
        print(f"SSO: unsupported browser '{browser}'", flush=True)
        return []


def _read_firefox_cookies(domains):
    """Read cookies from Firefox's SQLite database (plaintext values)."""
    profile_pattern = os.path.expanduser(
        "~/Library/Application Support/Firefox/Profiles/*/cookies.sqlite"
    )
    cookie_dbs = glob.glob(profile_pattern)
    if not cookie_dbs:
        print("SSO: no Firefox cookie database found", flush=True)
        return []

    # Use the most recently modified profile
    cookie_db = max(cookie_dbs, key=os.path.getmtime)
    print(f"SSO: reading Firefox cookies from {cookie_db}", flush=True)

    # Copy DB + WAL/SHM to avoid lock issues (Firefox locks the DB while running)
    tmp_dir = tempfile.mkdtemp()
    try:
        tmp_db = os.path.join(tmp_dir, "cookies.sqlite")
        shutil.copy2(cookie_db, tmp_db)
        for ext in ("-wal", "-shm"):
            src = cookie_db + ext
            if os.path.exists(src):
                shutil.copy2(src, tmp_db + ext)

        conn = sqlite3.connect(tmp_db)
        cookies = []
        for domain in domains:
            cursor = conn.execute(
                "SELECT host, name, value, path, isSecure, isHttpOnly, expiry "
                "FROM moz_cookies WHERE host LIKE ?",
                (domain,),
            )
            for row in cursor:
                cookies.append({
                    "host": row[0],
                    "name": row[1],
                    "value": row[2],
                    "path": row[3],
                    "secure": bool(row[4]),
                    "httponly": bool(row[5]),
                    "expiry": row[6],
                })
        conn.close()
        print(f"SSO: found {len(cookies)} Firefox cookies", flush=True)
        return cookies
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _read_chromium_cookies(domains, browser):
    """Read cookies from a Chrome/Chromium browser (encrypted values)."""
    base_path = os.path.expanduser("~/" + CHROMIUM_PATHS[browser])
    if not os.path.isdir(base_path):
        print(f"SSO: {browser} data directory not found: {base_path}", flush=True)
        return []

    # Find the cookie database — use the most recently modified profile
    candidates = []
    for profile_dir in ["Default"] + glob.glob(os.path.join(base_path, "Profile *")):
        if not os.path.isabs(profile_dir):
            profile_dir = os.path.join(base_path, profile_dir)
        candidate = os.path.join(profile_dir, "Cookies")
        if os.path.exists(candidate):
            candidates.append(candidate)
    cookie_db = max(candidates, key=os.path.getmtime) if candidates else None

    if not cookie_db:
        print(f"SSO: no {browser} cookie database found in {base_path}", flush=True)
        return []

    print(f"SSO: reading {browser} cookies from {cookie_db}", flush=True)

    # Get the decryption key from macOS Keychain
    aes_key = _get_chromium_key(browser)
    if aes_key is None:
        print(f"SSO: could not get {browser} encryption key from Keychain", flush=True)
        return []

    # Copy DB to avoid lock issues
    tmp_dir = tempfile.mkdtemp()
    try:
        tmp_db = os.path.join(tmp_dir, "Cookies")
        shutil.copy2(cookie_db, tmp_db)
        for ext in ("-wal", "-shm", "-journal"):
            src = cookie_db + ext
            if os.path.exists(src):
                shutil.copy2(src, tmp_db + ext)

        conn = sqlite3.connect(tmp_db)
        cookies = []
        for domain in domains:
            cursor = conn.execute(
                "SELECT host_key, name, value, encrypted_value, path, "
                "is_secure, is_httponly, expires_utc "
                "FROM cookies WHERE host_key LIKE ?",
                (domain,),
            )
            for row in cursor:
                host, name, value, enc_value, path, secure, httponly, expires = row
                if value:
                    decrypted = value
                else:
                    decrypted = _decrypt_chromium_cookie(enc_value, aes_key)
                if decrypted:
                    cookies.append({
                        "host": host,
                        "name": name,
                        "value": decrypted,
                        "path": path,
                        "secure": bool(secure),
                        "httponly": bool(httponly),
                        "expiry": _chrome_time_to_unix(expires),
                    })
        conn.close()
        print(f"SSO: found {len(cookies)} {browser} cookies", flush=True)
        return cookies
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _get_chromium_key(browser):
    """Get the AES encryption key from macOS Keychain for a Chromium browser (cached)."""
    if browser in _chromium_key_cache:
        return _chromium_key_cache[browser]
    service = CHROMIUM_KEYCHAIN_SERVICES.get(browser)
    if not service:
        return None
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        password = result.stdout.strip()
        # Derive AES-128 key via PBKDF2
        key = pbkdf2_hmac("sha1", password.encode("utf-8"), b"saltysalt", 1003, dklen=16)
        _chromium_key_cache[browser] = key
        return key
    except Exception as e:
        print(f"SSO: Keychain access failed: {e}", flush=True)
        return None


def _decrypt_chromium_cookie(encrypted_value, aes_key):
    """Decrypt a Chrome cookie value using AES-128-CBC via CommonCrypto."""
    if not encrypted_value or len(encrypted_value) < 4:
        return ""
    # v10 prefix indicates macOS Keychain encryption
    if encrypted_value[:3] != b"v10":
        try:
            return encrypted_value.decode("utf-8", errors="replace")
        except Exception:
            return ""
    data = encrypted_value[3:]
    if not data:
        return ""
    iv = b" " * 16  # 16 space characters
    try:
        lib = ctypes.cdll.LoadLibrary("/usr/lib/system/libcommonCrypto.dylib")
    except OSError:
        lib_path = ctypes.util.find_library("commonCrypto")
        if not lib_path:
            print("SSO: CommonCrypto library not found", flush=True)
            return ""
        lib = ctypes.cdll.LoadLibrary(lib_path)
    buffer_size = len(data) + 16
    buffer = ctypes.create_string_buffer(buffer_size)
    out_size = ctypes.c_size_t(0)
    # CCCrypt(op=kCCDecrypt, alg=kCCAlgorithmAES, options=kCCOptionPKCS7Padding,
    #         key, keyLength, iv, dataIn, dataInLength, dataOut, dataOutAvail, dataOutMoved)
    status = lib.CCCrypt(
        1, 0, 1,  # kCCDecrypt, kCCAlgorithmAES, kCCOptionPKCS7Padding
        aes_key, len(aes_key),
        iv,
        data, len(data),
        buffer, buffer_size,
        ctypes.byref(out_size),
    )
    if status != 0:
        return ""
    raw = buffer.raw[:out_size.value]
    # Chrome prepends 32 bytes of internal data before the actual cookie value.
    # Skip this prefix to get the clean plaintext.
    if len(raw) > 32:
        raw = raw[32:]
    return raw.decode("utf-8", errors="replace")


def _chrome_time_to_unix(chrome_time):
    """Convert Chrome's timestamp (microseconds since 1601-01-01) to Unix timestamp."""
    if chrome_time == 0:
        return 0
    # Chrome epoch offset: difference between 1601-01-01 and 1970-01-01 in microseconds
    return int((chrome_time - 11644473600000000) / 1000000)
