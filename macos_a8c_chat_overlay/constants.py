
# Apple libraries
from Quartz import (
    kCGEventFlagMaskAlternate,
    kCGEventFlagMaskCommand,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
)


WEBSITE = "https://chat.a8c.com"
LOGO_WHITE_PATH = "logo/logo_white.png"
LOGO_BLACK_PATH = "logo/logo_black.png"
MENU_ICON_PATH = "logo/menu_icon_18x18.png"
FRAME_SAVE_NAME = "A8CChatWindowFrame"
APP_TITLE = "A8C Chat"
PERMISSION_CHECK_EXIT = 1
CORNER_RADIUS = 15.0
DRAG_AREA_HEIGHT = 30
STATUS_ITEM_CONTEXT = 1
LAUNCHER_TRIGGER_MASK = (
    kCGEventFlagMaskShift |
    kCGEventFlagMaskControl |
    kCGEventFlagMaskAlternate |
    kCGEventFlagMaskCommand
)
# Default trigger is "Control + Space".
LAUNCHER_TRIGGER = {
    "flags": kCGEventFlagMaskControl,
    "key": 49
}
