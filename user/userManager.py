import json
from pathlib import Path

class UserManager:
    def __init__(self):
        self.credentials_file = Path.home() / ".wifi_auto_login" / "credentials.json"
        self.credentials_file.parent.mkdir(parents=True, exist_ok=True)

    def create_new_user(self):
        ssid = input("Enter Wi-Fi SSID: ").strip()
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
