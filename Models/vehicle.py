# ---------------------------------------------------------------------------
# Vehicle status constants
# ---------------------------------------------------------------------------
STATUS_AVAILABLE   = "AVAILABLE"
STATUS_ASSIGNED    = "ASSIGNED"
STATUS_MAINTENANCE = "MAINTENANCE"

# Vehicle type constants
TYPE_SMALL  = "SMALL"    # up to 1,000 kg
TYPE_MEDIUM = "MEDIUM"   # up to 5,000 kg
TYPE_LARGE  = "LARGE"    # up to 15,000 kg


class Vehicle:
    """
    Data-holder class representing an ABC-Trans fleet vehicle.

    Attributes:
        vehicle_id       (str)  : Unique system-generated identifier.
        registration     (str)  : Vehicle registration/licence plate number.
        vehicle_type     (str)  : Type of vehicle (SMALL / MEDIUM / LARGE).
        capacity_kg      (float): Maximum cargo capacity in kilograms.
        branch_id        (str)  : ID of the branch this vehicle belongs to.
        status           (str)  : Current status of the vehicle.
        maintenance_note (str)  : Description of maintenance issue (if any).
    """

    def __init__(
        self,
        vehicle_id: str,
        registration: str,
        vehicle_type: str,
        capacity_kg: float,
        branch_id: str,
        status: str = STATUS_AVAILABLE,
        maintenance_note: str = ""
    ):
        self.vehicle_id       = vehicle_id
        self.registration     = registration
        self.vehicle_type     = vehicle_type
        self.capacity_kg      = capacity_kg
        self.branch_id        = branch_id
        self.status           = status
        self.maintenance_note = maintenance_note

    # -----------------------------------------------------------------------
    # Helper
    # -----------------------------------------------------------------------
    def is_available(self) -> bool:
        """Return True if the vehicle is available for assignment."""
        return self.status == STATUS_AVAILABLE

    def can_carry(self, weight_kg: float) -> bool:
        """
        Return True if the vehicle can carry the given cargo weight.

        Args:
            weight_kg (float): Cargo weight to check in kilograms.
        """
        return weight_kg <= self.capacity_kg

    # -----------------------------------------------------------------------
    # Serialisation
    # -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convert the Vehicle object to a dictionary for JSON storage."""
        return {
            "vehicle_id"       : self.vehicle_id,
            "registration"     : self.registration,
            "vehicle_type"     : self.vehicle_type,
            "capacity_kg"      : self.capacity_kg,
            "branch_id"        : self.branch_id,
            "status"           : self.status,
            "maintenance_note" : self.maintenance_note
        }

    @staticmethod
    def from_dict(data: dict) -> "Vehicle":
        """Create a Vehicle object from a dictionary loaded from JSON."""
        return Vehicle(
            vehicle_id       = data["vehicle_id"],
            registration     = data["registration"],
            vehicle_type     = data["vehicle_type"],
            capacity_kg      = data["capacity_kg"],
            branch_id        = data["branch_id"],
            status           = data.get("status", STATUS_AVAILABLE),
            maintenance_note = data.get("maintenance_note", "")
        )

    def __repr__(self) -> str:
        return (
            f"Vehicle(id={self.vehicle_id}, "
            f"reg={self.registration}, "
            f"type={self.vehicle_type}, "
            f"status={self.status})"
        )