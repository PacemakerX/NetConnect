import platform
import os

def clear_screen():
    """
    Clears the terminal screen based on the operating system.

    This function detects the current operating system and uses the appropriate
    command to clear the terminal screen:
    - Windows: Uses 'cls' command
    - Linux/macOS: Uses 'clear' command
    - Other OS: Falls back to printing multiple newlines

    Returns:
        None

    Examples:
        >>> clear_screen()
        # Screen will be cleared

    Notes:
        - For Windows systems, uses 'cls' command via os.system
        - For Unix-based systems (Linux/macOS), uses 'clear' command
        - For unsupported systems, prints 100 newlines as a fallback
        - Requires 'platform' and 'os' modules

    Warning:
        The os.system() calls may be platform-dependent and might not work
        in all environments or terminal types.
    """
    os_type = platform.system().lower()

    if os_type == 'windows':
        os.system('cls')
    elif os_type in ['linux', 'darwin']:  # Linux or macOS
        os.system('clear')
    else:
        # Fallback method for unsupported operating systems
        print("\n" * 100)
