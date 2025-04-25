import platform
import os
import sys

class StartupGenerator:
    def __init__(self, script_path):
        self.script_path = script_path

    def create_startup(self):
        os_type = platform.system()

        if os_type == "Windows":
            self.create_windows_startup()
        elif os_type == "Linux":
            self.create_linux_startup()
        elif os_type == "Darwin":
            self.create_macos_startup()
        else:
            print(" Unsupported OS for startup automation.")
            sys.exit(1)

    def create_windows_startup(self):
        startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        startup_script_path = os.path.join(startup_folder, "WiFiAutoConnect.lnk")

        try:
            # Create shortcut for Windows startup
            import winshell
            from win32com.client import Dispatch

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(startup_script_path)
            shortcut.TargetPath = sys.executable
            shortcut.Arguments = f'"{self.script_path}"'
            shortcut.WorkingDirectory = os.path.dirname(self.script_path)
            shortcut.save()

            print(f"✅ Windows startup shortcut created at {startup_script_path}.")
        except Exception as e:
            print(f"❌ Failed to create Windows startup shortcut: {e}")
            sys.exit(1)

    def create_linux_startup(self):
        autostart_folder = os.path.expanduser("~/.config/autostart")
        if not os.path.exists(autostart_folder):
            os.makedirs(autostart_folder)

        desktop_entry_path = os.path.join(autostart_folder, "wifi_auto_connect.desktop")

        try:
            with open(desktop_entry_path, "w") as f:
                f.write(f"""[Desktop Entry]
Name=WiFiAutoConnect
Exec=python3 {self.script_path}
Type=Application
X-GNOME-Autostart-enabled=true
            """)

            os.chmod(desktop_entry_path, 0o755)  # Make the file executable
            print(f" Linux startup script created at {desktop_entry_path}.")
        except Exception as e:
            print(f" Failed to create Linux startup script: {e}")
            sys.exit(1)

    def create_macos_startup(self):
        try:
            # Create a plist file for macOS startup
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>WiFiAutoConnect</string>
    <key>ProgramArguments</key>
    <array>
      <string>python3</string>
      <string>{self.script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
  </dict>
</plist>"""

            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.wifi.autoconnect.plist")

            with open(plist_path, "w") as plist_file:
                plist_file.write(plist_content)

            # Load the plist file to run at login
            os.system(f"launchctl load {plist_path}")

            print(f" macOS startup plist created and loaded at {plist_path}.")
        except Exception as e:
            print(f" Failed to create macOS startup plist: {e}")
            sys.exit(1)
