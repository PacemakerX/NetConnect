import json
from pathlib import Path

class UserManager:
    """UserManager handles user credentials management for WiFi auto-login functionality.
    This class provides methods to create, edit and manage WiFi login credentials including
    SSID, username and password. Credentials are stored in JSON format in the user's home
    directory.
    Attributes:
        credentials_file (Path): Path object pointing to the JSON file storing credentials
            Located at ~/.wifi_auto_login/credentials.json
    Methods:
        create_new_user(): 
            Interactive prompt to create new user credentials.
            Gets SSID, username and password from user input.
            Validates that all fields are provided.
            Saves credentials to JSON file.
        edit_existing_user():
            Interactive prompt to edit existing credentials.
            Shows current SSID and username.
            Allows editing SSID, username or password.
            Updates JSON file with new credentials.
        _save_credentials(data):
            Internal method to save credentials dict to JSON file.
            Args:
                data (dict): Dictionary containing credentials to save
        _load_credentials():
            Internal method to load credentials from JSON file.
            Returns:
                dict: Dictionary containing stored credentials
    Raises:
        FileNotFoundError: If credentials file doesn't exist when trying to load
        JSONDecodeError: If credentials file contains invalid JSON
        PermissionError: If there are filesystem permission issues
    Example:
        manager = UserManager()
        manager.create_new_user()  # Create new credentials
        manager.edit_existing_user()  # Edit existing credentials
    """
    def __init__(self):
        self.credentials_file = Path.home() / ".wifi_auto_login" / "credentials.json"
        self.credentials_file.parent.mkdir(parents=True, exist_ok=True)

    def create_new_user(self):
        ssid = input("Enter Wi-Fi SSID ( NAME OF WIFI e.g G-VIT,LHG-VIT,E-VIT): ").strip()
        username = input("Enter Username: ").strip()
        password = input("Enter Password: ").strip()

        if not ssid or not username or not password:
            print("All fields are required.")
            return self.create_new_user()

        credentials = {
            "ssid": ssid,
            "username": username,
            "password": password
        }

        self._save_credentials(credentials)
        print(" Credentials saved successfully.")

    def edit_existing_user(self):
        if not self.credentials_file.exists():
            print(" No credentials found. Please create a new user first.")
            return

        credentials = self._load_credentials()

        print(f"\nCurrent SSID: {credentials['ssid']}")
        print(f"Current Username: {credentials['username']}")
        print("[1] Edit SSID\n[2] Edit Username\n[3] Edit Password\n[4] Back")

        choice = input("Select field to edit: ").strip()
        if choice == '1':
            credentials['ssid'] = input("New SSID: ").strip()
        elif choice == '2':
            credentials['username'] = input("New Username: ").strip()
        elif choice == '3':
            credentials['password'] = input("New Password: ").strip()
        elif choice == '4':
            return
        else:
            print("Invalid choice.")
            return self.edit_existing_user()

        self._save_credentials(credentials)
        print(" Updated successfully.")

    def _save_credentials(self, data):
        with open(self.credentials_file, "w") as f:
            json.dump(data, f)

    def _load_credentials(self):
        with open(self.credentials_file, "r") as f:
            return json.load(f)
