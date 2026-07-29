from Manager.account_manager import AccountManager
from Manager.order_manager import OrderManager
from Manager.fleet_manager import FleetManager
from Service.authentication_manager import AuthenticationManager, ROLE_STAFF, ROLE_ADMIN
from Service.notification_service import NotificationService
from Models.customer import Customer


# ---------------------------------------------------------------------------
# SmartFMSystem
# ---------------------------------------------------------------------------
class SmartFMSystem:
    """
    Top-level bootstrap controller for the SmartFM application.

    Responsibilities (from CRC Card 10):
        - Initialise and create all manager and service instances on startup
        - Provide references to subsystems for inter-class communication
        - Handle system-level shutdown and cleanup

    Collaborators:
        - AccountManager
        - OrderManager
        - FleetManager
        - AuthenticationManager
        - NotificationService
    """

    # Singleton instance holder
    _instance = None

    def __new__(cls):
        """
        Enforce Singleton pattern.
        Only one SmartFMSystem instance can exist at runtime.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Declare all subsystem references.
        Actual creation happens in initialise() to allow controlled ordering.
        """
        # Guard against re-initialisation if __init__ is called again
        if hasattr(self, "_initialised") and self._initialised:
            return

        # Subsystem references (set during initialise())
        self._authentication_manager = None
        self._notification_service   = None
        self._fleet_manager          = None
        self._account_manager        = None
        self._order_manager          = None

        # System state
        self._initialised = False
        self._running     = False

    # -----------------------------------------------------------------------
    # Bootstrap
    # -----------------------------------------------------------------------
    def initialise(self) -> None:
        """
        Bootstrap all subsystems in the correct dependency order.

        Initialisation order (from Assignment 2, Section 6):
            1. AuthenticationManager  - must be ready before any user access
            2. NotificationService    - needed by managers during their work
            3. FleetManager           - fleet data needed before orders
            4. AccountManager         - customer accounts needed before orders
            5. OrderManager           - depends on Fleet, Payment, Notification

        Raises:
            RuntimeError: If the system has already been initialised.
        """
        if self._initialised:
            raise RuntimeError("SmartFMSystem has already been initialised.")

        # Step 1 - Authentication (no dependencies)
        print("    [1/5] Starting AuthenticationManager...")
        self._authentication_manager = AuthenticationManager()

        # Step 2 - Notification service (no dependencies)
        print("    [2/5] Starting NotificationService...")
        self._notification_service = NotificationService()

        # Step 3 - Fleet manager (no dependencies)
        print("    [3/5] Starting FleetManager...")
        self._fleet_manager = FleetManager()

        # Step 4 - Account manager (depends on AuthenticationManager)
        print("    [4/5] Starting AccountManager...")
        self._account_manager = AccountManager(
            auth_manager=self._authentication_manager
        )

        # Step 5 - Order manager (depends on Fleet + Notification)
        print("    [5/5] Starting OrderManager...")
        self._order_manager = OrderManager(
            fleet_manager=self._fleet_manager,
            notification_service=self._notification_service
        )

        self._initialised = True
        self._running     = True

        # Step 6 - Seed default staff and admin accounts on first run
        self._seed_default_accounts()

    def _seed_default_accounts(self) -> None:
        """
        Seed default staff and admin accounts on first run.

        Creates the following accounts if they do not already exist:
            staff  / staff123   (STAFF role)
            admin  / admin123   (ADMIN role)

        These accounts are used for testing the staff and admin menus.
        They are only created once — subsequent runs will detect they
        already exist and skip creation.
        """
        # Default accounts to seed
        default_accounts = [
            {
                "username"  : "staff",
                "password"  : "staff123",
                "full_name" : "ABC-Trans Staff",
                "email"     : "staff@abctrans.vn",
                "phone"     : "0241234567",
                "address"   : "ABC-Trans Hanoi Central Branch",
                "role"      : ROLE_STAFF,
                "id_prefix" : "STAFF-001"
            },
            {
                "username"  : "admin",
                "password"  : "admin123",
                "full_name" : "ABC-Trans Admin",
                "email"     : "admin@abctrans.vn",
                "phone"     : "0247654321",
                "address"   : "ABC-Trans Head Office, Hanoi",
                "role"      : ROLE_ADMIN,
                "id_prefix" : "ADMIN-001"
            }
        ]

        for acc in default_accounts:
            # Skip if username already exists
            if self._account_manager.find_by_username(acc["username"]):
                continue

            # Hash the password
            password_hash = self._authentication_manager.hash_password(
                acc["password"]
            )

            # Create the Customer data-holder directly
            # (bypasses registration validation for internal accounts)
            customer = Customer(
                customer_id   = acc["id_prefix"],
                username      = acc["username"],
                password_hash = password_hash,
                full_name     = acc["full_name"],
                email         = acc["email"],
                phone         = acc["phone"],
                address       = acc["address"]
            )

            # Store directly in account manager's internal dictionary
            # and attach role metadata
            self._account_manager._customers[acc["id_prefix"]] = customer

            # Store the role mapping so AuthenticationManager knows the role
            # when this user logs in
            customer._role = acc["role"]

            self._account_manager.save()

    def shutdown(self) -> None:
        """
        Perform a clean system shutdown.
        Saves all in-memory data to persistent storage via each manager.
        """
        if not self._running:
            return

        print("  Saving data and shutting down subsystems...")

        if self._account_manager:
            self._account_manager.save()

        if self._fleet_manager:
            self._fleet_manager.save()

        if self._order_manager:
            self._order_manager.save()

        self._running = False
        print("  Shutdown complete.")

    # -----------------------------------------------------------------------
    # Subsystem accessors
    # These provide controlled access to each subsystem for use by the UI
    # -----------------------------------------------------------------------
    @property
    def authentication_manager(self) -> AuthenticationManager:
        """Return the AuthenticationManager instance."""
        self._check_initialised()
        return self._authentication_manager

    @property
    def notification_service(self) -> NotificationService:
        """Return the NotificationService instance."""
        self._check_initialised()
        return self._notification_service

    @property
    def fleet_manager(self) -> FleetManager:
        """Return the FleetManager instance."""
        self._check_initialised()
        return self._fleet_manager

    @property
    def account_manager(self) -> AccountManager:
        """Return the AccountManager instance."""
        self._check_initialised()
        return self._account_manager

    @property
    def order_manager(self) -> OrderManager:
        """Return the OrderManager instance."""
        self._check_initialised()
        return self._order_manager

    # -----------------------------------------------------------------------
    # Status helpers
    # -----------------------------------------------------------------------
    @property
    def is_running(self) -> bool:
        """Return True if the system is running."""
        return self._running

    @property
    def is_initialised(self) -> bool:
        """Return True if the system has been initialised."""
        return self._initialised

    def _check_initialised(self) -> None:
        """
        Raise an error if a subsystem is accessed before initialisation.

        Raises:
            RuntimeError: If initialise() has not been called yet.
        """
        if not self._initialised:
            raise RuntimeError(
                "SmartFMSystem has not been initialised. "
                "Call initialise() before accessing subsystems."
            )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return (
            f"SmartFMSystem("
            f"initialised={self._initialised}, "
            f"running={self._running})"
        )