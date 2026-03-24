# Python libraries
import base64
import json
import os
import sys

# Apple libraries
import objc
from AppKit import *
from WebKit import *
from Quartz import *
from AVFoundation import AVCaptureDevice, AVMediaTypeAudio
from Foundation import NSObject, NSURL, NSURLRequest, NSDate, NSHTTPCookie, NSHTTPCookieStorage
from ApplicationServices import AXIsProcessTrusted

# Local libraries
from .constants import (
    APP_TITLE,
    CORNER_RADIUS,
    DRAG_AREA_HEIGHT,
    MENU_ICON_PATH,
    FRAME_SAVE_NAME,
    WEBSITE,
    LAUNCHER_TRIGGER,
)
from .launcher import (
    install_startup,
    uninstall_startup,
)
from .listener import (
    global_show_hide_listener,
    load_custom_launcher_trigger,
    set_custom_launcher_trigger,
)
from .browser_cookies import read_browser_cookies
from .health_checks import LOG_DIR

KEEP_ON_TOP_FILE = LOG_DIR / "keep_on_top.json"


# Custom window (contains entire application).
class AppWindow(NSWindow):
    # Explicitly allow key window status
    def canBecomeKeyWindow(self):
        return True

    # Required to capture "Command+..." sequences.
    def keyDown_(self, event):
        self.delegate().keyDown_(event)


# Custom view (contains click-and-drag area on top sliver of overlay).
class DragArea(NSView):
    def initWithFrame_(self, frame):
        objc.super(DragArea, self).initWithFrame_(frame)
        self.setWantsLayer_(True)
        return self
    
    # Used to update top-bar background to (roughly) match app color.
    def setBackgroundColor_(self, color):
        self.layer().setBackgroundColor_(color.CGColor())

    # Used to capture the click-and-drag event.
    def mouseDown_(self, event):
        self.window().performWindowDragWithEvent_(event)


