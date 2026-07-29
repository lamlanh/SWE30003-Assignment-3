import hashlib


# ---------------------------------------------------------------------------
# Role constants
# ---------------------------------------------------------------------------
ROLE_CUSTOMER = "CUSTOMER"
ROLE_STAFF    = "STAFF"
ROLE_ADMIN    = "ADMIN"

# Maximum failed login attempts before account lockout
MAX_FAILED_ATTEMPTS = 5


class AuthenticationManager:
    """
    Manages authentication and session control for SmartFM.

    Responsibilities (from CRC Card 11):
        - Validate user credentials (username and password)
        - Enforce role-based access control for all system actions
        - Lock account after 5 consecutive failed login attempts
        - Manage user sessions (login, logout, session expiry)

    Collaborators:
        - Customer (data-holder)
        - SmartFMSystem
    """

    def __init__(self):
        """
        Initialise AuthenticationManager.
        Sets up session tracking and failed attempt counter.
        """
        # Currently logged-in user session
        # Format: { "user_id": str, "username": str, "role": str }
        self._current_session = None

        # Track failed login attempts per username
        # Format: { "username": int }
        self._failed_attempts = {}

        # Track locked accounts
        # Format: { "username": True }
        self._locked_accounts = {}

    # -----------------------------------------------------------------------
    # Password hashing
    # -----------------------------------------------------------------------
    def hash_password(self, plain_password: str) -> str:
        """
        Hash a plain-text password using SHA-256.

        Args:
            plain_password (str): The raw password entered by the user.

        Returns:
            str: The SHA-256 hex digest of the password.
        """
        return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()

    def verify_password(self, plain_password: str, stored_hash: str) -> bool:
        """
        Verify a plain-text password against a stored hash.

        Args:
            plain_password (str): The raw password entered by the user.
            stored_hash    (str): The hashed password stored in the system.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self.hash_password(plain_password) == stored_hash

    # -----------------------------------------------------------------------
    # Login / Logout
    # -----------------------------------------------------------------------
    def login(
        self,
        username: str,
        plain_password: str,
        stored_hash: str,
        user_id: str,
        role: str = ROLE_CUSTOMER
    ) -> tuple:
        """
        Attempt to log a user in.

        Args:
            username       (str): The username entered by the user.
            plain_password (str): The raw password entered by the user.
            stored_hash    (str): The hashed password from the system.
            user_id        (str): The unique ID of the user.
            role           (str): The role of the user (default: CUSTOMER).

        Returns:
            tuple: (success: bool, message: str)
        """
        # Check if account is locked
        if self.is_locked(username):
            return False, (
                f"Account '{username}' is locked after "
                f"{MAX_FAILED_ATTEMPTS} failed attempts. "
                "Please contact support."
            )

        # Verify the password
        if not self.verify_password(plain_password, stored_hash):
            self._record_failed_attempt(username)
            attempts = self._failed_attempts.get(username, 0)
            remaining = MAX_FAILED_ATTEMPTS - attempts

            if remaining <= 0:
                self._locked_accounts[username] = True
                return False, (
                    f"Account '{username}' has been locked after "
                    f"{MAX_FAILED_ATTEMPTS} failed attempts."
                )

            return False, (
                f"Incorrect password. "
                f"{remaining} attempt(s) remaining."
            )

        # Password correct — create session
        self._reset_failed_attempts(username)
        self._current_session = {
            "user_id"  : user_id,
            "username" : username,
            "role"     : role
        }
        return True, f"Welcome, {username}!"

    def logout(self) -> None:
        """
        Log out the current user and clear the session.
        """
        self._current_session = None

    # -----------------------------------------------------------------------
    # Session info
    # -----------------------------------------------------------------------
    def is_logged_in(self) -> bool:
        """Return True if a user is currently logged in."""
        return self._current_session is not None

    def get_current_user(self) -> dict:
        """
        Return the current session dictionary.

        Returns:
            dict: { user_id, username, role } or None if not logged in.
        """
        return self._current_session

    def get_current_user_id(self) -> str:
        """Return the current logged-in user's ID, or None."""
        if self._current_session:
            return self._current_session["user_id"]
        return None

    def get_current_role(self) -> str:
        """Return the current logged-in user's role, or None."""
        if self._current_session:
            return self._current_session["role"]
        return None

    # -----------------------------------------------------------------------
    # Access control
    # -----------------------------------------------------------------------
    def has_role(self, required_role: str) -> bool:
        """
        Check if the current user has the required role.

        Args:
            required_role (str): The role to check against.

        Returns:
            bool: True if the current user has the required role.
        """
        if not self.is_logged_in():
            return False
        return self._current_session["role"] == required_role

    def is_customer(self) -> bool:
        """Return True if the current user is a Customer."""
        return self.has_role(ROLE_CUSTOMER)

    def is_staff(self) -> bool:
        """Return True if the current user is Staff."""
        return self.has_role(ROLE_STAFF)

    def is_admin(self) -> bool:
        """Return True if the current user is an Admin."""
        return self.has_role(ROLE_ADMIN)

    # -----------------------------------------------------------------------
    # Account lockout
    # -----------------------------------------------------------------------
    def is_locked(self, username: str) -> bool:
        """
        Check if a user account is locked.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if the account is locked.
        """
        return self._locked_accounts.get(username, False)

    def _record_failed_attempt(self, username: str) -> None:
        """
        Increment the failed login attempt counter for a username.

        Args:
            username (str): The username that failed to log in.
        """
        self._failed_attempts[username] = (
            self._failed_attempts.get(username, 0) + 1
        )

    def _reset_failed_attempts(self, username: str) -> None:
        """
        Reset the failed attempt counter after a successful login.

        Args:
            username (str): The username that logged in successfully.
        """
        self._failed_attempts[username] = 0

    def unlock_account(self, username: str) -> None:
        """
        Unlock a locked account (admin action).

        Args:
            username (str): The username to unlock.
        """
        self._locked_accounts[username] = False
        self._failed_attempts[username] = 0

    def __repr__(self) -> str:
        logged_in = self._current_session["username"] if self._current_session else "None"
        return f"AuthenticationManager(current_user={logged_in})"