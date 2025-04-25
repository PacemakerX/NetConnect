import platform
import subprocess
import sys
from abc import ABC, abstractmethod

class WiFiConnector(ABC):
    def __init__(self, ssid):
        self.ssid = ssid

    @abstractmethod
    def connect(self):
        pass

class WindowsWiFiConnector(WiFiConnector):
    def connect(self):
        try:
            result = subprocess.run(["netsh", "wlan", "connect", f"name={self.ssid}"], capture_output=True, text=True)
            if "Connection request was completed successfully" in result.stdout:
                print(f"✅ Connected to {self.ssid} on Windows.")
            else:
                print(f"⚠️ Connection may have failed:\n{result.stdout}")
        except Exception as e:
            print(f"❌ Error connecting on Windows: {e}")
            sys.exit(1)

class LinuxWiFiConnector(WiFiConnector):
    def connect(self):
        try:
            subprocess.run(["nmcli", "dev", "wifi", "connect", self.ssid], check=True)
            print(f" Connected to {self.ssid} on Linux.")
        except FileNotFoundError:
            print(" nmcli not found. Are you on a minimal distro?")
            sys.exit(1)
        except subprocess.CalledProcessError:
            print(" Failed to connect on Linux.")
            sys.exit(1)

class MacOSWiFiConnector(WiFiConnector):
    def __init__(self, ssid, interface="Wi-Fi"):
        super().__init__(ssid)
        self.interface = interface

    def connect(self):
        try:
            subprocess.run(["networksetup", "-setairportnetwork", self.interface, self.ssid], check=True)
            print(f" Connected to {self.ssid} on macOS.")
        except subprocess.CalledProcessError:
            print(" Failed to connect on macOS. Check SSID or interface.")
            sys.exit(1)

def get_connector(ssid):
    os_type = platform.system()

    if os_type == "Windows":
        return WindowsWiFiConnector(ssid)
    elif os_type == "Linux":
        return LinuxWiFiConnector(ssid)
    elif os_type == "Darwin":
        return MacOSWiFiConnector(ssid)
    else:
        print(" Unsupported OS for auto Wi-Fi connection.")
        sys.exit(1)