# The main delegate for running the overlay app.
class AppDelegate(NSObject):
    # The main application setup.
    def applicationDidFinishLaunching_(self, notification):
        # Load keep-on-top preference (default True)
        self.keep_on_top = self._load_keep_on_top_pref()
        # Create a borderless, floating, resizable window
        self.window = AppWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(500, 200, 550, 580),
            NSWindowStyleMaskBorderless | NSWindowStyleMaskResizable,
            # NSBorderlessWindowMask | NSResizableWindowMask,  # Worked BEFORE Tahoe update
            NSBackingStoreBuffered,
            False
        )
        self._apply_keep_on_top()
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
        )
        # Save the last position and size
        self.window.setFrameAutosaveName_(FRAME_SAVE_NAME)
        # Create the webview for the main application.
        config = WKWebViewConfiguration.alloc().init()
        config.preferences().setJavaScriptCanOpenWindowsAutomatically_(True)
        config.preferences().setValue_forKey_(True, "mediaDevicesEnabled")
        # Initialize the WebView with a frame
        self.webview = WKWebView.alloc().initWithFrame_configuration_(
            ((0, 0), (800, 600)),  # Frame: origin (0,0), size (800x600)
            config
        )
        self.webview.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)  # Resizes with window
        # Set navigation delegate to handle link clicks
        self.webview.setNavigationDelegate_(self)
        # Set a custom user agent
        safari_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        self.webview.setCustomUserAgent_(safari_user_agent)
        # Make window transparent so that the corners can be rounded
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        # Set up content view with rounded corners
        content_view = NSView.alloc().initWithFrame_(self.window.contentView().bounds())
        content_view.setWantsLayer_(True)
        content_view.layer().setCornerRadius_(CORNER_RADIUS)
        content_view.layer().setBackgroundColor_(NSColor.whiteColor().CGColor())
        self.window.setContentView_(content_view)
        # Set up drag area (top sliver, full width)
        content_bounds = content_view.bounds()
        self.drag_area = DragArea.alloc().initWithFrame_(
            NSMakeRect(0, content_bounds.size.height - DRAG_AREA_HEIGHT, content_bounds.size.width, DRAG_AREA_HEIGHT)
        )
        content_view.addSubview_(self.drag_area)
        # Add close button to the drag area
        close_button = NSButton.alloc().initWithFrame_(NSMakeRect(5, 5, 20, 20))
        close_button.setBordered_(False)
        close_button.setImage_(NSImage.imageWithSystemSymbolName_accessibilityDescription_("xmark.circle.fill", None))
        close_button.setTarget_(self)
        close_button.setAction_("hideWindow:")
        self.drag_area.addSubview_(close_button)
        # Update the webview sizinug and insert it below drag area.
        content_view.addSubview_(self.webview)
        self.webview.setFrame_(NSMakeRect(0, 0, content_bounds.size.width, content_bounds.size.height - DRAG_AREA_HEIGHT))
        # SSO: track whether browser auth is in progress
        self._sso_browser_auth = False
        self._sso_retry_count = 0
        # Contat the target website.
        url = NSURL.URLWithString_(WEBSITE)
        request = NSURLRequest.requestWithURL_(url)
        self.webview.loadRequest_(request)
        # Set up script message handlers
        configuration = self.webview.configuration()
        user_content_controller = configuration.userContentController()
        user_content_controller.addScriptMessageHandler_name_(self, "backgroundColorHandler")
        user_content_controller.addScriptMessageHandler_name_(self, "downloadHandler")
        user_content_controller.addScriptMessageHandler_name_(self, "ssoCompleteHandler")
        # Inject JavaScript to monitor background color changes
        bg_color_script = """
            function _post(bg){try{const h=window.webkit?.messageHandlers?.backgroundColorHandler;h&&h.postMessage(bg);}catch(e){}}
            function _getColor(el){if(!el) return null; const c=getComputedStyle(el).backgroundColor; return (!c||c==='rgba(0, 0, 0, 0)'||c==='transparent')?null:c;}
            function sendBackgroundColor(){
                const bg=_getColor(document.body)||_getColor(document.documentElement)||'rgb(255,255,255)';
                _post(bg);
            }
            document.addEventListener('DOMContentLoaded', sendBackgroundColor);
            window.addEventListener('load', sendBackgroundColor);
            new MutationObserver(sendBackgroundColor).observe(document.documentElement,{attributes:true,attributeFilter:['style'],subtree:true,childList:true});
        """
        bg_user_script = WKUserScript.alloc().initWithSource_injectionTime_forMainFrameOnly_(bg_color_script, WKUserScriptInjectionTimeAtDocumentEnd, True)
        user_content_controller.addUserScript_(bg_user_script)
        # Inject JavaScript to intercept blob URL downloads (e.g., "Download as PNG")
        # This script stores blobs when created and intercepts programmatic anchor clicks
        download_script = """
            (function() {
                // Store blobs when they're created so we can access them even after revocation
                const blobStore = new Map();
                const originalCreateObjectURL = URL.createObjectURL;
                const originalRevokeObjectURL = URL.revokeObjectURL;

                URL.createObjectURL = function(blob) {
                    const url = originalCreateObjectURL.call(this, blob);
                    if (blob instanceof Blob) {
                        blobStore.set(url, blob);
                    }
                    return url;
                };

                // Delay revocation to allow download interception
                URL.revokeObjectURL = function(url) {
                    setTimeout(() => {
                        blobStore.delete(url);
                        originalRevokeObjectURL.call(this, url);
                    }, 1000);
                };

                // Intercept programmatic clicks on anchor elements
                const originalClick = HTMLAnchorElement.prototype.click;
                HTMLAnchorElement.prototype.click = function() {
                    if (this.hasAttribute('download') && this.href && this.href.startsWith('blob:')) {
                        const filename = this.download || 'download';
                        const blobUrl = this.href;
                        const blob = blobStore.get(blobUrl);

                        if (blob) {
                            // We have the blob stored, use it directly
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                const base64Data = reader.result.split(',')[1];
                                window.webkit.messageHandlers.downloadHandler.postMessage({
                                    filename: filename,
                                    data: base64Data,
                                    mimeType: blob.type
                                });
                            };
                            reader.readAsDataURL(blob);
                            return; // Don't call original click
                        }
                    }
                    return originalClick.call(this);
                };

                // Also handle regular click events on download links
                document.addEventListener('click', function(e) {
                    const anchor = e.target.closest('a[download]');
                    if (!anchor || !anchor.href || !anchor.href.startsWith('blob:')) return;

                    const blob = blobStore.get(anchor.href);
                    if (blob) {
                        e.preventDefault();
                        e.stopPropagation();
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            const base64Data = reader.result.split(',')[1];
                            window.webkit.messageHandlers.downloadHandler.postMessage({
                                filename: anchor.download || 'download',
                                data: base64Data,
                                mimeType: blob.type
                            });
                        };
                        reader.readAsDataURL(blob);
                    }
                }, true);
            })();
        """
        download_user_script = WKUserScript.alloc().initWithSource_injectionTime_forMainFrameOnly_(download_script, WKUserScriptInjectionTimeAtDocumentStart, True)
        user_content_controller.addUserScript_(download_user_script)
        # Create status bar item with template icon (auto-adapts to light/dark mode)
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSSquareStatusItemLength)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        menu_icon_path = os.path.join(script_dir, MENU_ICON_PATH)
        menu_icon = NSImage.alloc().initWithContentsOfFile_(menu_icon_path)
        menu_icon.setSize_(NSSize(18, 18))
        menu_icon.setTemplate_(True)  # Makes macOS auto-tint for light/dark mode
        self.status_item.button().setImage_(menu_icon)
        # Create status bar menu
        menu = NSMenu.alloc().init()
        # Create and configure menu items with explicit targets
        show_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Show "+APP_TITLE, "showWindow:", "")
        show_item.setTarget_(self)
        menu.addItem_(show_item)
        hide_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Hide "+APP_TITLE, "hideWindow:", "h")
        hide_item.setTarget_(self)
        menu.addItem_(hide_item)
        self.keep_on_top_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Keep Window on Top", "toggleKeepOnTop:", "")
        self.keep_on_top_item.setTarget_(self)
        self.keep_on_top_item.setState_(NSControlStateValueOn if self.keep_on_top else NSControlStateValueOff)
        menu.addItem_(self.keep_on_top_item)
        home_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Home", "goToWebsite:", "g")
        home_item.setTarget_(self)
        menu.addItem_(home_item)
        clear_data_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Clear Web Cache", "clearWebViewData:", "")
        clear_data_item.setTarget_(self)
        menu.addItem_(clear_data_item)
        # Reset window size (useful when window is off-screen)
        reset_size_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Reset Window Size", "resetWindowSize:", "")
        reset_size_item.setTarget_(self)
        menu.addItem_(reset_size_item)
        # Microphone.
        mic_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Request Microphone Access", "requestMicrophoneAccess:", "")
        mic_item.setTarget_(self)
        menu.addItem_(mic_item)
        # Intall / uninstall autolauncher.
        install_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Install Autolauncher", "install:", "")
        install_item.setTarget_(self)
        menu.addItem_(install_item)
        uninstall_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Uninstall Autolauncher", "uninstall:", "")
        uninstall_item.setTarget_(self)
        menu.addItem_(uninstall_item)
        # ----------------------------------------
        menu.addItem_(NSMenuItem.separatorItem())
        # Trigger.
        set_trigger_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Set New Trigger", "setTrigger:", "")
        set_trigger_item.setTarget_(self)
        menu.addItem_(set_trigger_item)
        trigger_label = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Current Trigger", "", "")
        trigger_label.setEnabled_(False)
        menu.addItem_(trigger_label)
        self.trigger_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("", "", "")
        self.trigger_item.setEnabled_(False)
        menu.addItem_(self.trigger_item)
        menu.addItem_(NSMenuItem.separatorItem())
        # ----------------------------------------
        # Quit.
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Quit", "terminate:", "q")
        quit_item.setTarget_(NSApp)
        menu.addItem_(quit_item)
        # Set the menu for the status item
        self.status_item.setMenu_(menu)
        # Add resize observer
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self, 'windowDidResize:', NSWindowDidResizeNotification, self.window
        )
        # Add local mouse event monitor for left mouse down
        self.local_mouse_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            NSEventMaskLeftMouseDown,  # Monitor left mouse-down events
            self.handleLocalMouseEvent  # Handler method
        )
        # Create the event tap for key-down events
        tap = CGEventTapCreate(
            kCGSessionEventTap, # Tap at the session level
            kCGHeadInsertEventTap, # Insert at the head of the event queue
            kCGEventTapOptionDefault, # Actively filter events
            CGEventMaskBit(kCGEventKeyDown), # Capture key-down events
            global_show_hide_listener(self), # Your callback function
            None # Optional user info (refcon)
        )
        if tap:
            # Integrate the tap into the run loop
            source = CFMachPortCreateRunLoopSource(None, tap, 0)
            CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
            CGEventTapEnable(tap, True)
            # CFRunLoopRun() # Start the run loop (causes HANG as of Tahoe)
        else:
            print("Failed to create event tap. Check Accessibility permissions.")
        # Check accessibility permissions and prompt user if needed
        self.accessibility_granted = AXIsProcessTrusted()
        if not self.accessibility_granted:
            self.showAccessibilityPrompt()
            self.startAccessibilityMonitor()
        # Load the custom launch trigger if the user set it.
        load_custom_launcher_trigger(self)
        # Set the delegate of the window to this parent application.
        self.window.setDelegate_(self)
        # Make sure this window is shown and focused.
        self.showWindow_(None)

    # Logic to show the overlay, make it the key window, and focus on the typing area.
    def showWindow_(self, sender):
        self.window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)
        # Execute the JavaScript to focus the textarea in the WKWebView
        self.webview.evaluateJavaScript_completionHandler_(
            "[...document.querySelectorAll('textarea')].sort((a,b)=>a.contains(b)?-1:b.contains(a)?1:0).pop()?.focus();",
            None
        )

    # Hide the overlay and allow focus to return to the next visible application.
    def hideWindow_(self, sender):
        NSApp.hide_(None)

    # Load keep-on-top preference from disk (defaults to True).
    def _load_keep_on_top_pref(self):
        try:
            if KEEP_ON_TOP_FILE.exists():
                with open(KEEP_ON_TOP_FILE, "r") as f:
                    return json.load(f).get("keep_on_top", True)
        except Exception:
            pass
        return True

    # Apply the current keep_on_top state to the window level and activation policy.
    def _apply_keep_on_top(self):
        if self.keep_on_top:
            self.window.setLevel_(NSFloatingWindowLevel)
            NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        else:
            self.window.setLevel_(NSNormalWindowLevel)
            NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)

    # Toggle always-on-top and Dock visibility.
    def toggleKeepOnTop_(self, sender):
        self.keep_on_top = not self.keep_on_top
        self._apply_keep_on_top()
        self.keep_on_top_item.setState_(
            NSControlStateValueOn if self.keep_on_top else NSControlStateValueOff
        )
        with open(KEEP_ON_TOP_FILE, "w") as f:
            json.dump({"keep_on_top": self.keep_on_top}, f)
        self.showWindow_(None)

    # Reset window to default size and center on screen (useful when edges are off-screen).
    def resetWindowSize_(self, sender):
        default_width = 550
        default_height = 580
        # Get the current screen (where the window is, or main screen as fallback)
        screen = self.window.screen() or NSScreen.mainScreen()
        screen_frame = screen.visibleFrame()
        # Calculate centered position
        x = screen_frame.origin.x + (screen_frame.size.width - default_width) / 2
        y = screen_frame.origin.y + (screen_frame.size.height - default_height) / 2
        # Set the new frame
        new_frame = NSMakeRect(x, y, default_width, default_height)
        self.window.setFrame_display_animate_(new_frame, True, True)
        # Make sure window is visible
        self.showWindow_(None)

    # Go to the default landing website for the overlay (in case accidentally navigated away).
    def goToWebsite_(self, sender):
        url = NSURL.URLWithString_(WEBSITE)
        request = NSURLRequest.requestWithURL_(url)
        self.webview.loadRequest_(request)
    
    # Clear the webview cache data (in case cookies cause errors).
    def clearWebViewData_(self, sender):
        dataStore = self.webview.configuration().websiteDataStore()
        dataTypes = WKWebsiteDataStore.allWebsiteDataTypes()
        dataStore.removeDataOfTypes_modifiedSince_completionHandler_(
            dataTypes,
            NSDate.distantPast(),
            lambda: print("Data cleared")
        )

    # Explicitly request microphone permission from macOS.
    def requestMicrophoneAccess_(self, sender):
        try:
            AVCaptureDevice.requestAccessForMediaType_completionHandler_(
                AVMediaTypeAudio,
                lambda granted: print(f"Microphone access {'granted' if granted else 'denied'}.", flush=True)
            )
        except Exception as e:
            print(f"Failed to request microphone access: {e}", flush=True)

    # Go to the default landing website for the overlay (in case accidentally navigated away).
    def install_(self, sender):
        if install_startup():
            # Exit the current process since a new one will launch.
            print("Installation successful, exiting.", flush=True)
            NSApp.terminate_(None)
        else:
            print("Installation unsuccessful.", flush=True)

    # Go to the default landing website for the overlay (in case accidentally navigated away).
    def uninstall_(self, sender):
        if uninstall_startup():
            NSApp.hide_(None)

    # Handle the 'Set Trigger' menu item click.
    def setTrigger_(self, sender):
        set_custom_launcher_trigger(self)

    def updateTriggerMenu(self, key_string=""):
        self.trigger_item.setTitle_("    " + key_string)

    # For capturing key commands while the key window (in focus).
    def keyDown_(self, event):
        modifiers = event.modifierFlags()
        key_command = modifiers & NSEventModifierFlagCommand
        key_alt = modifiers & NSEventModifierFlagOption
        key_shift = modifiers & NSEventModifierFlagShift
        key_control = modifiers & NSEventModifierFlagControl
        key = event.charactersIgnoringModifiers()
        # Command (NOT alt)
        if (key_command or key_control) and (not key_alt):
            # Select all
            if key == 'a':
                self.window.firstResponder().selectAll_(None)
            # Copy
            elif key == 'c':
                self.window.firstResponder().copy_(None)
            # Cut
            elif key == 'x':
                self.window.firstResponder().cut_(None)
            # Paste
            elif key == 'v':
                self.window.firstResponder().paste_(None)
            # Hide
            elif key == 'h':
                self.hideWindow_(None)
            # Quit
            elif key == 'q':
                NSApp.terminate_(None)
            # # Undo (causes crash for some reason)
            # elif key == 'z':
            #     self.window.firstResponder().undo_(None)

    # Handler for capturing a click-and-drag event when not already the key window.
    @objc.python_method
    def handleLocalMouseEvent(self, event):
        if event.window() == self.window:
            # Get the click location in window coordinates
            click_location = event.locationInWindow()
            # Use hitTest_ to determine which view receives the click
            hit_view = self.window.contentView().hitTest_(click_location)
            # Check if the hit view is the drag area
            if hit_view == self.drag_area:
                # Bring the window to the front and make it key
                self.showWindow_(None)
                # Initiate window dragging with the event
                self.window.performWindowDragWithEvent_(event)
                return None  # Consume the event
        return event  # Pass unhandled events along

    # Handler for when the window resizes (adjusts the drag area).
    def windowDidResize_(self, notification):
        bounds = self.window.contentView().bounds()
        w, h = bounds.size.width, bounds.size.height
        self.drag_area.setFrame_(NSMakeRect(0, h - DRAG_AREA_HEIGHT, w, DRAG_AREA_HEIGHT))
        self.webview.setFrame_(NSMakeRect(0, 0, w, h - DRAG_AREA_HEIGHT))

    # Handler for script messages from JavaScript (background color and downloads)
    def userContentController_didReceiveScriptMessage_(self, userContentController, message):
        if message.name() == "backgroundColorHandler":
            bg_color_str = message.body()
            # Convert CSS color to NSColor (assuming RGB for simplicity)
            if bg_color_str.startswith("rgb") and ("(" in bg_color_str) and (")" in bg_color_str):
                rgb_values = [float(val) for val in bg_color_str[bg_color_str.index("(")+1:bg_color_str.index(")")].split(",")]
                r, g, b = [val / 255.0 for val in rgb_values[:3]]
                color = NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, 1.0)
                self.drag_area.setBackgroundColor_(color)
        elif message.name() == "downloadHandler":
            self._handleDownload(message.body())
        elif message.name() == "ssoCompleteHandler":
            self.ssoCompleteHandler_(message)

    # Handle file downloads from blob URLs
    @objc.python_method
    def _handleDownload(self, download_info):
        try:
            filename = download_info.get("filename", "download")
            base64_data = download_info.get("data", "")
            mime_type = download_info.get("mimeType", "application/octet-stream")
            # Decode base64 data
            file_data = base64.b64decode(base64_data)
            # Determine file extension if not present
            if "." not in filename:
                ext_map = {
                    "image/png": ".png",
                    "image/jpeg": ".jpg",
                    "image/gif": ".gif",
                    "image/webp": ".webp",
                    "application/pdf": ".pdf",
                }
                filename += ext_map.get(mime_type, "")
            # Save to Downloads folder with duplicate handling
            downloads_path = os.path.expanduser("~/Downloads")
            save_path = os.path.join(downloads_path, filename)
            # Handle duplicate filenames
            base_name, ext = os.path.splitext(save_path)
            counter = 1
            while os.path.exists(save_path):
                save_path = f"{base_name} ({counter}){ext}"
                counter += 1
            # Write the file
            with open(save_path, "wb") as f:
                f.write(file_data)
            print(f"Downloaded: {save_path}", flush=True)
            # Reveal file in Finder
            NSWorkspace.sharedWorkspace().selectFile_inFileViewerRootedAtPath_(save_path, "")
        except Exception as e:
            print(f"Download failed: {e}", flush=True)


    # Navigation delegate method to handle link clicks and blob downloads
    def webView_decidePolicyForNavigationAction_decisionHandler_(self, webView, navigationAction, decisionHandler):
        request = navigationAction.request()
        url = request.URL()
        url_string = url.absoluteString() if url else ""
        # Intercept blob: URLs for download (WKWebView can't load these natively)
        if url_string.startswith("blob:"):
            print(f"Intercepting blob URL for download: {url_string}", flush=True)
            # Cancel navigation and trigger download via JavaScript
            decisionHandler(0)  # WKNavigationActionPolicyCancel = 0
            self._downloadBlobURL(url_string)
            return
        host = url.host() if url else None
        # WordPress.com SSO: WebAuthn (security keys) doesn't work in WKWebView,
        # so we handle the OAuth flow in ASWebAuthenticationSession which uses
        # Safari's full browser capabilities including WebAuthn support.
        if host == "public-api.wordpress.com":
            # Auto-retry: if we just imported cookies and SSO still triggers,
            # retry with a delay (browser may not have flushed cookies to disk yet)
            if self._sso_retry_count > 0 and self._sso_retry_count <= 3:
                print(f"SSO: auto-retry {self._sso_retry_count}/3 (waiting 2s)", flush=True)
                decisionHandler(0)
                self._sso_retry_count += 1
                # Delay before retry to let the browser flush cookies to disk
                NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                    2.0, self, "ssoAutoRetry:", None, False)
                return
            if self._sso_retry_count > 3:
                # Give up retrying, show the waiting page again
                self._sso_retry_count = 0
            print(f"SSO redirect detected, opening default browser", flush=True)
            decisionHandler(0)  # Cancel navigation in WKWebView
            self._sso_browser_auth = True
            self._showSSOWaitingPage()
            # Open chat.a8c.com in the user's default browser for authentication
            NSWorkspace.sharedWorkspace().openURL_(NSURL.URLWithString_(WEBSITE))
            return
        # Get the navigation type (link click, form submit, etc.)
        nav_type = navigationAction.navigationType()
        # WKNavigationTypeLinkActivated = 0 (user clicked a link)
        # Check if this is a user-initiated link click
        if nav_type == 0:  # Link activated by user click
            # Check if the URL is external (not chat.a8c.com)
            if host and host not in ["chat.a8c.com", "www.chat.a8c.com"]:
                # Open external link in default browser
                print(f"Opening external link in browser: {url_string}", flush=True)
                NSWorkspace.sharedWorkspace().openURL_(url)
                # Cancel the navigation in the webview
                decisionHandler(0)  # WKNavigationActionPolicyCancel = 0
                return
        # Allow all other navigations (internal links, initial page load, etc.)
        decisionHandler(1)  # WKNavigationActionPolicyAllow = 1

    # Handler for "I've signed in" button on the SSO waiting page
    def ssoCompleteHandler_(self, message):
        if message.body() == "done":
            self._sso_retry_count = 1  # Enable auto-retry on next SSO redirect
            self._importBrowserCookiesAndReload()

    # Read cookies from the user's default browser and set them in WKWebView
    @objc.python_method
    def _importBrowserCookiesAndReload(self):
        self._sso_browser_auth = False
        domains = ["%chat.a8c.com%", "%.wordpress.com%", "%wordpress.com"]
        browser_cookies = read_browser_cookies(domains)
        if not browser_cookies:
            print("SSO: no cookies found in browser", flush=True)
            self._showSSOErrorPage("No session found in your browser. Please sign in to chat.a8c.com in your browser first, then try again.")
            return
        # Filter out connect.sid — it's a server-side session cookie tied to the browser.
        # Importing it causes session conflicts when the browser also has chat.a8c.com open.
        # Instead, we keep refreshToken/token_provider (JWT-based, creates a new session)
        # and all WordPress.com auth cookies.
        filtered = [c for c in browser_cookies if c["name"] != "connect.sid"]
        print(f"SSO: filtered {len(browser_cookies)} → {len(filtered)} cookies (excluded connect.sid)", flush=True)
        browser_cookies = filtered
        # Clear ALL existing WKWebView data to avoid conflicts with stale sessions,
        # cached redirects, or service workers — then set the fresh browser cookies
        self._pending_browser_cookies = browser_cookies
        self.webview.stopLoading()
        from WebKit import WKWebsiteDataStore
        data_store = self.webview.configuration().websiteDataStore()
        all_types = WKWebsiteDataStore.allWebsiteDataTypes()
        data_store.removeDataOfTypes_modifiedSince_completionHandler_(
            all_types, NSDate.distantPast(), self._onWKCookiesCleared)

    @objc.python_method
    def _onWKCookiesCleared(self):
        browser_cookies = self._pending_browser_cookies
        self._pending_browser_cookies = None
        print(f"SSO: cleared WKWebView cookies, setting {len(browser_cookies)} browser cookies", flush=True)
        wk_cookie_store = self.webview.configuration().websiteDataStore().httpCookieStore()
        remaining = [len(browser_cookies)]
        def on_cookie_set():
            remaining[0] -= 1
            if remaining[0] <= 0:
                print(f"SSO: all {len(browser_cookies)} cookies set, reloading in 2s", flush=True)
                NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                    2.0, self, "ssoReloadAfterDelay:", None, False)
        for bc in browser_cookies:
            props = {
                "Domain": bc["host"],
                "Name": bc["name"],
                "Value": bc["value"],
                "Path": bc.get("path", "/"),
            }
            if bc.get("secure"):
                props["Secure"] = "TRUE"
            if bc.get("expiry") and bc["expiry"] > 0:
                props["Expires"] = NSDate.dateWithTimeIntervalSince1970_(bc["expiry"])
            cookie = NSHTTPCookie.cookieWithProperties_(props)
            if cookie:
                wk_cookie_store.setCookie_completionHandler_(cookie, on_cookie_set)
            else:
                # Skip invalid cookies, adjust counter
                remaining[0] -= 1
        if remaining[0] <= 0:
            # All cookies were invalid or empty list
            print("SSO: no valid cookies to set", flush=True)
            self._showSSOErrorPage("Could not import browser cookies. Please try again.")

    # Timer callback for auto-retry after SSO redirect
    def ssoAutoRetry_(self, timer):
        self._importBrowserCookiesAndReload()

    # Timer callback to reload chat after cookies are set
    def ssoReloadAfterDelay_(self, timer):
        print("SSO: reloading chat.a8c.com now", flush=True)
        self.webview.stopLoading()
        url = NSURL.URLWithString_(WEBSITE)
        request = NSURLRequest.requestWithURL_(url)
        self.webview.loadRequest_(request)

    # Show a waiting page while SSO authentication happens in the default browser
    @objc.python_method
    def _showSSOWaitingPage(self):
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        :root { color-scheme: light dark; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; padding: 20px;
            background: light-dark(#f5f5f7, #1d1d1f);
            color: light-dark(#1d1d1f, #f5f5f7);
        }
        .container { text-align: center; max-width: 400px; }
        .icon { font-size: 48px; margin-bottom: 16px; }
        h1 { font-size: 22px; font-weight: 600; margin-bottom: 12px; }
        .message {
            font-size: 15px; color: light-dark(#6e6e73, #a1a1a6);
            line-height: 1.5; margin-bottom: 24px;
        }
        .done-btn {
            background: #0071e3; color: white; border: none;
            padding: 12px 32px; font-size: 16px; font-weight: 500;
            border-radius: 8px; cursor: pointer; transition: background 0.2s;
        }
        .done-btn:hover { background: #0077ed; }
        .done-btn:active { background: #006edb; }
        .tip {
            margin-top: 16px; font-size: 13px;
            color: light-dark(#86868b, #8e8e93);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">&#x1F310;</div>
        <h1>Sign in with your browser</h1>
        <p class="message">
            A browser window has opened for WordPress.com sign-in.<br>
            After you've signed in, come back here and click the button below.
        </p>
        <button class="done-btn" onclick="window.webkit.messageHandlers.ssoCompleteHandler.postMessage('done')">
            I've signed in
        </button>
        <p class="tip">Chrome/Brave users: macOS may ask for Keychain access — click <b>Allow</b>.</p>
        <p class="tip">Having issues? <a href="https://aip2.wordpress.com/2026/01/18/instant-librechat-access-with-a-keyboard-shortcut-%E2%9A%A1-librechat-a8c-overlay" style="color: #0071e3;">Report on the A8C Overlay P2</a></p>
    </div>
</body>
</html>
"""
        self.webview.loadHTMLString_baseURL_(html, None)

    # Show an error page when SSO cookie import fails
    @objc.python_method
    def _showSSOErrorPage(self, message):
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        :root {{ color-scheme: light dark; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; padding: 20px;
            background: light-dark(#f5f5f7, #1d1d1f);
            color: light-dark(#1d1d1f, #f5f5f7);
        }}
        .container {{ text-align: center; max-width: 400px; }}
        h1 {{ font-size: 22px; font-weight: 600; margin-bottom: 12px; }}
        .message {{
            font-size: 15px; color: light-dark(#6e6e73, #a1a1a6);
            line-height: 1.5; margin-bottom: 24px;
        }}
        .retry-btn {{
            background: #0071e3; color: white; border: none;
            padding: 12px 32px; font-size: 16px; font-weight: 500;
            border-radius: 8px; cursor: pointer;
        }}
        .retry-btn:hover {{ background: #0077ed; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Sign-in incomplete</h1>
        <p class="message">{message}</p>
        <button class="retry-btn" onclick="window.location.href='{WEBSITE}'">Try Again</button>
    </div>
</body>
</html>
"""
        self.webview.loadHTMLString_baseURL_(html, None)

    # Download a blob URL by fetching it via JavaScript and passing to native handler
    @objc.python_method
    def _downloadBlobURL(self, blob_url):
        # Use JavaScript to fetch the blob and convert to base64
        js_code = f"""
        (function() {{
            fetch('{blob_url}')
                .then(r => r.blob())
                .then(blob => {{
                    const reader = new FileReader();
                    reader.onloadend = () => {{
                        const base64Data = reader.result.split(',')[1];
                        window.webkit.messageHandlers.downloadHandler.postMessage({{
                            filename: 'download',
                            data: base64Data,
                            mimeType: blob.type
                        }});
                    }};
                    reader.readAsDataURL(blob);
                }})
                .catch(err => console.error('Blob download failed:', err));
        }})();
        """
        self.webview.evaluateJavaScript_completionHandler_(js_code, None)

    # Navigation delegate method to handle load failures
    def webView_didFailProvisionalNavigation_withError_(self, webView, navigation, error):
        error_code = error.code()
        error_description = error.localizedDescription()
        # Error 102 = Frame load interrupted by policy change (e.g., SSO redirect cancelled).
        # Error -999 = NSURLErrorCancelled. Both are expected when we cancel for SSO.
        if error_code in (102, -999) and self._sso_browser_auth:
            print(f"Navigation cancelled for SSO (code {error_code}), ignoring", flush=True)
            return
        print(f"Navigation failed: {error_code} - {error_description}", flush=True)
        self._showErrorPage(error_code, error_description)

    # Show a custom error page when navigation fails
    @objc.python_method
    def _showErrorPage(self, error_code, error_description):
        error_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {{
            color-scheme: light dark;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            background: light-dark(#f5f5f7, #1d1d1f);
            color: light-dark(#1d1d1f, #f5f5f7);
        }}
        .container {{
            text-align: center;
            max-width: 400px;
        }}
        .icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        h1 {{
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 12px;
        }}
        .message {{
            font-size: 16px;
            color: light-dark(#6e6e73, #a1a1a6);
            margin-bottom: 24px;
            line-height: 1.5;
        }}
        .retry-btn {{
            background: #0071e3;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 500;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .retry-btn:hover {{
            background: #0077ed;
        }}
        .retry-btn:active {{
            background: #006edb;
        }}
        .error-details {{
            margin-top: 24px;
            padding: 12px;
            background: light-dark(#e8e8ed, #2d2d2d);
            border-radius: 8px;
            font-size: 12px;
            color: light-dark(#86868b, #8e8e93);
        }}
        .tip {{
            margin-top: 16px;
            font-size: 13px;
            color: light-dark(#86868b, #8e8e93);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">⚠️</div>
        <h1>Something went wrong</h1>
        <p class="message">The page could not be loaded. Please check your connection and try again.</p>
        <button class="retry-btn" onclick="window.location.href='{WEBSITE}'">Try Again</button>
        <div class="error-details">
            Error {error_code}: {error_description}
        </div>
        <p class="tip">Tip: Make sure you're connected to the Automattic proxy</p>
    </div>
</body>
</html>
"""
        self.webview.loadHTMLString_baseURL_(error_html, None)

    # Show initial prompt explaining accessibility permissions are needed
    def showAccessibilityPrompt(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Accessibility Permission Required")
        alert.setInformativeText_(
            f"{APP_TITLE} needs Accessibility permissions to detect your keyboard shortcut.\n\n"
            "Please grant permission in System Settings, then the app will prompt you to restart."
        )
        alert.addButtonWithTitle_("Open System Settings")
        alert.addButtonWithTitle_("Later")
        alert.setAlertStyle_(NSAlertStyleWarning)
        response = alert.runModal()
        if response == NSAlertFirstButtonReturn:
            # Open System Settings to Accessibility pane
            url = NSURL.URLWithString_("x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility")
            NSWorkspace.sharedWorkspace().openURL_(url)

    # Start a timer to periodically check if accessibility permissions were granted
    def startAccessibilityMonitor(self):
        self.accessibility_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            2.0,  # Check every 2 seconds
            self,
            "checkAccessibilityStatus:",
            None,
            True
        )

    # Timer callback to check if accessibility permissions are now granted
    def checkAccessibilityStatus_(self, timer):
        if AXIsProcessTrusted():
            # Permissions granted! Stop the timer and prompt for restart
            timer.invalidate()
            self.accessibility_timer = None
            self.showRestartPrompt()

    # Show prompt asking user to restart the app after permissions were granted
    def showRestartPrompt(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Restart Required")
        alert.setInformativeText_(
            "Accessibility permissions have been granted.\n\n"
            f"Please restart {APP_TITLE} for the keyboard shortcut to work."
        )
        alert.addButtonWithTitle_("Restart Now")
        alert.addButtonWithTitle_("Later")
        alert.setAlertStyle_(NSAlertStyleInformational)
        response = alert.runModal()
        if response == NSAlertFirstButtonReturn:
            self.restartApp_(None)

    # Restart the application
    def restartApp_(self, sender):
        # Get the path to the current application
        bundle_path = NSBundle.mainBundle().bundlePath()
        # Use NSTask to relaunch
        task = NSTask.alloc().init()
        task.setLaunchPath_("/usr/bin/open")
        task.setArguments_(["-n", bundle_path])
        task.launch()
        # Terminate current instance
        NSApp.terminate_(None)
