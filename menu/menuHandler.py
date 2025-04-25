from user.userManager import UserManager

class MenuHandler:
    def __init__(self):
        self.user_manager = UserManager()

    def main_menu(self):
        print("\n[1] New User")
        print("[2] Existing User")
        print("[3] Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == '1':
            self.new_user_flow()
        elif choice == '2':
            self.existing_user_flow()
        elif choice == '3':
            print("Exiting...")
            exit(0)
        else:
            print("Invalid choice. Try again.")
            self.main_menu()

    def new_user_flow(self):
        print("\n--- New User Setup ---")
        self.user_manager.create_new_user()

    def existing_user_flow(self):
        print("\n--- Existing User Menu ---")
        self.user_manager.edit_existing_user()
