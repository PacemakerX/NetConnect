#!/usr/bin/env python3
"""
WiFi Auto Login System
=====================

This module serves as the main entry point for the WiFi Auto Login application.
It handles the initialization, splash screen display, and main program flow.

The application provides automated WiFi login capabilities with the following features:
- User-friendly menu interface
- Automatic startup configuration
- Splash screen display
- Error handling for graceful exits

Dependencies:
    - menu.menuHandler: Handles all menu-related operations
    - utils.platformUtils: Provides platform-specific utility functions
    - startup.startupGenerator: Manages application startup configuration
"""

import os
import sys
from pathlib import Path
from menu.menuHandler import MenuHandler
from utils.platformUtils import clear_screen
from startup.startupGenerator import StartupGenerator

def show_splash() -> None:
    """
    Display the application's splash screen.
    
    Attempts to load and display custom splash art from assets/splash.txt.
    Falls back to a simple text header if the splash file is not found.
    
    Returns:
        None
    """
    splash_path = Path(__file__).parent / "assets" / "splash.txt"
    if splash_path.exists():
        with open(splash_path, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("=== WiFi Auto Login ===")

def setup_startup() -> None:
    """
    Configure application to run at system startup.
    
    Raises:
        SystemExit: If startup configuration fails
    """
    try:
        startup = StartupGenerator()
        startup.setup_startup()
    except Exception as e:
        print(f"Error creating startup: {e}")
        sys.exit(1)

def main() -> None:
    """
    Main application entry point.
    
    Handles the primary program flow:
    1. Clears the screen
    2. Shows splash screen
    3. Initializes and runs menu system
    4. Sets up startup configuration
    """
    clear_screen()
    show_splash()

    # Initialize and run menu system
    menu = MenuHandler()
    menu.main_menu()

    # Configure startup after successful setup
    setup_startup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(0)
