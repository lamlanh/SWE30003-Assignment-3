import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for subfolder in ("models", "utils"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

from models.vehicle  import Vehicle
from models.driver   import Driver
from models.branch   import Branch
from utils.json_helper  import JsonHelper
from utils.id_generator import IdGenerator


# ---------------------------------------------------------------------------
# Vehicle and Driver status constants
# ---------------------------------------------------------------------------
VEH_AVAILABLE   = "AVAILABLE"
VEH_ASSIGNED    = "ASSIGNED"
VEH_MAINTENANCE = "MAINTENANCE"

DRV_AVAILABLE   = "AVAILABLE"
DRV_ASSIGNED    = "ASSIGNED"
DRV_ON_LEAVE    = "ON_LEAVE"


class FleetManager:
    """
    Manages vehicle and driver records for SmartFM.

    Responsibilities (CRC Card 4):
        - Add, update, or decommission a vehicle record
        - Add, update, or deactivate a driver record
        - Check vehicle availability for a given cargo weight
        - Check driver availability
        - Assign a vehicle and driver to a confirmed order
        - Flag vehicles under maintenance and exclude from assignments

    Collaborators:
        - Vehicle    (data-holder)
        - Driver     (data-holder)
        - Branch     (data-holder)
        - JsonHelper (storage)
        - IdGenerator
        - OrderManager
        - ShipmentManager
    """

    def __init__(self):
        """Initialise FleetManager and load all fleet data from JSON."""
        self._helper     = JsonHelper()
        self._id_gen     = IdGenerator()

        # In-memory dictionaries
        self._vehicles   = {}   # { vehicle_id: Vehicle }
        self._drivers    = {}   # { driver_id: Driver }
        self._branches   = {}   # { branch_id: Branch }

        self._load()

        # Seed default data on first run if empty
        if not self._vehicles and not self._drivers:
            self._seed_default_data()

    # -----------------------------------------------------------------------
    # Load / Save
    # -----------------------------------------------------------------------
    def _load(self) -> None:
        """Load all fleet records from JSON files into memory."""
        raw_vehicles = self._helper.load("vehicles")
        self._vehicles = {
            vid: Vehicle.from_dict(data)
            for vid, data in raw_vehicles.items()
        }

        raw_drivers = self._helper.load("drivers")
        self._drivers = {
            did: Driver.from_dict(data)
            for did, data in raw_drivers.items()
        }

        raw_branches = self._helper.load("branches")
        self._branches = {
            bid: Branch.from_dict(data)
            for bid, data in raw_branches.items()
        }

    def save(self) -> None:
        """Save all fleet records from memory to JSON files."""
        self._helper.save("vehicles", {
            vid: v.to_dict() for vid, v in self._vehicles.items()
        })
        self._helper.save("drivers", {
            did: d.to_dict() for did, d in self._drivers.items()
        })
        self._helper.save("branches", {
            bid: b.to_dict() for bid, b in self._branches.items()
        })

    # -----------------------------------------------------------------------
    # Default seed data
    # -----------------------------------------------------------------------
    def _seed_default_data(self) -> None:
        """
        Seed default branch, vehicles, and drivers on first run.
        Ensures the system has usable data immediately without manual setup.
        """
        # Default branch
        branch = Branch(
            branch_id = "BRANCH-001",
            name      = "Hanoi Central Branch",
            address   = "123 Tran Duy Hung, Hanoi, Vietnam",
            region    = "North",
            phone     = "024-3456-7890"
        )
        self._branches["BRANCH-001"] = branch

        # Default vehicles
        vehicles = [
            Vehicle("VEH-001", "51A-12345", "SMALL",   1000.0,  "BRANCH-001"),
            Vehicle("VEH-002", "51A-67890", "MEDIUM",  5000.0,  "BRANCH-001"),
            Vehicle("VEH-003", "51B-11111", "LARGE",   15000.0, "BRANCH-001"),
        ]
        for v in vehicles:
            self._vehicles[v.vehicle_id] = v

        # Default drivers
        drivers = [
            Driver("DRV-001", "Nguyen Van An",  "B2-123456", "2028-12-31", "0901234567", "BRANCH-001"),
            Driver("DRV-002", "Tran Thi Bich",  "B2-654321", "2027-06-30", "0907654321", "BRANCH-001"),
            Driver("DRV-003", "Le Van Cuong",   "C-789012",  "2029-03-31", "0903456789", "BRANCH-001"),
        ]
        for d in drivers:
            self._drivers[d.driver_id] = d

        self.save()

    # -----------------------------------------------------------------------
    # Vehicle management
    # -----------------------------------------------------------------------
    def add_vehicle(
        self,
        registration : str,
        vehicle_type : str,
        capacity_kg  : float,
        branch_id    : str
    ) -> tuple:
        """
        Add a new vehicle to the fleet.

        Args:
            registration (str)  : Vehicle registration / plate number.
            vehicle_type (str)  : SMALL, MEDIUM, or LARGE.
            capacity_kg  (float): Maximum cargo weight in kg.
            branch_id    (str)  : Branch this vehicle belongs to.

        Returns:
            tuple: (success: bool, message: str, vehicle: Vehicle or None)
        """
        # Validate inputs
        if not registration.strip():
            return False, "Registration cannot be empty.", None

        if vehicle_type.upper() not in ("SMALL", "MEDIUM", "LARGE"):
            return False, "Vehicle type must be SMALL, MEDIUM, or LARGE.", None

        if capacity_kg <= 0:
            return False, "Capacity must be greater than 0 kg.", None

        # Check registration uniqueness
        reg_upper = registration.strip().upper()
        if any(v.registration == reg_upper for v in self._vehicles.values()):
            return False, f"Vehicle '{registration}' already exists.", None

        vehicle_id = self._id_gen.next_vehicle_id(self._vehicles)
        vehicle = Vehicle(
            vehicle_id   = vehicle_id,
            registration = reg_upper,
            vehicle_type = vehicle_type.upper(),
            capacity_kg  = capacity_kg,
            branch_id    = branch_id
        )
        self._vehicles[vehicle_id] = vehicle
        self.save()
        return True, f"Vehicle {vehicle_id} ({reg_upper}) added successfully.", vehicle

    def update_vehicle_status(
        self,
        vehicle_id       : str,
        new_status       : str,
        maintenance_note : str = ""
    ) -> tuple:
        """
        Update a vehicle's operational status.

        Args:
            vehicle_id       (str): The vehicle to update.
            new_status       (str): AVAILABLE or MAINTENANCE.
            maintenance_note (str): Reason for maintenance (if applicable).

        Returns:
            tuple: (success: bool, message: str)
        """
        vehicle = self._vehicles.get(vehicle_id)
        if not vehicle:
            return False, f"Vehicle {vehicle_id} not found."

        if new_status.upper() not in (VEH_AVAILABLE, VEH_MAINTENANCE):
            return False, "Status must be AVAILABLE or MAINTENANCE."

        if vehicle.status == VEH_ASSIGNED:
            return False, f"Cannot update {vehicle_id} — it is currently assigned to a shipment."

        vehicle.status           = new_status.upper()
        vehicle.maintenance_note = maintenance_note
        self.save()
        return True, f"Vehicle {vehicle_id} status updated to {new_status}."

    def remove_vehicle(self, vehicle_id: str) -> tuple:
        """
        Remove (decommission) a vehicle from the fleet.

        Args:
            vehicle_id (str): The vehicle to remove.

        Returns:
            tuple: (success: bool, message: str)
        """
        if vehicle_id not in self._vehicles:
            return False, f"Vehicle {vehicle_id} not found."

        if self._vehicles[vehicle_id].status == VEH_ASSIGNED:
            return False, "Cannot remove a vehicle that is currently assigned."

        del self._vehicles[vehicle_id]
        self.save()
        return True, f"Vehicle {vehicle_id} removed from the fleet."

    # -----------------------------------------------------------------------
    # Driver management
    # -----------------------------------------------------------------------
    def add_driver(
        self,
        full_name      : str,
        licence_number : str,
        licence_expiry : str,
        phone          : str,
        branch_id      : str
    ) -> tuple:
        """
        Add a new driver to the fleet.

        Args:
            full_name      (str): Driver's full name.
            licence_number (str): Driver's licence number.
            licence_expiry (str): Licence expiry date (YYYY-MM-DD).
            phone          (str): Driver's contact phone number.
            branch_id      (str): Branch this driver belongs to.

        Returns:
            tuple: (success: bool, message: str, driver: Driver or None)
        """
        if not full_name.strip():
            return False, "Driver name cannot be empty.", None
        if not licence_number.strip():
            return False, "Licence number cannot be empty.", None
        if not phone.strip():
            return False, "Phone number cannot be empty.", None

        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(licence_expiry, "%Y-%m-%d")
        except ValueError:
            return False, "Licence expiry must be in YYYY-MM-DD format.", None

        # Check licence uniqueness
        if any(d.licence_number == licence_number.strip()
               for d in self._drivers.values()):
            return False, f"Licence '{licence_number}' already registered.", None

        driver_id = self._id_gen.next_driver_id(self._drivers)
        driver = Driver(
            driver_id      = driver_id,
            full_name      = full_name.strip(),
            licence_number = licence_number.strip(),
            licence_expiry = licence_expiry,
            phone          = phone.strip(),
            branch_id      = branch_id
        )
        self._drivers[driver_id] = driver
        self.save()
        return True, f"Driver {driver_id} ({full_name}) added successfully.", driver

    def update_driver_status(
        self,
        driver_id  : str,
        new_status : str,
        leave_note : str = ""
    ) -> tuple:
        """
        Update a driver's operational status.

        Args:
            driver_id  (str): The driver to update.
            new_status (str): AVAILABLE or ON_LEAVE.
            leave_note (str): Reason for leave (if applicable).

        Returns:
            tuple: (success: bool, message: str)
        """
        driver = self._drivers.get(driver_id)
        if not driver:
            return False, f"Driver {driver_id} not found."

        if new_status.upper() not in (DRV_AVAILABLE, DRV_ON_LEAVE):
            return False, "Status must be AVAILABLE or ON_LEAVE."

        if driver.status == DRV_ASSIGNED:
            return False, f"Cannot update {driver_id} — currently assigned to a shipment."

        driver.status     = new_status.upper()
        driver.leave_note = leave_note
        self.save()
        return True, f"Driver {driver_id} status updated to {new_status}."

    def remove_driver(self, driver_id: str) -> tuple:
        """
        Remove (deactivate) a driver from the fleet.

        Args:
            driver_id (str): The driver to remove.

        Returns:
            tuple: (success: bool, message: str)
        """
        if driver_id not in self._drivers:
            return False, f"Driver {driver_id} not found."

        if self._drivers[driver_id].status == DRV_ASSIGNED:
            return False, "Cannot remove a driver that is currently assigned."

        del self._drivers[driver_id]
        self.save()
        return True, f"Driver {driver_id} removed from the fleet."

    # -----------------------------------------------------------------------
    # Availability checks
    # -----------------------------------------------------------------------
    def get_available_vehicles(self, cargo_weight_kg: float = 0) -> list:
        """
        Return available vehicles that can carry the given cargo weight.

        Excludes vehicles that are ASSIGNED or MAINTENANCE.
        Validates that vehicle capacity is sufficient for the cargo.

        Args:
            cargo_weight_kg (float): Required cargo weight (0 = any weight).

        Returns:
            list: Available Vehicle objects sorted by capacity.
        """
        available = [
            v for v in self._vehicles.values()
            if v.status == VEH_AVAILABLE and v.capacity_kg >= cargo_weight_kg
        ]
        return sorted(available, key=lambda v: v.capacity_kg)

    def get_available_drivers(self) -> list:
        """
        Return available drivers with valid (non-expired) licences.

        Excludes drivers that are ASSIGNED or ON_LEAVE.
        Also excludes drivers with expired licences.

        Returns:
            list: Available Driver objects sorted by name.
        """
        available = [
            d for d in self._drivers.values()
            if d.status == DRV_AVAILABLE and d.is_licence_valid()
        ]
        return sorted(available, key=lambda d: d.full_name)

    # -----------------------------------------------------------------------
    # Assignment helpers (called by OrderManager)
    # -----------------------------------------------------------------------
    def assign_vehicle(self, vehicle_id: str) -> tuple:
        """
        Mark a vehicle as ASSIGNED.
        Called by OrderManager when an order is confirmed.

        Args:
            vehicle_id (str): The vehicle to assign.

        Returns:
            tuple: (success: bool, message: str)
        """
        vehicle = self._vehicles.get(vehicle_id)
        if not vehicle:
            return False, f"Vehicle {vehicle_id} not found."
        if vehicle.status != VEH_AVAILABLE:
            return False, f"Vehicle {vehicle_id} is not available ({vehicle.status})."

        vehicle.status = VEH_ASSIGNED
        self.save()
        return True, f"Vehicle {vehicle_id} assigned."

    def assign_driver(self, driver_id: str) -> tuple:
        """
        Mark a driver as ASSIGNED.
        Called by OrderManager when an order is confirmed.

        Args:
            driver_id (str): The driver to assign.

        Returns:
            tuple: (success: bool, message: str)
        """
        driver = self._drivers.get(driver_id)
        if not driver:
            return False, f"Driver {driver_id} not found."
        if driver.status != DRV_AVAILABLE:
            return False, f"Driver {driver_id} is not available ({driver.status})."

        driver.status = DRV_ASSIGNED
        self.save()
        return True, f"Driver {driver_id} assigned."

    def release_vehicle(self, vehicle_id: str) -> None:
        """
        Release a vehicle back to AVAILABLE.
        Called when an order is cancelled or completed.

        Args:
            vehicle_id (str): The vehicle to release.
        """
        vehicle = self._vehicles.get(vehicle_id)
        if vehicle and vehicle.status == VEH_ASSIGNED:
            vehicle.status = VEH_AVAILABLE
            self.save()

    def release_driver(self, driver_id: str) -> None:
        """
        Release a driver back to AVAILABLE.
        Called when an order is cancelled or completed.

        Args:
            driver_id (str): The driver to release.
        """
        driver = self._drivers.get(driver_id)
        if driver and driver.status == DRV_ASSIGNED:
            driver.status = DRV_AVAILABLE
            self.save()

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------
    def get_vehicle(self, vehicle_id: str):
        """Return a Vehicle by ID or None."""
        return self._vehicles.get(vehicle_id)

    def get_driver(self, driver_id: str):
        """Return a Driver by ID or None."""
        return self._drivers.get(driver_id)

    def get_all_vehicles(self) -> list:
        """Return all vehicles sorted by ID."""
        return sorted(self._vehicles.values(), key=lambda v: v.vehicle_id)

    def get_all_drivers(self) -> list:
        """Return all drivers sorted by name."""
        return sorted(self._drivers.values(), key=lambda d: d.full_name)

    def get_all_branches(self) -> list:
        """Return all branches."""
        return list(self._branches.values())

    def get_default_branch_id(self) -> str:
        """Return the first available branch ID."""
        if self._branches:
            return list(self._branches.keys())[0]
        return "BRANCH-001"

    def get_fleet_summary(self) -> dict:
        """
        Return a summary of fleet statistics.

        Returns:
            dict: Counts of vehicles and drivers by status.
        """
        return {
            "total_vehicles"      : len(self._vehicles),
            "available_vehicles"  : sum(1 for v in self._vehicles.values() if v.status == VEH_AVAILABLE),
            "assigned_vehicles"   : sum(1 for v in self._vehicles.values() if v.status == VEH_ASSIGNED),
            "maintenance_vehicles": sum(1 for v in self._vehicles.values() if v.status == VEH_MAINTENANCE),
            "total_drivers"       : len(self._drivers),
            "available_drivers"   : sum(1 for d in self._drivers.values() if d.status == DRV_AVAILABLE),
            "assigned_drivers"    : sum(1 for d in self._drivers.values() if d.status == DRV_ASSIGNED),
            "on_leave_drivers"    : sum(1 for d in self._drivers.values() if d.status == DRV_ON_LEAVE),
        }

    def __repr__(self) -> str:
        return (
            f"FleetManager("
            f"vehicles={len(self._vehicles)}, "
            f"drivers={len(self._drivers)})"
        )