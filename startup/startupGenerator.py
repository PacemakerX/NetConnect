import os
import sys
import platform
import json
from pathlib import Path
import stat
import shutil
import subprocess

try:
    import winreg as reg  # For Windows registry
except ImportError:
    pass  # Not on Windows

class StartupGenerator:
    def __init__(self, app_name="NetConnect"):
        """
        Initialize the StartupGenerator with app name and credential file path
        """
        self.app_name = app_name
        self.os_type = platform.system()
        self.credentials_file = Path.home() / ".wifi_auto_login" / "credentials.json"
        
        # Define script locations based on OS
        if self.os_type == "Windows":
            self.scripts_dir = Path.home() / "AppData" / "Local" / self.app_name
            self.script_path = self.scripts_dir / "wifi_connect.ps1"
        elif self.os_type == "Linux":
            self.scripts_dir = Path.home() / ".local" / "share" / self.app_name.lower()
            self.script_path = self.scripts_dir / "wifi_connect.sh"
        elif self.os_type == "Darwin":  # macOS
            self.scripts_dir = Path.home() / "Library" / "Application Support" / self.app_name
            self.script_path = self.scripts_dir / "wifi_connect.sh"
        else:
            raise OSError(f"Unsupported operating system: {self.os_type}")

    def setup_startup(self):
        """
        Main method to setup startup for the detected OS
        """
        try:
            # Create directory if it doesn't exist
            self.scripts_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate and save the connection script
            self._generate_connection_script()
            
            # Create startup entry for the generated script
            self._create_startup_entry()
            
            return True, f"Startup configuration completed for {self.os_type}"
        except Exception as e:
            return False, f"Failed to setup startup: {str(e)}"

    def _generate_connection_script(self):
        """
        Generate the platform-specific connection script
        """
        # Make sure the scripts directory exists
        if not self.scripts_dir.exists():
            self.scripts_dir.mkdir(parents=True)
            
        if self.os_type == "Windows":
            self._generate_windows_script()
        elif self.os_type == "Linux":
            self._generate_linux_script()
        elif self.os_type == "Darwin":  # macOS
            self._generate_macos_script()
    
    def _generate_windows_script(self):
        """
        Generate PowerShell script for Windows
        """
        script_content = '''
        # WiFi Auto Connect Script
        $ErrorActionPreference = "Stop"
        [Console]::CursorVisible = $false

        # Load credentials from file
        $credentialsFile = Join-Path -Path $HOME -ChildPath ".wifi_auto_login/credentials.json"
        try {
            $credentials = Get-Content -Path $credentialsFile -Raw | ConvertFrom-Json
            $wifiSSID = $credentials.ssid
            $USERNAME = $credentials.username
            $PASSWORD = $credentials.password
        } catch {
            Write-Host "Error loading credentials: $_"
            exit 1
        }

            
        # Get connected SSID
        function Get-ConnectedSSID {
            $output = netsh wlan show interfaces
            $match = ($output | Select-String '^\s*SSID\s*:\s*(.+)$')
            if ($match) {
                return ($match.Matches.Groups[1].Value.Trim())
            }
            return $null
        }

        # Connect to WiFi
        function Connect-ToWiFi {
            Write-Host "Connecting to Wi-Fi: $wifiSSID ..."
            netsh wlan connect name="$wifiSSID" | Out-Null
            Start-Sleep -Seconds 4
            $ssid = Get-ConnectedSSID
            if ($ssid -ieq $wifiSSID) {
                return $true
            }
            return $false
        }

        # Detect Captive Portal (Windows-independent)
        function NeedsLogin {
            try {
                $response = Invoke-WebRequest -Uri "http://detectportal.firefox.com/success.txt" -UseBasicParsing -TimeoutSec 5
                return ($response.StatusCode -ne 200 -or $response.Content.Trim() -ne "success")
            } catch {
                return $true
            }
        }

        # Main
        if (-not (Connect-ToWiFi)) {
            Write-Host "Could not verify Wi-Fi connection. Proceeding anyway..."
        }

        if (NeedsLogin) {
            Write-Host "Attempting to log in to the captive portal..."
            try {
                Invoke-WebRequest -Uri $LOGIN_URL -Method POST -Body @{
                    "userId"      = $USERNAME
                    "password"    = $PASSWORD
                    "serviceName" = "ProntoAuthentication"
                } -UseBasicParsing -TimeoutSec 10 | Out-Null

                Show-Spinner -Duration 2
                Write-Host "`nConnected successfully without browser pop-up!"
            } catch {
                Write-Host "Login failed. Please check your credentials or network."
            }
        } else {
            Write-Host "Already connected. No captive portal detected."
        }

        [Console]::CursorVisible = $true
        '''
        # Write the PowerShell script
        with open(self.script_path, 'w') as f:
            f.write(script_content)

    def _generate_linux_script(self):
        """
        Generate shell script for Linux
        """
        script_content = '''#!/bin/bash
        # WiFi Auto Connect Script for Linux

        # Hide the cursor
        tput civis

        # Load credentials from file
        CREDENTIALS_FILE="$HOME/.wifi_auto_login/credentials.json"
        if [ ! -f "$CREDENTIALS_FILE" ]; then
            echo "Credentials file not found: $CREDENTIALS_FILE"
            exit 1
        fi

        # Parse JSON - requires jq
        if ! command -v jq &> /dev/null; then
            echo "Error: jq is required but not installed. Please install jq."
            exit 1
        fi

        WIFI_SSID=$(jq -r '.ssid' "$CREDENTIALS_FILE")
        USERNAME=$(jq -r '.username' "$CREDENTIALS_FILE")
        PASSWORD=$(jq -r '.password' "$CREDENTIALS_FILE")

        # URL for login submission
        LOGIN_URL="http://phc.prontonetworks.com/cgi-bin/authlogin?URI=http://detectportal.firefox.com/canonical.html"


        # Connect to Wi-Fi network
        echo "Connecting to Wi-Fi: $WIFI_SSID ..."
        nmcli dev wifi connect "$WIFI_SSID" || {
            echo "Failed to connect to $WIFI_SSID"
            tput cnorm  # Show cursor before exit
            exit 1
        }

        # Make the login request silently
        echo "Attempting to log in to captive portal..."
        {
            curl -X POST "$LOGIN_URL" \\
                -d "userId=$USERNAME" \\
                -d "password=$PASSWORD" \\
                -d "serviceName=ProntoAuthentication" \\
                -s -o /dev/null 
        } && echo "Connected successfully!" || echo "Failed to connect. Please check your credentials or network."

        # Show the cursor again
        tput cnorm
        '''
        # Write the shell script
        with open(self.script_path, 'w') as f:
            f.write(script_content)
        
        # Make it executable
        os.chmod(self.script_path, os.stat(self.script_path).st_mode | stat.S_IXUSR | stat.S_IXGRP)

    def _generate_macos_script(self):
        """
        Generate shell script for macOS
        """
        script_content ='''#!/bin/bash
        # WiFi Auto Connect Script for Linux

        # Hide the cursor
        tput civis

        # Load credentials from file
        CREDENTIALS_FILE="$HOME/.wifi_auto_login/credentials.json"
        if [ ! -f "$CREDENTIALS_FILE" ]; then
            echo "Credentials file not found: $CREDENTIALS_FILE"
            exit 1
        fi

        # Parse JSON - requires jq
        if ! command -v jq &> /dev/null; then
            echo "Error: jq is required but not installed. Please install jq."
            exit 1
        fi

        WIFI_SSID=$(jq -r '.ssid' "$CREDENTIALS_FILE")
        USERNAME=$(jq -r '.username' "$CREDENTIALS_FILE")
        PASSWORD=$(jq -r '.password' "$CREDENTIALS_FILE")

       # URL for login submission
        LOGIN_URL="http://phc.prontonetworks.com/cgi-bin/authlogin?URI=http://detectportal.firefox.com/canonical.html"

        # Connect to the Wi-Fi network
        echo "Connecting to the Wi-Fi..."
        networksetup -setairportnetwork "$WIFI_SSID"

        # Wait a few seconds to ensure the connection is up
        sleep 5

        # Make the login request
        echo "Logging in to captive portal..."
        {
            curl -X POST "$LOGIN_URL" \
                -d "userId=$USERNAME" \
                -d "password=$PASSWORD" \
                -d "serviceName=ProntoAuthentication" \
                -s -o /dev/null
        } && echo "Connected successfully!" || echo "Failed to connect. Please check your credentials or network."

        # Show the cursor again
        tput cnorm
        '''
        # Write the shell script
        with open(self.script_path, 'w') as f:
            f.write(script_content)
        
        # Make it executable
        os.chmod(self.script_path, os.stat(self.script_path).st_mode | stat.S_IXUSR | stat.S_IXGRP)

    def _create_startup_entry(self):
        """
        Create the appropriate startup entry based on the OS
        """
        if self.os_type == "Windows":
            self._create_windows_startup()
        elif self.os_type == "Linux":
            self._create_linux_startup()
        elif self.os_type == "Darwin":  # macOS
            self._create_macos_startup()

    def _create_windows_startup(self):
        """
        Create Windows startup entry using registry
        """
        try:
            # Convert to string path for registry
            script_path_str = str(self.script_path)
            
            # Use PowerShell to run the script
            powershell_command = f'powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "{script_path_str}"'
            
            # Create registry key
            registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, registry_path, 0, reg.KEY_WRITE)
            reg.SetValueEx(registry_key, self.app_name, 0, reg.REG_SZ, powershell_command)
            reg.CloseKey(registry_key)
            
            print(f"Windows startup entry created for {self.app_name}")
            return True
        except Exception as e:
            print(f"Failed to create Windows startup entry: {e}")
            return False

    def _create_linux_startup(self):
        """
        Create Linux startup entry using .desktop file
        """
        try:
            # Create autostart directory if it doesn't exist
            autostart_dir = Path.home() / ".config" / "autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            
            # Create .desktop file
            desktop_file_path = autostart_dir / f"{self.app_name.lower()}.desktop"
            
            desktop_content = f"""[Desktop Entry]
            Name={self.app_name}
            Exec={self.script_path}
            Type=Application
            X-GNOME-Autostart-enabled=true
            """
            
            with open(desktop_file_path, 'w') as f:
                f.write(desktop_content)
            
            # Make it executable
            os.chmod(desktop_file_path, os.stat(desktop_file_path).st_mode | stat.S_IXUSR | stat.S_IXGRP)
            
            print(f"Linux startup entry created at {desktop_file_path}")
            return True
        except Exception as e:
            print(f"Failed to create Linux startup entry: {e}")
            return False

    def _create_macos_startup(self):
        """
        Create macOS startup entry using LaunchAgent
        """
        try:
            # Create LaunchAgents directory if it doesn't exist
            launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
            launch_agents_dir.mkdir(parents=True, exist_ok=True)
            
            # Create plist file
            plist_file_path = launch_agents_dir / f"com.{self.app_name.lower()}.autoconnect.plist"
            
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>com.{self.app_name.lower()}.autoconnect</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{self.script_path}</string>
                </array>
                <key>RunAtLoad</key>
                <true/>
                <key>KeepAlive</key>
                <false/>
            </dict>
            </plist>
            """
            
            with open(plist_file_path, 'w') as f:
                f.write(plist_content)
            
            # Load the plist file
            try:
                subprocess.run(['launchctl', 'load', str(plist_file_path)], check=True)
            except subprocess.CalledProcessError:
                print("Warning: Could not load the LaunchAgent immediately. It will load on next login.")
            
            print(f"macOS startup entry created and loaded at {plist_file_path}")
            return True
        except Exception as e:
            print(f"Failed to create macOS startup entry: {e}")
            return False

    # def remove_startup(self):
    #     """
    #     Remove startup entries and scripts
    #     """
    #     try:
    #         # Remove startup entry
    #         if self.os_type == "Windows":
    #             self._remove_windows_startup()
    #         elif self.os_type == "Linux":
    #             self._remove_linux_startup()
    #         elif self.os_type == "Darwin":  # macOS
    #             self._remove_macos_startup()
            
    #         # Remove script file if it exists
    #         if self.script_path.exists():
    #             os.remove(self.script_path)
            
    #         # Try to remove scripts directory if empty
    #         if self.scripts_dir.exists() and not any(self.scripts_dir.iterdir()):
    #             self.scripts_dir.rmdir()
                
    #         return True, f"Startup configuration removed for {self.os_type}"
    #     except Exception as e:
    #         return False, f"Failed to remove startup: {str(e)}"

    # def _remove_windows_startup(self):
    #     """Remove Windows startup entry"""
    #     try:
    #         registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    #         registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, registry_path, 0, reg.KEY_WRITE)
    #         reg.DeleteValue(registry_key, self.app_name)
    #         reg.CloseKey(registry_key)
    #     except FileNotFoundError:
    #         # Key doesn't exist, that's fine
    #         pass
    #     except Exception as e:
    #         print(f"Warning: Failed to remove Windows registry key: {e}")

    # def _remove_linux_startup(self):
    #     """Remove Linux startup entry"""
    #     desktop_file_path = Path.home() / ".config" / "autostart" / f"{self.app_name.lower()}.desktop"
    #     if desktop_file_path.exists():
    #         os.remove(desktop_file_path)

    # def _remove_macos_startup(self):
    #     """Remove macOS startup entry"""
    #     plist_file_path = Path.home() / "Library" / "LaunchAgents" / f"com.{self.app_name.lower()}.autoconnect.plist"
    #     if plist_file_path.exists():
    #         try:
    #             # Unload first
    #             subprocess.run(['launchctl', 'unload', str(plist_file_path)], check=False)
    #         except Exception:
    #             pass
    #         os.remove(plist_file_path)
