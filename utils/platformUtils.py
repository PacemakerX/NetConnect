import platform
import os

def clear_screen():
    """
    Clears the terminal screen based on the operating system.
    """
    os_type = platform.system().lower()

    if os_type == 'windows':
        os.system('cls')
    elif os_type in ['linux', 'darwin']:  # Linux or macOS
        os.system('clear')
    else:
        print("\n" * 100)  # Fallback: just print newlines if the OS is unsupported
