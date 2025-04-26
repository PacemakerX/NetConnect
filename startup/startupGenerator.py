import os
import platform
from pathlib import Path
import stat
import subprocess

try:
    import winreg as reg  # For Windows registry
except ImportError:
    pass  # Not on Windows

class StartupGenerator:
    """
    A class that generates and manages startup scripts for automatic WiFi connection across different operating systems.
    
    This class handles:
    - Creation of platform-specific startup scripts
    - Management of startup entries in system startup mechanisms
    - OS-specific file path handling
    - Script generation for Windows (PowerShell), Linux (Bash), and macOS (Bash)
    
    Attributes:
        app_name (str): Name of the application, defaults to "NetConnect"
        os_type (str): Current operating system (Windows/Linux/Darwin)
        credentials_file (Path): Path to the JSON file storing WiFi credentials
        scripts_dir (Path): Directory where connection scripts will be stored
        script_path (Path): Full path to the connection script file
    
    Supported Operating Systems:
        - Windows: Uses PowerShell scripts and registry for startup
        - Linux: Uses Bash scripts and .desktop files for startup
        - macOS: Uses Bash scripts and LaunchAgents for startup
    
    File Structure:
        Windows:
            - Scripts: %LOCALAPPDATA%/NetConnect/
            - Credentials: %USERPROFILE%/.wifi_auto_login/credentials.json
        Linux:
            - Scripts: ~/.local/share/netconnect/
            - Credentials: ~/.wifi_auto_login/credentials.json
        macOS:
            - Scripts: ~/Library/Application Support/NetConnect/
            - Credentials: ~/.wifi_auto_login/credentials.json
    """

    def __init__(self, app_name="NetConnect"):
        """
        Initialize the StartupGenerator with required paths and system information.
        
        Args:
            app_name (str): Name of the application, used for file paths and startup entries.
                          Defaults to "NetConnect"
        
        Raises:
            OSError: If the current operating system is not supported
                    (must be Windows, Linux, or macOS)
        """
        self.app_name = app_name
        self.os_type = platform.system()
        self.credentials_file = Path.home() / ".wifi_auto_login" / "credentials.json"
        
        # Define OS-specific script locations
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
        Main method to setup automatic startup configuration for the detected operating system.

        This method performs the following steps:
        1. Creates necessary directories for storing scripts
        2. Generates OS-specific connection script (PowerShell/Bash)
        3. Creates system startup entry to run the script at boot

        Returns:
            tuple: (success, message)
                - success (bool): True if setup was successful, False otherwise
                - message (str): Descriptive message about the operation result

        Raises:
            OSError: If there are permission issues creating directories
            IOError: If there are issues writing the script files
            Exception: For any other unexpected errors during setup

        Example:
            success, msg = startup_gen.setup_startup()
            if success:
                print("Startup configured successfully")
            else:
                print(f"Setup failed: {msg}")
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
        Generate the appropriate connection script based on the detected operating system.

        This method acts as a dispatcher that:
        1. Ensures the scripts directory exists
        2. Calls the appropriate OS-specific script generator:
           - Windows: Generates PowerShell script
           - Linux: Generates Bash script with proper permissions
           - macOS: Generates Bash script with proper permissions

        The generated scripts are stored in OS-specific locations:
        - Windows: %LOCALAPPDATA%/NetConnect/wifi_connect.ps1
        - Linux: ~/.local/share/netconnect/wifi_connect.sh
        - macOS: ~/Library/Application Support/NetConnect/wifi_connect.sh

        Raises:
            OSError: If directory creation fails
            IOError: If script writing fails
            ValueError: If the operating system is not supported
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
        Generate PowerShell script for Windows automatic WiFi connection.

        This method creates a PowerShell script that:
        1. Loads WiFi credentials from a JSON file
        2. Attempts to connect to the specified WiFi network
        3. Handles captive portal authentication if needed
        4. Provides visual feedback during the connection process

        Script Features:
        - Error handling for credential loading and network operations
        - Cursor visibility management for better UI
        - Network connection status verification
        - Captive portal detection and automated login
        - Progress indication during connection attempts

        Script Location:
            %LOCALAPPDATA%/NetConnect/wifi_connect.ps1

        Required Credentials Format (JSON):
        {
            "ssid": "WiFi-Network-Name",
            "username": "Registration Number",
            "password": "password123"
        }

        PowerShell Functions:
        - Get-ConnectedSSID: Retrieves currently connected WiFi network name
        - Connect-ToWiFi: Handles WiFi connection using Windows native commands
        - NeedsLogin: Detects if captive portal authentication is required

        Note:
            The script requires PowerShell execution policy to allow script execution,
            which is handled by the startup configuration process.
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

            # Set Captive Portal Login URL
            $LOGIN_URL = "$LOGIN_URL = "http://phc.prontonetworks.com/cgi-bin/authlogin?URI=http://detectportal.firefox.com/canonical.html"

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

            # Detect Captive Portal
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

                    Write-Host "`nConnected successfully without browser pop-up!"
                } catch {
                    Write-Host "Login failed. Please check your credentials or network."
                }
            } else {
                Write-Host "Already connected. No captive portal detected."
            }

            Write-Host "Connection setup complete. Stabilizing..."
            Start-Sleep -Seconds 90  # Hold script alive for 90 seconds after login to stabilize

            [Console]::CursorVisible = $true
            '''
            
            # Write the PowerShell script
        with open(self.script_path, 'w') as f:
            f.write(script_content)

    def _generate_linux_script(self):
        """
        Generate a bash script for Linux systems to handle automatic WiFi connection and captive portal authentication.

        This method creates a shell script that:
        1. Loads WiFi credentials from a JSON file
        2. Connects to the specified WiFi network using nmcli
        3. Handles captive portal authentication
        4. Provides visual feedback during the connection process

        Script Features:
        - JSON credential parsing using jq
        - Network connection using NetworkManager (nmcli)
        - Cursor visibility management for better UI
        - Error handling for credential loading and network operations
        - Silent curl operations for portal authentication
        - Progress indication during connection attempts

        Script Location:
            ~/.local/share/netconnect/wifi_connect.sh

        Required Dependencies:
            - jq: JSON parser (script checks for its presence)
            - nmcli: NetworkManager command line interface
            - curl: For HTTP requests
            - tput: For terminal cursor control

        Required Credentials Format (JSON):
        {
            "ssid": "WiFi-Network-Name",
            "username": "Registration Number",
            "password": "password123"
        }

        Script Flow:
        1. Check for credentials file
        2. Verify jq installation
        3. Extract credentials using jq
        4. Attempt WiFi connection using nmcli
        5. Perform captive portal authentication if needed
        6. Display connection status

        Raises:
            OSError: If there are permission issues writing the script
            IOError: If there are issues making the script executable

        Note:
            The script is made executable after creation using chmod
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
        Generate a bash script for macOS systems to handle automatic WiFi connection and captive portal authentication.

        This method creates a shell script that:
        1. Loads WiFi credentials from a JSON file
        2. Connects to the specified WiFi network using networksetup
        3. Handles captive portal authentication
        4. Provides visual feedback during the connection process

        Script Features:
        - JSON credential parsing using jq
        - Network connection using networksetup (macOS native)
        - Cursor visibility management for better UI
        - Error handling for credential loading and network operations
        - Silent curl operations for portal authentication
        - Progress indication during connection attempts

        Script Location:
            ~/Library/Application Support/NetConnect/wifi_connect.sh

        Required Dependencies:
        - jq: JSON parser (script checks for its presence)
        - networksetup: macOS network configuration utility
        - curl: For HTTP requests
        - tput: For terminal cursor control

        Required Credentials Format (JSON):
        {
            "ssid": "WiFi-Network-Name",
            "username": "Registration Number", 
            "password": "password123"
        }

        Script Flow:
        1. Hide cursor for cleaner output
        2. Check for credentials file existence
        3. Verify jq installation
        4. Extract credentials using jq
        5. Attempt WiFi connection using networksetup
        6. Perform captive portal authentication if needed
        7. Display connection status
        8. Restore cursor visibility

        Raises:
            OSError: If there are permission issues writing the script
            IOError: If there are issues making the script executable
            
        Note:
            The script is made executable after creation using chmod
            The script handles macOS-specific network configuration
            Uses tput for terminal manipulation
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
        Create an appropriate startup entry for the detected operating system.

        This method acts as a dispatcher that calls the appropriate OS-specific startup entry creation method:
        - Windows: Creates registry entry to run PowerShell script
        - Linux: Creates .desktop file in autostart directory
        - macOS: Creates and loads a LaunchAgent plist file

        Each OS-specific method handles:
        - Creation of necessary startup directories
        - Writing startup configuration files
        - Setting appropriate permissions
        - Registering with OS startup mechanism

        Returns:
            bool: Success status of the startup entry creation

        Raises:
            OSError: If permission issues prevent startup entry creation
            Exception: For other OS-specific startup configuration issues
        """
        if self.os_type == "Windows":
            self._create_windows_startup()
        elif self.os_type == "Linux":
            self._create_linux_startup()
        elif self.os_type == "Darwin":  # macOS
            self._create_macos_startup()

    def _create_windows_startup(self):
        """
        Create Windows startup entry using the Windows Registry.

        This method:
        1. Converts the script path to a proper Windows path string
        2. Creates a PowerShell command with appropriate execution policy
        3. Adds an entry to the Windows Registry under HKEY_CURRENT_USER

        Registry Configuration:
        - Key: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
        - Value Name: Application name (self.app_name)
        - Value Type: REG_SZ (string)
        - Value Data: PowerShell command to execute script

        PowerShell Execution:
        - Uses -ExecutionPolicy Bypass for script execution
        - Runs in hidden window mode
        - Executes the connection script at startup

        Returns:
            bool: True if successful, False otherwise

        Raises:
            WindowsError: If registry operations fail
            PermissionError: If insufficient privileges
        """
        try:
            script_path_str = str(self.script_path)
            powershell_command = f'powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "{script_path_str}"'
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
        Create Linux startup entry using XDG autostart mechanism.

        This method:
        1. Creates the autostart directory in user's config
        2. Generates a .desktop file with appropriate entries
        3. Sets executable permissions on the .desktop file

        File Structure:
        - Location: ~/.config/autostart/
        - Filename: <app_name>.desktop
        - Format: XDG Desktop Entry specification

        Desktop Entry Contents:
        - Name: Application name
        - Exec: Path to connection script
        - Type: Application
        - X-GNOME-Autostart-enabled: true

        Required Permissions:
        - Directory: 755 (drwxr-xr-x)
        - .desktop file: 755 (-rwxr-xr-x)

        Returns:
            bool: True if successful, False otherwise

        Raises:
            OSError: If directory/file creation fails
            PermissionError: If setting executable bit fails
        """
        try:
            autostart_dir = Path.home() / ".config" / "autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            desktop_file_path = autostart_dir / f"{self.app_name.lower()}.desktop"
            desktop_content = f"""[Desktop Entry]
            Name={self.app_name}
            Exec={self.script_path}
            Type=Application
            X-GNOME-Autostart-enabled=true
            """
            with open(desktop_file_path, 'w') as f:
                f.write(desktop_content)
            os.chmod(desktop_file_path, os.stat(desktop_file_path).st_mode | stat.S_IXUSR | stat.S_IXGRP)
            print(f"Linux startup entry created at {desktop_file_path}")
            return True
        except Exception as e:
            print(f"Failed to create Linux startup entry: {e}")
            return False

    def _create_macos_startup(self):
        """
        Create macOS startup entry using LaunchAgent to enable automatic script execution at login.
        
        This method:
        1. Creates a LaunchAgents directory in the user's Library folder
        2. Generates a properly formatted .plist file for LaunchAgent configuration
        3. Loads the LaunchAgent using launchctl
        
        LaunchAgent Configuration:
        - Location: ~/Library/LaunchAgents/
        - Filename: com.<app_name>.autoconnect.plist
        - Format: Apple Property List (plist) XML
        
        Plist File Structure:
        - Label: Unique identifier for the LaunchAgent
        - ProgramArguments: Array containing script path
        - RunAtLoad: Set to true for execution at login
        - KeepAlive: Set to false as continuous execution isn't needed
        
        File Permissions:
        - Directory: 755 (drwxr-xr-x)
        - Plist file: 644 (-rw-r--r--)
        
        LaunchAgent Loading:
        - Uses launchctl load command
        - Automatically retries on next login if immediate loading fails
        
        Returns:
            bool: True if successful, False otherwise
        
        Raises:
            OSError: If directory/file creation fails
            subprocess.CalledProcessError: If launchctl loading fails
            Exception: For other unexpected errors
        
        Example plist content:
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.netconnect.autoconnect</string>
            <key>ProgramArguments</key>
            <array>
                <string>/Users/username/Library/Application Support/NetConnect/wifi_connect.sh</string>
            </array>
            <key>RunAtLoad</key>
            <true/>
            <key>KeepAlive</key>
            <false/>
        </dict>
        </plist>
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

# To Be Implmented
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
