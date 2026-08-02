from datetime import datetime


# ---------------------------------------------------------------------------
# Driver status constants
# ---------------------------------------------------------------------------
STATUS_AVAILABLE = "AVAILABLE"
STATUS_ASSIGNED  = "ASSIGNED"
STATUS_ON_LEAVE  = "ON_LEAVE"


class Driver:
    """
    Data-holder class representing an ABC-Trans driver.

    Attributes:
        driver_id       (str)  : Unique system-generated identifier.
        full_name       (str)  : Driver's full name.
        licence_number  (str)  : Driver's vehicle licence number.
        licence_expiry  (str)  : Licence expiry date (YYYY-MM-DD).
        phone           (str)  : Driver's contact phone number.
        branch_id       (str)  : ID of the branch this driver belongs to.
        status          (str)  : Current status of the driver.
        leave_note      (str)  : Reason for leave (if on leave).
    """

    def __init__(
        self,
        driver_id: str,
        full_name: str,
        licence_number: str,
        licence_expiry: str,
        phone: str,
        branch_id: str,
        status: str = STATUS_AVAILABLE,
        leave_note: str = ""
    ):
        self.driver_id      = driver_id
        self.full_name      = full_name
        self.licence_number = licence_number
        self.licence_expiry = licence_expiry
        self.phone          = phone
        self.branch_id      = branch_id
        self.status         = status
        self.leave_note     = leave_note

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def is_available(self) -> bool:
        """Return True if the driver is available for assignment."""
        return self.status == STATUS_AVAILABLE

    def is_licence_valid(self) -> bool:
        """
        Return True if the driver's licence has not expired.
        Compares licence expiry date against today's date.
        """
        try:
            expiry = datetime.strptime(self.licence_expiry, "%Y-%m-%d").date()
            return expiry >= datetime.today().date()
        except ValueError:
            return False

    # -----------------------------------------------------------------------
    # Serialisation
    # -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convert the Driver object to a dictionary for JSON storage."""
        return {
            "driver_id"      : self.driver_id,
            "full_name"      : self.full_name,
            "licence_number" : self.licence_number,
            "licence_expiry" : self.licence_expiry,
            "phone"          : self.phone,
            "branch_id"      : self.branch_id,
            "status"         : self.status,
            "leave_note"     : self.leave_note
        }

    @staticmethod
    def from_dict(data: dict) -> "Driver":
        """Create a Driver object from a dictionary loaded from JSON."""
        return Driver(
            driver_id      = data["driver_id"],
            full_name      = data["full_name"],
            licence_number = data["licence_number"],
            licence_expiry = data["licence_expiry"],
            phone          = data["phone"],
            branch_id      = data["branch_id"],
            status         = data.get("status", STATUS_AVAILABLE),
            leave_note     = data.get("leave_note", "")
        )

    def __repr__(self) -> str:
        return (
            f"Driver(id={self.driver_id}, "
            f"name={self.full_name}, "
            f"status={self.status})"
        )