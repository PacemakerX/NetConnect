import os
import sys
from menu.menuHandler import MenuHandler
from utils.platformUtils import clear_screen
from pathlib import Path

# Load splash art from assets
def show_splash():
    splash_path = Path(__file__).parent / "assets" / "splash.txt"
    if splash_path.exists():
        with open(splash_path, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("=== WiFi Auto Login ===")

def main():
    clear_screen()
    show_splash()

    menu = MenuHandler()
    menu.main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n Aborted by user.")
        sys.exit(0)
