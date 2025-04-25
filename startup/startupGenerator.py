import platform
import os
import sys
import winreg as reg  # Registry module for Windows

class StartupGenerator:
    def __init__(self, script_path):
        self.script_path = script_path

    def create_startup(self):
        os_type = platform.system()

        if os_type == "Windows":
            self.create_windows_startup_registry()
        elif os_type == "Linux":
            self.create_linux_startup()
        elif os_type == "Darwin":
            self.create_macos_startup()
        else:
            print("Unsupported OS for startup automation.")
            sys.exit(1)

    def create_windows_startup_registry(self):
        # Registry key to make script run at startup
        try:
            registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, registry_path, 0, reg.KEY_WRITE)
            reg.SetValueEx(registry_key, "WiFiAutoConnect", 0, reg.REG_SZ, f'"{sys.executable}" "{self.script_path}"')
            reg.CloseKey(registry_key)
            print(" Windows registry startup entry created.")
        except Exception as e:
            print(f" Failed to create Windows startup registry entry: {e}")
            sys.exit(1)

    def create_linux_startup(self):
        # Linux startup with `.desktop` file as previously provided
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
            os.chmod(desktop_entry_path, 0o755)  # Make it executable
            print(f" Linux startup script created at {desktop_entry_path}.")
        except Exception as e:
            print(f" Failed to create Linux startup script: {e}")
            sys.exit(1)

    def create_macos_startup(self):
        # macOS startup using a plist file as previously provided
        try:
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
