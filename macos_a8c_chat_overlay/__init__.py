"""
macOS A8C Chat Overlay - A macOS overlay app for A8C Chat.
"""

import os
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ABOUT_DIR = os.path.join(DIRECTORY, "about")
with open(os.path.join(ABOUT_DIR,"version.txt")) as f:
    __version__ = f.read().strip()
with open(os.path.join(ABOUT_DIR,"author.txt")) as f:
    __author__ = f.read().strip()

__all__ = ["main"]

from .main import main
