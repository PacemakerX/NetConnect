from user.userManager import UserManager

class MenuHandler:
    """
    A class to handle the menu system and user interaction flow.

    This class manages the main menu interface and different user flows (new/existing users).
    It acts as a bridge between the user interface and the UserManager functionality.

    Attributes:
        user_manager (UserManager): An instance of UserManager class to handle user-related operations.
    """

    def __init__(self):
        """Initialize MenuHandler with a UserManager instance."""
        self.user_manager = UserManager()

    def main_menu(self):
        """
        Display and handle the main menu options.

        Presents three options to the user:
        1. Create a new user
        2. Access existing user menu
        3. Exit the program

        The method uses recursive calls for invalid inputs.
        """
        print("\n[1] New User")
        print("[2] Existing User")
        print("[3] Exit")

        choice = input("\nEnter choice: ").strip()

        # Dictionary mapping choices to their corresponding methods
        menu_options = {
            '1': self.new_user_flow,
            '2': self.existing_user_flow,
            '3': self._exit_program
        }

        if choice in menu_options:
            menu_options[choice]()
        else:
            print("Invalid choice. Try again.")
            self.main_menu()

    def new_user_flow(self):
        """
        Handle the new user registration flow.
        
        Displays the new user setup header and delegates user creation
        to the UserManager instance.
        """
        print("\n--- New User Setup ---")
        self.user_manager.create_new_user()

    def existing_user_flow(self):
        """
        Handle the existing user menu flow.
        
        Displays the existing user menu header and delegates user editing
        to the UserManager instance.
        """
        print("\n--- Existing User Menu ---")
        self.user_manager.edit_existing_user()

    def _exit_program(self):
        """
        Handle program exit.
        
        Displays exit message and terminates the program.
        """
        print("Exiting...")
        exit(0)
